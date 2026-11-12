# Rig card — VTI

*Rig-level machine facts for the Sharpe Lab VTI (variable-temperature
insert) cryostat. Canonical copy: `hera/rig-cards/VTI.md` in the
`measurement-env` repo; deployed as `rig_card.md` next to
`device_card.md` in the measurement directory. Errors or gaps found
in-session go to `session_notes.md`, not this file — agents are
read-only on the repo.*

## Identity
- **Rig**: VTI — wet variable-temperature insert, out-of-plane magnet
- **Rig owner**: Bingcheng (VTI czar) — adjudicates envelope and
  operating-edge questions
- **Control PC**: `dgg-vti` (Windows 11); measurement dirs under
  `~/VTI_local_data/<user>/<session>/`
- **Base temperature**: ≈ 1.2–1.3 K; electron temperature ≈ 8 K
- **Status**: in service

## Magnet

- **Supply / driver**: CAEN ELS FAST-PS 1K5, `drivers.FastBi1K5`
  (raw TCP `192.168.0.10:10001`). Out-of-plane field, Tesla, via the
  `mag` qcodes Parameter.
- **Coil constant**: `T_per_A = 1/7.3` ≈ 0.137 T/A.
- **Ramp rate**: fixed 1 A/min ≈ **0.137 T/min**, hard-coded in the
  driver and sent with every setpoint. An 8 T traverse is a ~58 min
  floor.
- **Set semantics**: `magnet.mag(target)` **blocks** until the field
  is reached (busy-polls the ramping flag, then 3 s dwell). A cell
  that ramps is busy the whole ramp.
- **Interrupt ≠ stop**: interrupting the notebook cell does **not**
  stop the supply — it keeps ramping to the last setpoint. There is no
  abort/pause/ramp-to-zero method; recovery is calling `mag()` again
  with a new target. Aborting a ramp is the operator acting on the
  instrument, never a kernel interrupt.
- **Magnet limit**: **14.0 T** (Zack ruling 2026-06-12), enforced by
  the driver (`max_field_T = 14.0`; `mag()` raises above it). The
  session cap (device card / SAFETIES, machine-enforced via
  `magnet.mag.vals`) is what measurements obey.
- **Read-truth**: `mag()`'s get returns the **measured** output
  current × `T_per_A` (`GET:I:?`, 2-stage moving-average readback,
  ~41 ms lag ≈ 0.1 mT at our slew). The set-point is not readable as
  field; never infer field from the last set call.
- **Persistent-switch heater**: `heater_on()` / `heater_off()`, each
  blocks 10 s, **no field-matching check** before toggling —
  operator-only, with care.
- **Never re-traverse**: the fixed slow ramp makes field the expensive
  axis. Plan sweeps to start where the magnet sits and end where the
  next measurement needs it; alternate fan directions across
  iterations rather than returning to a preferred start field.

## Thermometry & heaters

- **Controller**: Lakeshore 335 (`drivers.Lakeshore_335`).
  Input A = sample-mount Cernox (`sample_temperature`, `KRDG? A`);
  input B = vaporizer Cernox (`vaporizer_temperature`, `KRDG? B`).
- **Sensors**: 2× CX-1030-CU-HT-0.3M (serials X225149, X225150),
  NIST-traceable ITS-90, 0.3–420 K. Calibration packages in-repo at
  `hera/vti/cernox-cal/` (INDEX.md has the error budget). Curve
  assignments (read from NVRAM 2026-06-12): **input A = curve 23,
  serial X225149**; input B = curve 21, whose header *also* reads
  X225149 — likely X225150's data loaded under an unedited name, or a
  duplicate load of A's curve. Impact is bounded by the inter-sensor
  cal delta and B is control-only, but the anomaly is unresolved
  (Bingcheng).
- **Accuracy**: ±6–9 mK at 10–20 K, zero-field. Field-induced error:
  order tens of mK at 10 K / 6 T (CX-1030 magnetoresistance runs a
  few× the published CX-1050 table), negligible above ~30 K. B is
  logged per point, so the field term is a clean post-hoc correction.
