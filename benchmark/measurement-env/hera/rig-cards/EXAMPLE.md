# Rig card — EXAMPLE (not a real rig)

*Rig cards are per-fridge machine facts. The canonical copy of each card
lives in this repo (`hera/rig-cards/<rig>.md`); a session deploys it as
`rig_card.md` next to `device_card.md` in the measurement directory. See
`README.md` here for the layer model, the deployment loop, and what a rig
card must never carry.*

*This file is an **authoring tool** for writing a new rig card — agents
never see it. The italic notes are guidance for the author; delete them
from a real card. The rig below is fictional.*

*Norm: a finished rig card has **no `[VERIFY]` markers**. The rig is the
static layer — session-scoped uncertainty belongs on the device card. A
`[VERIFY]` here is a debt with an owner, acceptable mid-authoring, not a
steady state.*

---

## Identity
- **Rig**: `EXAMPLE` — wet variable-temperature cryostat ("the example
  fridge")
- **Control PC**: `dgg-example` (Windows 11; measurement dirs under
  `~/EX_local_data/<user>/<session>/`)
- **Base temperature**: ≈ 1.5 K this configuration
- **Status**: fictional / for reference only

## Magnet

*The session field cap is not here — that's a per-session
device-card/SAFETIES choice; this section is the machine limits it sits
inside.*

- **Supply / driver**: ACME PS-2K, `drivers.AcmePS2K` (raw TCP
  `192.168.0.99:10001`). Out-of-plane field, Tesla, via the `field`
  qcodes Parameter.
- **Coil constant**: 0.125 T/A.
- **Ramp rate**: fixed ≈ 0.125 T/min (1 A/min), hard-coded in the
  driver. 8 T → 0 takes ~64 min.
- **Set semantics**: `magnet.field(target)` **blocks** until the field is
  reached (polls the ramping flag, then a settle dwell). A cell that
  ramps is busy the whole ramp.
- **Interrupt ≠ stop**: interrupting the notebook cell does **not**
  stop the supply — it keeps ramping to the last setpoint. Recovery is
  calling `field()` again with a new target; aborting a ramp is the
  operator acting on the instrument, never a kernel interrupt.
- **Driver limit**: `max_field_T = 9.0` — driver-level only; the
  session cap (device card / SAFETIES) is what measurements obey.
- **Read-truth**: `field()`'s get returns the **measured** output current
  × coil constant (`GET:I:?`, averaged readback). The set-point is not
  readable as field; never infer field from the last set call.
- **Persistent-switch heater**: `heater_on()` / `heater_off()`, each
  blocks 10 s, **no field-matching check** — operator-only.
- **Never re-traverse**: the slow fixed ramp makes field moves the
  expensive axis. Plan sweeps to start where the magnet sits and end
  where the next measurement needs it; alternate fan directions rather
  than returning to a preferred start field.

## Thermometry & heaters

*Channel map, sensor provenance, control topology — what's closed-loop
vs hands-on-rig.*

- **Controller**: LakeShore 335. Input A = sample-mount Cernox
  (closed-loop with the sample heater); input B = vaporizer Cernox.
- **Calibration**: NIST-traceable packages in
  `hera/example/cernox-cal/` (fictional); accuracy ±6–10 mK in the
  10–30 K band, zero-field. Field-induced error is order tens of mK at
  10 K / 6 T — B is logged per point, so it's a post-hoc correction.
- **Control topology**: only the LS335 sample loop is closed-loop.
  The vaporizer / needle valve is **operator-only, hands at the rig** —
  reaching and holding elevated T is operator craft; an agent's role is
  read-only settle-and-verify.
- **Offsets**: mount→device thermal gradient is **uncharacterized**
  (heater-power dependent) — not documented in this card; treat
  absolute-T claims accordingly and ask the operator.

## Silent preconditions

*Sweeps depend on this state but never set it.*

| Hazard | One-line read | Expected at rest | Why silent |
|---|---|---|---|
| Sample temperature | `ls335.sample_temperature()` | ≈ 1.5 K (base) | every sweep assumes T; almost none set it |
| Magnet field | `magnet.field()` | wherever the last ramp ended — read, don't assume 0 | gate sweeps inherit B from the previous cell |
| Persistent-switch heater | `magnet._status()['heater']` | on (driver refuses ramps when off) | only touched at cooldown bring-up |

## Sweep stack

*The rig's call surface and any deltas from the lab-standard measureme
stack. Loader/protocol conventions live in the prompt, not here.*

- **Kernel stack**: `sweep.AsyncStation` from the sharpelab `sweep`
  package:

  ```python
  s = sweep.AsyncStation(meas_config)
  s.fp(sr0.X).fp(sr0.P)
  s.sweep(param, vec, delay=...)                  # 1D
  s.multisweep([p1, p2], [v1, v2], delay=...)     # co-swept 1D
  s.megasweep(slow, svec, fast, fvec, ...)        # 2D
  s.multimegasweep([slow], [svec], [p1, p2], [v1, v2], ...)
  s.add_comment('<recipe-slug>')
  ```

## Timing rules of thumb

*Defaults with a calibrating-run citation — calibrate per session, don't
inherit.*

- Per-point time: ~1.2 s/pt (calibrated on example run 80).
- 2D row overhead: ~30 s/B-row when the slow axis is the magnet — the
  blocking ramp between rows (example runs 84–86).
- Magnet ramp to start field: 0.125 T/min, from wherever the magnet
  sits (read it, see Silent preconditions).

## Standard equipment

*Racked inventory with default addresses; the device card fills the
(per-device) holes and wins conflicts.*

- **Lock-ins**: 4× SR830 (`sr0…sr3`), GPIB 1–4 (default). Channel
  roles, gains, and contact pairs: (per-device).
- **DC sources**: 2× Keithley 2400 (gates, default GPIB 24/25);
  SRS DC205 (serial; rate-based ramp — use `vti_drivers.SRS_DC205`,
  not the sharpelab one; they are not interchangeable).
- **Contact mux**: QDevil QSwitch via `drivers.QSwitch` +
  `drivers.contact_mux.ContactMux`. Rig-level facts: enumerates as a
  serial device at a fixed, OS-pinned COM port; the driver's IDN check
  confirms the right device; switching uses a
  ground-during-transition sequence; `settle_s` default 10 s (lock-ins
  need several time constants after a switch — calibrate per campaign
  via the buffer-trace procedure). The `lines`/`breakouts` maps are
  wiring → (per-device).

## Known quirks

*Free list, provenance-cited.*

- Console is cp1252; python unicode output mangles unless
  `PYTHONIOENCODING=utf-8` (set in `~/.bashrc`, new shells only).
- The supply's status query bundles six redundant SCPI reads — don't
  poll `status()` in a tight loop while a sweep is running.

## What this card does not carry

- **Device facts** — wiring maps, gains, validators, gate stacks,
  calibrated settle times → device card.
- **Campaign state** — goals, recipes in play, reference runs → brief.
- **Session caps** — field/T/voltage limits chosen for a session →
  device card + SAFETIES cell.
- **Conclusions** — no prior-campaign operating points, no device
  leans, no "last time X worked". Rig cards are agent-visible during
  blinded sessions, and **operational defaults are also information**.
