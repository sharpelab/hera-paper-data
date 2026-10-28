# Rig card — toploader

*Rig-level machine facts for the Sharpe Lab toploader cryostat.
Canonical copy: `hera/rig-cards/toploader.md` in the `measurement-env`
repo; deployed as `rig_card.md` next to `device_card.md` in the
measurement directory. Errors or gaps found in-session go to
`session_notes.md`, not this file — agents are read-only on the repo.*

## Identity
- **Rig**: toploader — dilution-refrigerator cryostat with a
  top-loading probe; sample base ≈ **30 mK** (probe MC, rotator probe
  loaded; zf1 cooldown 2026-04)
- **Rig owner**: Aaron
- **Control PC**: `toploader` (Windows 11); measurement dirs under
  `~/measurements/<user>/<session>/`
- **Bring-up**: the launcher GUI (`uv run measurement-env` in
  `~/measurement_env`) owns run creation (dated templates), JupyterLab
  (rooted at `~/measurements`), the hardware workers, and the
  aggregate health panel
- **Status**: in service

## Magnet

- **Controller**: AMI Model 430 (qcodes `AMIModel430`),
  `TCPIP0::192.168.0.101::7180::SOCKET`. Out-of-plane field, Tesla,
  via `magnet.field()`.
- **Coil constant**: 0.116783 T/A (`sharpelab_nb.constants.TOPLOADER`).
- **Absolute field ceiling**: **±9 T** — AMI430 hardware limit
  (Isaac, 2026-06-18); the driver raises if `|target| > COIL? ×
  current_limit`. The session cap (device card / SAFETIES) is what
  measurements obey.
- **Read-truth**: `magnet.field()` returns the **measured** readback;
  the set-point is not readable as field — never infer field from the
  last set call.
- **Set semantics**: `magnet.field(target)` **blocks** until the supply
  reports holding (busy-polls `ramping_state`).
- **Interrupt ≠ stop**: the ramp is commanded before the blocking poll,
  so a kernel interrupt during the wait leaves the supply ramping to its
  last target — recovery is calling `magnet.field()` again.
- **Ramp rate**: instrument-configured, not a code constant — read the
  live value with `magnet.ramp_rate()` (T/s, first segment).
- **Machine field-history behavior** (independent of any device):
  - **Remanence**: any excursion to finite field leaves up to **~±10 mT**
    remanent on the return toward zero (measured, Aaron) — set by having
    gone to finite field at all, not by direction reversal; it bounds how
    well true B = 0 is known.
  - **Ramp heating**: ramping dissipates into the cold stage via
    hysteretic flux-motion loss whose per-unit-field rate ∝ **J_c(B)**,
    so it is **largest at low |B|** (worst traversing ~0) — not eddy
    currents, and not a ramp-rate-segment artifact.
  - The two are independent (heat ∝ flux *motion*; remanence = endpoint
    *state*). The sweep discipline that follows (one-sided ramps toward 0,
    mandatory post-ramp settles) is sample/campaign-scoped — see the
    device card and session brief, not here.
- The Influx `magnet` worker polls the AMI430 every 30 s alongside any
  kernel connection — see Known quirks.

## Thermometry & heaters

- **Bridges**: two AVS-47B resistance bridges, owned by launcher
  **workers** (persistent GPIB connections): fridge bridge
  `GPIB11::21` (6 channels — 3K, 50mK, Still, MixingCh low/high,
  Magnet; ~210 s full scan) and probe bridge `GPIB10::20` (probe
  mixing chamber; ~55 s). The workers write InfluxDB and
  `C:\Users\toploader\temperature_logs\*.txt`.
- **Kernel readout is file-based, never GPIB**:
  `temperature_from_logfile` params over `TOPLOADER.temp_logfiles` —
  `temperature` (probe MC), `fridge_temperature` (fridge MC),
  `mag_temperature` (magnet) — `fp()`-able as recorded channels.
  Staleness floor = worker cadence (probe ~55 s, fridge ~210 s); a
  "current" read can be minutes old.
- **Sample heater**: a Keithley 2400 wired as the sample-stage heater
  (`heater`, GPIB4::12), **open-loop voltage drive** — set
  `heater.volt`, settle, and read T back from the logfile params; there
  is no closed control loop. The V→T relation is per-cooldown — device
  card. Ramp it in ≤1 V steps, with a mandatory equilibration hold after
  each — 5 min for a full 1 V step, proportionally less for smaller steps.
- **Sensors**: RuO₂ resistance thermometers (3K / Still / Magnet /
  50 mK / probe MC-low) plus a Pt1000 on MC-high; per-channel
  polynomial cal curves in `src/workers/avs_calibration.py`, the probe
  MC-low (sample) curve per-probe. Absolute-cal provenance and
  field-error budget are uncharacterized.
- Room temp/humidity: Thorlabs TSP01B worker (Influx
  `thorlabs_thermo`).

## Safe operating envelope (T/B)

- **No T/B envelope ruling on record for this rig.** (The VTI's
  2026-06-12 envelope ruling does not transfer.) The machine field
  ceiling is ±9 T (Magnet).
- **Closed-cycle cryogen — consumption is not a session budget
  constraint.** The LC workers (FP + PT families) monitor compressor
  and pulse-tube state.

## Silent preconditions