- **Control topology**: only the LS335 **sample loop is closed-loop**
  (input A ↔ sample-mount heater). PID / heater-range settings are a
  TODO even in the lab's own VTI doc. The **vaporizer / needle valve
  is operator-only, hands at the rig** — reaching and holding elevated
  T is operator craft; an agent's role is read-only settle-and-verify.
- **Offsets**: the mount→device thermal gradient is **uncharacterized**
  (heater-power dependent). Treat absolute-T claims accordingly; LK
  fits inherit T errors linearly. Ask the operator.

## Safe operating envelope (T/B)

- **Normal working window: no T/B co-constraints.** Elevated
  temperatures and fields within the rig's ordinary operating ranges
  are operationally fine. (Provenance: Aaron, 2026-06-12, via Zack.)
- **Consideration zone**: simultaneously **above ~10 T and above
  ~15 K** (early cut — Bingcheng, 2026-06-12, via Zack). Plans
  entering it get pre-checked with Bingcheng or the operator;
  Bingcheng adjudicates the edges.
- **Cryogen economics**: **closed-loop He system — consumption is not
  a session budget constraint** (Bingcheng/Qingrui, 2026-06-12, via
  Zack). Elevated-T holds still ride the vaporizer; no hold-time cap
  is documented for this rig.

## Silent preconditions

Per the prompt's "preflight the silent preconditions" working-style
bullet — state sweeps depend on but never set, with the cheap read for
each. (LS335 instance is named `heater` in current templates.)

| Hazard | One-line read | Expected at rest | Why silent |
|---|---|---|---|
| Sample temperature | `heater.sample_temperature()` | ≈ 1.2–1.3 K at base | every sweep assumes T; almost none set it |
| Magnet field | `magnet.mag()` (measured readback) | wherever the last ramp ended — read, never assume 0 | gate sweeps inherit B from prior cells |
| Vaporizer state | `heater.vaporizer_temperature()` | tracks base unless a ladder is in progress | needle-valve setting is manual and persists across cells |
| PS heater / output | `magnet._status()` | heater on, output enabled (`mag()` raises otherwise) | touched only at bring-up |

## Sweep stack & data layout

