# Device card — RPL_19

*Per-device card for Aaron's RPL_19 rhombohedral-graphene device, 2026-02-17
cooldown (toploader cryostat). Lives in the measurement directory; not committed
to the measurement-env repo.*

## Identity
- **Device id**: `RPL_19`
- **Material**: rhombohedral **tetralayer** (4-layer) graphene — Aaron's SC /
  anomalous-Hall (AH) device family (Aaron-confirmed 2026-06-05; the `RPL` series
  prefix is not "pentalayer" here). The campaign studies a superconducting (SC)
  dome and an anomalous-Hall / chiral-SC region as a function of carrier density
  `n` and displacement field `D`.
- **Active user**: aaron
- **Status**: established device, many prior cooldowns (Oct 2025 → Feb 2026). This
  cooldown follows a power-loss event — see "Checks after power loss" in the
  notebook (gate sweeps run first to confirm the device survived).

## Gate stack
- **Top hBN** (`k_tg`): ~16 nm. *(Validator-era comment in cell 16 reads
  "Top hBN: 16 nm"; the (n, D) conversion in the map-building cells uses
  `dtg = 17.25` nm — a refined effective thickness from capacitance fitting.
  Aaron, 2026-06-06: both are approximate calibrations; for highest accuracy
  the lever arm should be checked via quantum oscillations. The lever lengths
  are device-specific, not cooldown-dependent.)*
- **Bottom hBN** (`k_bg`): ~25.5 nm (`dbg = 25.5` in the gate→(n,D) helper).
- **Silicon back gate** (`k_si`): YES — a doped-Si global back gate is present and
  driven (`k_si`, typically held at +48 V this cooldown to set the band filling
  / screening). This is a three-gate device (top, back, Si), unlike the b1c2 chip.
- **hBN dielectric constant** (`ep`): 3.
- **(n, D) convention**: `n ∝ Vtg/dtg + Vbg/dbg`, `D ∝ Vtg/dtg − Vbg/dbg`, via the
  `calculate_gate_voltages(n, D, dtg=17.25, dbg=25.5)` / `calculate_n_D(...)`
  helpers in the "Custom functions" cell. `n` is quoted in units of 1e12 cm⁻²,
  `D` in V/nm in this notebook.

## Validators (this cooldown)
Set in the Init cell (`from qcodes import validators`):

- `k_tg.volt`: **(-6.5, +6.5) V**
- `k_bg.volt`: **(-8.5, +7) V**
- `k_si.volt`: **(-50, +50) V**
- `heater.volt`: **(0, 12) V**

## Measurement setup (rig instruments wired this cooldown)
Physical setup state for this device/run — what knobs and readouts exist,
independent of what's been measured yet. (Cooldown-invariant for the toploader
rig; gate *ranges* drift between cooldowns — see Validators.)

- **Gates**: `k_tg` (top), `k_bg` (back), `k_si` (silicon global back gate),
  driven by Keithley 2400 sourcemeters. `n`/`D` computed from (Vtg, Vbg) via the
  Custom-functions helpers; `k_si` sets overall filling/screening.
- **AC excitation / lock-ins**: 8× SR830 + 1× SR860 (`sr830_1 … sr830_9`;
  `sr830_8` is the SR860, added this cooldown). One channel carries current
  (the `I_{src-drain}` entry in the active `mc_*` config, gain `-1E6`); the
  others read four-terminal voltages (gain `100`). AC drive is set on
  `sr830_1.amplitude` (the source lock-in's reference output), excitation
  frequency ~7.8 Hz. Per-channel `sr830_*.sensitivity` is tuned to the signal
  level and is part of map quality (coarse maps run at coarser sensitivity).
- **DC bias**: SRS DC205 sources are wired (`dc205_1`; `bias_voltage` = a second
  DC205) for DC-bias / Idc spectroscopy. **Bias calibration (Aaron-confirmed
  2026-06-05):** `dc205.volt = 1 V → 10 nA` through a 100 MΩ bias resistor, i.e.
  `I_dc (nA) = dc205.volt × 10`. Not exercised in the nD-map sections.
- **Magnet**: a superconducting magnet is wired and available as an out-of-plane
  (perpendicular) **field** knob, set in **Tesla**. Two paths exist: an AMI430
  controller (`mag`) and a Yokogawa-GS200-driven coil (`yoko_mag`, coil constant
  ≈ 0.1168 T/A). Field is a real measurement axis this campaign (the device has
  SC and AH features whose field response is of interest); the nD-map sections
  sit at nominally zero field. **The perpendicular null is trapped flux, not a
  fixed instrument offset (Aaron-confirmed 2026-06-05):** it is cooldown- and
  field-history-dependent and **moves after large-field excursions**, so "zero
  field" means "the current trapped-flux null" and must be re-found after big
  field sweeps — never read an absolute B from a nominal-zero point.
- **Temperature / thermometry**: probe + fridge mixing-chamber temperatures read
  from the toploader log files (`temperature` ≈ probe, `fridge_temperature`,
  `mag_temperature`); base T ≈ 28–30 mK. A Keithley-2400 `heater` is wired for
  T-dependence (validator 0–12 V).
- **Rotator**: not referenced in this notebook's setup; assume the field is the
  fixed-axis perpendicular field unless an expert says otherwise.

## Active measurement config at this point
- `mc_31` is the config in use for the positive-D nD mapping: current channel
  `sr830_4 = I_{30-21}`; voltage channels `sr830_1 = 29-28`, `sr830_2 = 28-25`,
  `sr830_3 = 25-24`; `sr830_5…9 = n.c.` `k_si` held at +48 V.
- The notebook defines configs `mc_1 … mc_32` (a long history of contact-pair
  rewirings across cooldowns). Only a few channels are live in `mc_31`.

## Known operating points / features (from this device's history)
- A **superconducting (SC) dome** and a related **CSC / anomalous-Hall (AHC)**
  region live at **positive D ≈ +1 V/nm** at low density (`n` of order a few
  ×10¹¹ to ~1×10¹² cm⁻²). Prior cooldowns mapped the SC dome, ran Fraunhofer /
  Ic-vs-B, effective-mass and Landau-fan measurements, and hysteresis scans
  across flavor transitions. The positive-D, low-n corner is the scientifically
  interesting region this device keeps returning to.

## Notes / caveats
- **Device-card drift**: this card summarizes the current cooldown; some thickness
  numbers (16 vs 17.25 nm top hBN) differ between the validator comment and the
  (n,D) helper. Aaron (2026-06-06) confirms both are approximate calibrations —
  resolve via quantum oscillations for the accurate lever arm; the lever lengths
  themselves are device-specific, not cooldown-dependent. Don't over-index on the
  exact `dtg`.
- The active-config contact map (`mc_31`) is the wiring *for this map*; earlier
  `mc_*` entries are stale wirings from prior sessions.
