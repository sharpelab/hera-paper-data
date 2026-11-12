# Device card — RPL_19

*Per-device card for Aaron's RPL_19 rhombohedral-graphene device. Lives in the
measurement directory alongside the working notebook; not committed to the
measurement-env repo. This copy reflects the 2025-11-03 cooldown (the one this
fixture captures). Built from the notebook's Init/Configs/Gate-checks cells +
the RPL19 notebook index synopsis.*

## Identity
- **Device id**: `RPL_19`
- **Material**: **rhombohedral tetralayer (4-layer)** graphene (confirmed by
  Aaron, 2026-06-05) + hBN encapsulation, on a silicon back gate. Hosts a
  superconducting (SC) dome and anomalous-Hall (AH) physics in later cooldowns.
  (Note: the "RPL" series prefix is not a literal layer count — RPL_19 is 4-layer;
  do not infer other RPL devices' layer counts from it.)
- **Active user**: aaron
- **Status**: mature cooldown (2025-11-03) — SC dome under characterization.

## Gate stack
- **Top hBN thickness** (`t_tg`): 16 nm (top gate, Keithley2400 `k_tg`,
  `GPIB4::9`).
- **Bottom hBN thickness** (`t_bg`): 25.5 nm (back gate, Keithley2400 `k_bg`,
  `GPIB4::10`).
- **Si back gate**: **yes** — degenerate Si, driven by Keithley2400 `k_si`
  (`GPIB4::11`); held at **V_Si = −48 V** through the SC work this cooldown.
- **hBN dielectric constant** (`ep`): 3.
- **Single device or dual**: single.

## Validators (current cooldown)
*Set by the gate-check section this cooldown (top-gate and back-gate
responsiveness sweeps, cells 50–62). Gate currents stay ~1e−11–1e−10 A across
the maps (no leakage). The SC work sits in a narrow window around the dome.*

- `k_tg.volt`: swept up to ~+1 V in checks; SC dome work at TG ≈ 0.41–0.53 V.
- `k_bg.volt`: swept −7 → −3 V in the gate map; SC dome at BG ≈ −5.4 → −5.0 V.
- `k_si.volt`: −48 V (fixed this cooldown).
- Validators are removed/relaxed in setup (`*.volt.remove_validator()`); respect
  the ranges the gate checks actually exercised.

## Gate-coupling notes
- Top hBN (16 nm) is thinner than bottom hBN (25.5 nm) — top-gate motion changes
  the state more strongly than an equal back-gate step.
- Approximate `n ∝ Vtg/dtg + Vbg/dbg`; `D ∝ Vtg/dtg − Vbg/dbg`.
- The SC dome is mapped along a line in (Vbg, Vtg) built by
  `draw_line_through_point(point=(-5.2, 0.47), slope=0.3, ...)` — i.e. the dome
  optimum sits near (BG = −5.2, TG = 0.47) at V_Si = −48 V.

## Measurement setup (rig instruments wired this cooldown)
Physical setup state for this device/run — what knobs and readouts exist,
independent of what's been measured yet. (Cooldown-invariant rig state for the
toploader; gate ranges drift between cooldowns — see Validators.)

- **Gates**: `k_tg`, `k_bg`, `k_si` (top / back / silicon), all Keithley2400
  voltage sources; ranges per Validators. `n`/`D` from (Vtg, Vbg).
- **DC bias**: SRS DC205 sources (`dc205_0`, `dc205_1` = `dc205`, `dc205_3`) are
  wired; `dc205_1.volt` is the DC-bias knob used at the dome. A Yokogawa GS200
  (`y200`) is also present as a bias/voltage source. **DC205 bias calibration
  (Aaron, confirmed 2026-06-05): 1 V → 10 nA** — a 100 MΩ bias resistor on the
  DC205 line, so the DC-bias axis is `dc205.volt × 10 = I_dc (nA)` (his Fraunhofer
  ana confirms: `xs = data['xs']*10  # bias in nA`). The AC current bias is
  delivered through the lock-in drive amplitude.
- **Lock-ins**: up to 9× SR830 (`sr830_1..9`) plus SR860 capability; channel →
  contact-pair wiring per the Contact map below. This cooldown's SC config (MC4)
  reads current on `sr830_4` (gain −1e6) and longitudinal voltage on `sr830_3`
  and `sr830_5`. AC excitation set via `sr830_1.amplitude` (~0.5–1 nA at 7.78 Hz).
- **Temperature / thermometry**: base T read via the fridge logfile (`T` column,
  ~45–60 mK base this run; colder, 27–41 mK, reachable with patience). A
  Keithley2400 `heater` (`GPIB4::12`) is wired for temperature-dependence work.
- **Magnet**: an **AMI430 superconducting magnet** (`mag`, perpendicular field,
  set in **Tesla**) is wired and available as a measurement knob, alongside a
  **Yokogawa 7651** (`yoko_mag`) that can also drive field. The magnet has been
  used this cooldown for ramps and small-field line-cuts (tens of mT); it is a
  live knob for field-dependent experiments. **The perpendicular null is set by
  trapped flux (Aaron, 2026-06-05): it is cooldown-dependent and *shifts* after
  sweeping to large field and back to zero** — so it is a moving, field-history-
  dependent offset, not a fixed instrument zero. (Observed ~+7 mT in this
  cooldown's Fraunhofer.) Define any field axis relative to the *current* true
  null, and re-find it after large-field excursions.
- **Rotator**: no in-situ angle rotator is configured in this cooldown's setup
  (field is taken as out-of-plane / perpendicular).

## Known operating points
- **SC dome optimum**: (TG ≈ 0.47 V, BG ≈ −5.2 V) at V_Si = −48 V, base T. This
  is the point the SC-gatemap section converged on (the `draw_line_through_point`
  center).

## Contact map
*From the notebook's `mc_*` config definitions (cell 49). Source/drain and probe
wiring shift between configs.*

- **MC4** (the SC-characterization config this section): current `sr830_4 =
  I_{6-22}` (gain −1e6); voltage `sr830_3 = 25-24`, `sr830_5 = 13-14`; other
  channels n.c.
- MC3 (used for the gate map): `sr830_4 = I_{30-15}`, voltages on 29-28 / 28-25 /
  25-24, etc.
- Earlier configs (MC1/MC2) source on 30-29 / drain region around 6-22; see the
  cell-49 `mc_*` dicts for the full wiring per config.

## Recipe applicability for device-init
- `gate-current-sanity-check`: applies.
- `top-gate-sweep-check` / `back-gate-sweep-check`: applies; respect the cooldown
  validators.
- `gate-leakage-survey`: applies if checks hint at trouble (leakage is small this
  cooldown).
- `silicon-backgate-survey`: applies (Si BG present; held at −48 V here).

## Notes
- This is the 2025-11-03 cooldown of a long-running device — later cooldowns
  (Dec 2025, Jan/Feb 2026) add Hall measurements, effective-mass and
  quantum-oscillation work, and AH physics. For this fixture, treat the campaign
  as **SC dome characterization**.
- `measurebot` alerts (Slack/Discord/email) are wired at the top of the notebook.
