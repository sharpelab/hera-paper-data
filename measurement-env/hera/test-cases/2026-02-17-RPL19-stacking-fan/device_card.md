# Device card — RPL_19 (tetralayer graphene)

*Per-device card for RPL_19 on the **toploader** cryostat, 2026-02-17 cooldown.
Deployed into the measurement directory alongside the working notebooks. Carries
physical truth: what is wired, the hardware, the gate operating limits, and the
contact configuration. The CNP location and (n, D) calibration were established
in device-init and are committed below.*

## Identity
- **Device id**: `RPL_19`
- **Material**: tetralayer graphene (`4LGr`), hBN-encapsulated, dual graphite
  gates over a silicon contact-doping gate. Layer count from optical contrast +
  Raman; **stacking order not assigned** (the question this campaign answers).
  (The "RPL" series prefix is not a literal layer count.)
- **Owner**: aaron
- **Fridge**: toploader. Base (sample) temperature ≈ 30 mK this cooldown.
- **Status**: mature cooldown, dual-gated (n, D) work.

## Gate stack
- **Top gate** (`k_tg`, Keithley2400): top hBN ~16 nm.
- **Back gate** (`k_bg`, Keithley2400): bottom hBN ~25.5 nm.
- **Silicon back gate** (`k_si`, Keithley2400): global Si gate held at
  **V_Si = +48 V** through the science sections of this cooldown (contact
  doping; graphite screens Si from the channel).
- **Acquisition lever lengths** (used throughout data acquisition): `dtg =
  17.25 nm`, `dbg = 25.5 nm`, `ep = 3`. Gate → (n, D) via
  `sharpelab_nb.gates.calculate_n_D(vtg, vbg, dtg=17.25, dbg=25.5, ep=3)`;
  target (n, D) → gate volts via `calculate_gate_voltages(...)`. `n` in
  ~10¹² cm⁻²; `D` in V/nm. (These effective lever lengths, not the nominal hBN
  thicknesses, are what the (n, D) conversion uses this cooldown.)

## (n, D) calibration — ESTABLISHED (device-init, committed)
Ratio DATA-calibrated; absolute n/D **scale geometry-prior (~10–15%)** until a
quantum-Hall lever-arm check (dn/dB = ν e/h) upgrades it — do not quote absolute
n at ratio precision.

- **Lever arms**: `dtg = 17.25`, `dbg = 25.5`, `ep = 3` (above).
- **Accessible (n, D) window** at V_Si = 48 V: roughly `n ∈ [0, 1.5]`,
  `D ∈ [−0.7, +1.05]` V/nm.
- The CNP and D = 0 line are located; `n`, `D` computed directly from
  `calculate_n_D` on the gate columns of each sweep.

## Gate operating limits (this cooldown)

| Parameter | Operating limit |
|---|---|
| `k_tg.volt` | **(−6.5, +6.5) V** |
| `k_bg.volt` | **(−8.5, +7.0) V** |
| `k_si.volt` | **(−50, +50) V** |
| `heater.volt` | **(0, 12) V** |
| **B field** | AMI430 magnet, swept in this campaign to several T |

## Measurement setup (instruments wired this cooldown)
- **Gates**: `k_tg`, `k_bg`, `k_si` (top / back / silicon), each a Keithley2400
  in voltage-source mode (5 mV ramp steps); ranges per the operating limits.
  (n, D) ↔ (Vtg, Vbg) via `calculate_gate_voltages(..., dtg=17.25, dbg=25.5)`.
- **AC excitation / lock-ins**: a stack of SR830 lock-ins (`sr830_1..7`, GPIB)
  plus two SR860s (`sr830_8`, `sr830_9`). AC current-bias drive set on
  `sr830_1.amplitude` through a large bias resistor (fixed AC current bias).
  Active config this run: **`sr830_4` is the current channel** (`I_{30-21}`,
  transimpedance gain −1×10⁶); Rxx per voltage pair is
  `sr830_{pair}_X / sr830_4_X`. The longitudinal Rxx pairs are `sr830_1`
  (`29-28`), `sr830_2` (`28-25`), `sr830_3` (`25-24`); the Hall Rᵧₓ pairs are
  `sr830_5` (`28-10`), `sr830_6` (`25-11`). **No single canonical Rxx channel —
  all of `sr830_1/2/3` are valid longitudinal pairs; read each separately.**
- **DC bias**: `dc205_3` / `dc205_1` (SRS DC205) wired for DC-bias spectroscopy;
  held at 0 in the field work here. Calibration: 1 V → 10 nA (100 MΩ bias
  resistor).
- **Temperature / heater**: a Keithley2400 `heater` (`GPIB4::12`, 0–12 V) drives
  the sample heater for T-dependent work; base sample temperature ≈ 30 mK read
  via `temperature()` / `fridge_temperature()` from the fridge logfiles.
- **Magnet**: **AMI430 superconducting magnet** (`mag`) — perpendicular field,
  set in Tesla — the primary field knob. A Yokogawa GS200 (`yoko_mag`, coil
  const 0.116783 T/A, ≈ ±23 mT) is also wired for small-range low-noise work.
  **Perpendicular null is set by trapped flux: cooldown- and field-history-
  dependent, shifts after large-field excursions** (~+7 mT observed a prior
  cooldown) — define field axes relative to the current true null.
- **Rotator**: toploader sample-angle rotator present; perpendicular field is
  the working axis here.

## Notes
- `dtg=17.25, dbg=25.5` are the lever lengths in `calculate_gate_voltages` for
  this device — not the ~16 nm nominal top-hBN thickness.
- Heavy use of `multisweep` / `multimegasweep` (simultaneous (Vtg, Vbg) ramping
  along an (n, D) line, optionally with field on a slow axis) — the idiom for
  fixed-D / fixed-n cuts and Landau fans.
- `add_comment` discipline is partial; trust the cell code + `metadata.json`
  (`function`, `slow_param`/`fast_param`, `slow_setpoints`) over any standing
  comment string.

## Recipe applicability
- `investigations/tetralayer-stacking-fs-count.md` governs (material line =
  `4LGr`).