- **Kernel stack**: the `sweep` package (measureme submodule — the
  single source of truth for sweep semantics); VTI notebooks build the
  station via `drivers.async_station`, a thin `sweep.Station` subclass
  (convergence onto sweep's own `AsyncStation` is backlogged):

  ```python
  s = async_station(meas_config)
  s.fp(sr0.X).fp(sr0.P)
  s.sweep(param, vec, delay=...)                  # 1D
  s.multisweep([p1, p2], [v1, v2], delay=...)     # co-swept 1D (e.g. a D-line)
  s.megasweep(slow, svec, fast, fvec, ...)        # 2D
  s.multimegasweep([slow], [svec], [p1, p2], [v1, v2],
                   slow_delay=..., fast_delay=...)
  s.add_comment('<recipe-slug>')
  ```

- **Comments are station-lifetime, not per-run**: every `add_comment`
  since station construction appears in every subsequent run's
  metadata. Rebuild the station (or scrub) between runs with different
  intent — stale inherited comments are a known trap.
- The basedir must exist before `async_station(...)` is constructed
  (the station writes `log.log` into it).

## Timing rules of thumb

Defaults for wall-clock arithmetic — calibrate against runs in the
current measurement dir before pricing anything long, and cite the
calibrating run.

- **Per-point**: ~1.2 s/pt for 1D sweeps; ~2.0–2.5 s/pt for 2D D=0
  multimegasweeps (2026-06-16 gatemap + fans).
- **Fan arithmetic**: wall-clock ≈ B_span / 0.137 T/min (ramp floor)
  + N_rows × (N_fast × per-point + row turnaround).
- **Row turnaround**: ~60 s/row at fine B steps (run 5, 2026-06-10:
  121 rows × 271 pts, predicted 12.3 h vs actual 13.6 h). At coarse
  steps rows are ramp-limited instead (run 3: 278 s/row at 0.25 T
  steps ≈ 110 s ramp + turnaround).
- **Measured ramps are slower than bare ramps**: a field traverse
  recorded as a sweep moves at ~0.092 T/min effective (per-point
  overhead on top of the 0.137 bare rate) — ~40% more wall-clock than
  an unrecorded ramp. Usually still worth it; price honestly.
- **Closed-loop T settles run 2–5 min** on this rig (2026-06-10/12
  ladder, ~54 min/pt dominated by sweeps) — not the 10–20 min of
  toploader lore. Don't inherit settle budgets across rigs.

## Standard equipment

Racked inventory with defaults; anything marked **(per-device)** is a
hole the device card fills, and the device card wins any conflict.

- **Lock-ins**: SR830 family, 4 in recent service (`sr0…sr3`). Channel
  roles, gains, sensitivities, contact pairs: (per-device).
  **Settling**: `time_constant` + `filter_slope` are operator-set on the
  front panel and **not set by the kit** — read them (`srN.time_constant()`,
  `srN.filter_slope()`) at bring-up and record them, so the swept-point dwell
  (`≳ k·τ`; k ≈ 5 at 6 dB/oct, 7–10 at 24 dB/oct) can be priced against a
  known τ and bent knowingly, not guessed (STYLE rule 12 settling floor). The
  run-metadata `instruments` snapshot currently stores these as `None` —
  until that's fixed, the bring-up record is the only place τ lives on disk.
- **Current preamp**: Ithaco transimpedance preamp on the drain
  channel; gain setting (per-device), recorded per run in
  `measurement_config`.
- **DC sources**: SRS DC205 (serial, 115200 baud, **ASRL7**,
  s/n 20500514) — use `drivers.SRS_DC205` (rate-based ramp,
  deterministic dV/dt); the
  `sharpelab_nb` driver of the same name has different ramp semantics
  and they are **not interchangeable**. 2× Keithley 2400 for gates.
- **Contact mux**: QDevil QSwitch (expected IDN: serial 37, firmware
  2.0) via `drivers.QSwitch` + `drivers.contact_mux.ContactMux`.
  **Max signal voltage 60 V DC** (30 Vrms / 42 Vpp AC) — QDevil's rated
  limit (`docs/manuals/qswitch/`, §3.1 + specifications table); every
  signal line routed through the switch must stay within it.
  USB-CDC serial (Microchip VID_04D8), **ASRL4**.
  Switching grounds lines during transitions; `settle_s` default 10 s.
  Per-cooldown bless status (validated address, any `settle_s` override)
  lives in the device card; `ContactMux` is live only when the device
  card says so. The `lines`/`breakouts` maps are wiring → (per-device).
- **Terranova 906A gauge**: serial, **ASRL8** — held by the
  influx-logger kernel.
- **He level**: AMI Model 1700 (`drivers.AMI_1700`),
  `192.168.0.100:7180` (s/n 1700-20-207).
- **Instrument LAN** (isolated 192.168.0/24): `.10` FastBi supply,
  `.100` AMI 1700, `.101` this PC, `.1` router.

## Known quirks

- Console is cp1252; `PYTHONIOENCODING=utf-8` is set in `~/.bashrc`
  to address unicode issues.
- **The LS335 has two masters**: a Grafana logger polls it alongside
  the measurement kernel, and VISA contention between them has killed
  a run. Do not add anything that polls the Lakeshore per-point.
- The FastBi1K5 ramp busy-poll has no sleep — the driver hammers the
  socket for the entire ramp. Don't add concurrent socket traffic to
  the supply during a ramp (eng-backlog has the throttle fix).

## What this card does not carry

- **Device facts** — wiring/contact maps, gains, gate stacks,
  validators, calibrated settle times → device card.
- **Campaign state** — goals, recipes in play, reference runs → brief.
- **Session caps** — field/T/voltage limits chosen for a session →
  device card + SAFETIES cell.
- **Conclusions** — no prior-campaign operating points, no device
  leans, no "last time X worked". This card is agent-visible during
  blinded sessions, and operational defaults are also information.