Per the prompt's "preflight the silent preconditions" working-style
bullet — state sweeps depend on but never set, with the cheap read for
each. (Instance names per the toploader template's setup cells.)

| Hazard | One-line read | Expected at rest | Why silent |
|---|---|---|---|
| Probe temperature | `temperature()` (logfile param) | base, mK range | every sweep assumes T; the read can be ~1 min stale (worker cadence) |
| Magnet field | `magnet.field()` | wherever the last ramp ended — read, never assume 0 | gate sweeps inherit B from prior cells |
| Workers alive | launcher health panel (or Influx freshness) | all green | dead workers freeze the temperature logfiles — reads go stale silently |

## Sweep stack & data layout

- **Kernel stack**: the `sweep` package (measureme submodule) used
  directly. Setup runs `sweep.set_basedir('./data')`; each measurement
  cell builds its own station:

  ```python
  s = sweep.AsyncStation(measurement_config)
  s.add_comment('<recipe-slug>')
  s.ramp(param, target)                  # rate-limited move (volt.step)
  s.fp(temperature)                      # logfile params record like any channel
  s.fp(k_tg.volt).fp(k_tg.curr)
  s.plot(xp, k_tg.curr)                  # live Qt monitor
  s.sweep(param, vec, delay=...)         # 1D
  s.megasweep(slow, svec, fast, fvec,
              slow_delay=..., fast_delay=...)         # 2D
  s.multimegasweep([slow], [svec], [p1, p2], [v1, v2],
                   slow_delay=..., fast_delay=...)    # co-swept fast axis
  s.register_run_before(callback, args=(s,))          # e.g. leakage aborts
  ```

  `sweep.raster` is available for polygon-bounded maps;
  `measurement_config` is a plain dict (channel→contact, gains, bias) —
  see the measure template's `meas-config` slot.
- **Comments are station-lifetime, not per-run**: every `add_comment`
  since station construction appears in every subsequent run's
  metadata — rebuild the station per run; stale inherited comments are
  a known trap.

## Timing rules of thumb

Defaults — calibrate against runs in the current measurement dir before
pricing anything long, and cite the calibrating run.

- **Per-point**: ~1.2 s/pt typical for swept axes (zf1 campaign,
  2026-04). `nplci` changes per-point cost materially (nplci=10 ≈
  167 ms/pt readback on the gate-current channels, per
  `gate-current-sanity-check`).
- **Gate ramps** are rate-limited by the Keithleys' `volt.step`
  (template default 5 mV/step).
- **Field- and heater-axis settles** dominate long 2D runs and are
  mandatory — but they are sample/campaign-scoped (magnet thermal
  recovery, sample-heater equilibration). Price them from the device
  card / brief, not from a rig default.

## Standard equipment

Racked inventory with defaults; anything marked **(per-device)** is a
hole the device card fills, and the device card wins any conflict.
Default addresses live in the measure template's CONFIG cell.

- **Lock-ins**: standard rack is 8× SR830 (idx 1–7, 9) + 1× SR860
  (idx 8, TCPIP `192.168.0.107`); SR860 and idx 9 are commented out in
  the current CONFIG. Rig-standard gains: 100 on voltage channels.
  **Current channel**: one SR830 through an **Ithaco 1211**
  transimpedance preamp at gain **−1e6**; which index carries it, plus
  contact wiring and role assignments, is (per-device) — the `mc` dict +
  `contact_pairs`, device card wins.
- **Gate sources**: 3× Keithley 2400 at GPIB4::9/10/11; names and roles
  (per-device — the third Keithley varies by insert). Template defaults
  `rangev` 21 V, `rangei` 1 µA, compliance **10 nA / 20 V**, `volt.step`
  5 mV. Voltage limits: (per-device) — validators/SAFETIES. A 4th
  Keithley 2400 serves as the sample `heater` (GPIB4::12) — see
  Thermometry.
- **Other DC sources**: SRS DC205 via `sharpelab_nb.drivers.SRS_DC205`
  — fixed-duration ramp (~1 s regardless of ΔV) plus a mandatory 10 s
  settle when ΔV > 0.1 V; **not** the VTI's rate-based driver of the
  same name. **Output range ±15 V** (SRS DC205 hardware; Isaac
  2026-06-18); any series bias resistor is (per-device) wiring. Two
  units racked (`dc205_1` ASRL6, `dc205_3` ASRL7). Yokogawa GS200
  (`y200`, GPIB5::19).
- **Rotator**: ANC350 two-axis piezo (θ/φ) on the rotator-probe insert
  (`sharpelab_nb.drivers.anc350` + `lockin_servo`); angle readback on
  lock-ins 6 (θ) / 7 (φ). Bring-up, servo, and cal constants are
  per-cooldown → device card.
- **Alerts**: measurebot (Discord/Slack/email) wired into the template.
- **Workers** (launcher-managed → InfluxDB `023_toploader` at
  `metrics.aaronsharpe.science`): LC scraper (FP + PT families),
  Thorlabs TSP01B, AVS fridge/probe bridges, magnet poller.

## Known quirks

- **`autorange_sr830s` silently no-ops when |phase| < 160°** — phase
  drift during a sweep stops autoranging with zero warning.
- **SR830 X-readout can read slightly negative when true R ≈ 0**
  (X-phase imbalance / imperfect phase tune). Threshold-cross
  extraction is fine; any fit assuming R ≥ 0 breaks.
- **`temperature_from_logfile` hardcodes column −3** of the log
  format — a worker or format change breaks it silently.
- **The magnet has two masters**: the Influx magnet worker polls the
  AMI430 every 30 s alongside the kernel's connection. Contention is
  not characterized — if kernel magnet reads misbehave, check the
  worker first (single-poller fix is in the eng-backlog).
