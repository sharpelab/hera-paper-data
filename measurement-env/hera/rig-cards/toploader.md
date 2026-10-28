# Rig card — toploader

*Rig-level machine facts for the Sharpe Lab toploader cryostat.
Canonical copy: `hera/rig-cards/toploader.md` in the `measurement-env`
repo; deployed as `rig_card.md` next to `device_card.md` in the
measurement directory. Errors or gaps found in-session go to
`session_notes.md`, not this file — agents are read-only on the repo.*

## Identity
- **Rig**: toploader — closed-cycle dilution-refrigerator cryostat with
  a top-loading probe; sample base ≈ **30 mK** (probe MC). Which insert is
  loaded is per-cooldown → device card.
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
  `temperature_from_logfiles` params over
  `TOPLOADER.temp_logfile_candidates` — `temperature` (probe MC),
  `fridge_temperature` (fridge MC), `mag_temperature` (magnet) —
  `fp()`-able as recorded channels. Reads lag by up to the worker
  cadence (probe ~55 s, fridge/magnet ~210 s).
- **Sample heater**: a Keithley 2400 wired as the sample-stage heater
  (`heater`, GPIB4::12), **open-loop voltage drive** — set
  `heater.volt`, settle, and read T back from the logfile params; there
  is no closed control loop. The V→T relation is per-cooldown — device
  card. Ramp **up** in ≤1 V steps with a mandatory equilibration hold
  after each — ~15 min/1 V baseline, confirm T has settled (stable to
  within ~1%) before measuring; the open-loop settle grows with heater
  level and runs longer above ~4 V. Ramp **down** without holds — the
  equilibration is ascent-only; the voltage stepping itself is what
  protects the dilution circuit, and `volt.step` pacing provides it.
  (Aaron, 2026-07-20.) Ceiling is per-cooldown (fridge/probe state) —
  device card; ≈6 V typical. Accessible sample T tops out ≈0.5 K.
  (Aaron, 2026-08-02.)
- **Sensors**: RuO₂ resistance thermometers (3K / Still / Magnet /
  50 mK / probe MC-low) plus a Pt1000 on MC-high; per-channel
  polynomial cal curves in `src/workers/avs_calibration.py`, the probe
  MC-low (sample) curve per-probe. Absolute-cal provenance is
  uncharacterized; field error from RuO₂ magnetoresistance is
  negligible (Aaron, 2026-08-02).
- Room temp/humidity: Thorlabs TSP01B worker (Influx
  `thorlabs_thermo`).

## Silent preconditions

Per the prompt's "preflight the silent preconditions" working-style
bullet — state sweeps depend on but never set, with the cheap read for
each. (Instance names per the toploader template's setup cells.)

| Hazard | One-line read | Expected at rest | Why silent |
|---|---|---|---|
| Probe temperature | `temperature()` (logfile param) | base, mK range | every sweep assumes T; the read can be ~1 min stale (worker cadence) |
| Magnet field | `magnet.field()` | wherever the last ramp ended — read, never assume 0 | gate sweeps inherit B from prior cells |
| Workers alive | launcher health panel (or Influx freshness) | all green | a dead worker's T reads keep returning the last value — one non-fatal warning, then quiet |

## Sweep stack & data layout

The `sweep` package (measureme submodule) is the single source of truth for the
station/sweep call surface (including `sweep.raster` for polygon-bounded maps),
the on-disk run format, and the metadata schema: `docs/api/measureme.md`. Rig
specifics:

- **Setup**: `sweep.set_basedir('./data')`, then each measurement cell builds
  its own `sweep.AsyncStation(measurement_config)`.
- **`measurement_config`** is a plain dict (channel→contact, gains, bias) — see
  the measure template's `meas-config` slot.

## Timing rules of thumb

Defaults — calibrate against runs in the current measurement dir before
pricing anything long, and cite the calibrating run.

- **Per-point**: ~1.2 s/pt typical for swept axes. `nplci` changes
  per-point cost materially (nplci=10 ≈
  167 ms/pt readback on the gate-current channels, per
  `gate-current-sanity-check`).
- **Gate ramps** are rate-limited by the Keithleys' `volt.step`
  (template default 5 mV/step).
- **Field- and heater-axis settles** dominate long 2D runs and are
  mandatory. Post-ramp settle scales with the ramp just taken — a few
  seconds after small field steps, longer after 100s of mT–T (Aaron,
  2026-08-02). Campaign discipline (magnet thermal recovery,
  sample-heater equilibration) is priced from the device card / brief,
  not from a rig default.

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
  — its `ramp_voltage`/`smart_voltage` path is a fixed-duration ramp
  (~1 s regardless of ΔV) plus a mandatory 10 s settle when ΔV > 0.1 V.
  The **direct `.volt` set** (SCPI voltage, qcodes-substepped by `volt.step`)
  carries **no 10 s settle** — so a `s.sweep(dc205_1.volt, …)` bias sweep isn't
  a ~1 h run; it substeps at `volt.step`, not the 10 s ramp settle.
  **Not** the VTI's rate-based driver of the same name. **Output range ±15 V** (SRS DC205 hardware; Isaac
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
- **The magnet has two masters**: the Influx magnet worker polls the
  AMI430 every 30 s alongside the kernel's connection. Contention is
  not characterized — if kernel magnet reads misbehave, check the
  worker first (single-poller fix is in the eng-backlog).
