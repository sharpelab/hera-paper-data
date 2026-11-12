# Device card — RPL_19

*Per-device card for Aaron's RPL_19 rhombohedral-graphene device. Lives in the
measurement directory; not committed to the measurement-env repo. Captured for
the 2026-01-24 cooldown of the toploader cryostat.*

## Identity
- **Device id**: `RPL_19`
- **Material**: **rhombohedral tetralayer (4-layer)** graphene (confirmed by
  Aaron, 2026-06-05), hBN-encapsulated, on a silicon back gate. This is one of
  Aaron's RPL-series SC / anomalous-Hall (AHC) devices. The campaign treats it as
  hosting a superconducting (SC) dome plus an anomalous-Hall / chiral-SC ("CSC")
  feature in the (n, D) phase diagram. (Note: the "RPL" series prefix is not a
  literal layer count — RPL_19 is 4-layer; do not infer other RPL devices' layer
  counts from it.)
- **Active user**: aaron
- **Status**: mature cooldown, deep into Phase-2 exploration (AH spot checks,
  effective-mass and quantum-oscillation work).

## Gate stack
- **Top gate** (`k_tg`, Keithley2400): top hBN ~**16 nm**.
- **Back gate** (`k_bg`, Keithley2400): bottom hBN ~**25.5 nm**.
- **Silicon back gate** (`k_si`, Keithley2400): global Si gate, held at
  **V_Si = +48 V** through the science sections of this cooldown (sets the
  band alignment / screening regime).
- `n` and `D` are computed from (Vtg, Vbg) via `calculate_gate_voltages(n, D,
  dtg=17.25, dbg=25.5)` (note `dtg=17.25` here, **not** the 16/25.5 nominal hBN
  thicknesses — these are the *effective* gate-lever lengths Aaron uses for the
  (n, D) conversion this cooldown). Densities `n` are quoted in units of
  ~10¹² cm⁻² (campaign convention: "n = 1" ≈ a dome operating point); `D` in
  V/nm.

## Validators (this cooldown)
Set live in the Init block:
- `k_tg.volt`: **(-6.5, +6.5) V**
- `k_bg.volt`: **(-8.5, +7) V**
- `k_si.volt`: **(-50, +50) V**
- `heater.volt`: **(0, 12) V**

## Measurement setup (instruments wired this cooldown)
Physical rig state — what knobs and readouts exist, independent of what has been
measured. Cooldown-invariant rig context for the toploader.

- **Gates**: `k_tg`, `k_bg`, `k_si` (top / back / silicon), each a Keithley2400
  in voltage-source mode with 5 mV ramp steps; ranges per Validators. Physical
  (n, D) ↔ (Vtg, Vbg) via `calculate_gate_voltages(..., dtg=17.25, dbg=25.5)`.
- **AC excitation / lock-ins**: a stack of SR830 lock-ins (`sr830_1..7`,
  GPIB) plus two SR860s (`sr830_8`, `sr830_9`). The AC current-bias drive is set
  on `sr830_1.amplitude` (driven through a large bias resistor → a fixed AC
  current bias). The active config this run: `sr830_4` is the **current** channel
  (`I_{30-21}`, transimpedance gain −1×10⁶). In Aaron's own analysis the voltage
  channels split into **longitudinal Rxx** — `sr830_1` (`29-28`), `sr830_2`
  (`28-25`), `sr830_3` (`25-24`) (his `long1`) — and **Hall Rᵧₓ** — `sr830_5`
  (`28-10`), `sr830_6` (`25-11`) (his `realhall`). **There is no single canonical
  Rxx channel (Aaron, 2026-06-05): all of `sr830_1/2/3` are valid longitudinal
  pairs** — do not pick one as authoritative. Other configs (`mc_1`…`mc_27`)
  define alternate contact wirings (e.g. `mc_26` moves the current contact and
  adds Hall pairs). (Note: Aaron's ana cells are commented "Incorrectly labeled
  MC_25" — the `mc_25` label in the sweeps is suspect; trust the contact strings
  in `mc_0` / `metadata.json`, not the config number.)
- **DC bias**: `bias_voltage` = `dc205_3` (SRS DC205), held at 0 in the
  field/temperature work here; a second `dc205_1` is also wired for DC-bias
  spectroscopy. **DC205 bias calibration (Aaron, confirmed 2026-06-05):
  1 V → 10 nA** — a 100 MΩ bias resistor on the DC205 line, so the DC-bias axis
  is `dc205.volt × 10 = I_dc (nA)`.
- **Temperature / heater**: a Keithley2400 **`heater`** (`GPIB4::12`) drives the
  sample heater (0–12 V) for temperature-dependent work; base mixing-chamber
  temperature read via `temperature()` / `fridge_temperature()` from the fridge
  logfiles (~29–32 mK at base). A magnet-temperature readout `T` is also logged.
- **Magnet**: an **AMI430 superconducting magnet** (`mag`) — perpendicular field,
  **set in Tesla** — is wired and is the primary field knob (it has been swept to
  ±1.5 T and beyond in this campaign). A **Yokogawa GS200** (`yoko_mag`, coil
  constant 0.116783 T/A, ≈ ±23 mT range) and a Yokogawa-7651-style source are
  *also* wired as an alternate low-noise field source for small-range work. Both
  are available as field knobs. **The perpendicular null is set by trapped flux
  (Aaron, 2026-06-05): it is cooldown- and field-history-dependent and *shifts*
  after sweeping to large field and back to zero** — a moving offset, not a fixed
  instrument zero (observed ~+7 mT in the 2025-11-03 cooldown's Fraunhofer).
  Define any field axis relative to the *current* true null, and re-find it after
  large-field excursions.
- **Rotator**: the toploader sample-angle rotator is present (sets the in/out-of-
  plane field projection); the perpendicular field is the working axis here.

## Known operating points (this campaign)
- **Main SC / dome point**: ~(n ≈ 0.465, D ≈ 1.000) — the AH-spot-check anchor.
- **Effective-mass anchor**: (n = 1, D = 1) — where the temperature-dependent
  field sweeps are run.
- **CSC / chiral-SC region**: lower density, D ≈ 1 (n ≈ 0.5–0.75) and a
  negative-D counterpart at D ≈ −0.7.
- The accessible window is roughly n ∈ [0, 1.5], D ∈ [−0.7, +1.05] at V_Si = 48 V.

## Notes
- `dtg=17.25, dbg=25.5` are the lever lengths in `calculate_gate_voltages` for
  this device — do not confuse with the 16 nm nominal top-hBN thickness.
- Heavy use of `multisweep` / `multimegasweep` (simultaneous (Vtg,Vbg) ramping
  along an (n, D) line, optionally with field on a slow axis) — Aaron's idiom for
  fixed-D / fixed-n cuts and Landau fans.
- Cell `add_comment` discipline is partial; many sweeps carry only the standing
  `'MC6, Vsi = 48V, gate map in -100 mT'` annotation, which is **stale boilerplate
  copied between cells** and does *not* reliably describe the actual sweep —
  trust the cell code + `metadata.json` (`function`, `slow_param`/`fast_param`,
  `slow_setpoints`) over the comment string.
