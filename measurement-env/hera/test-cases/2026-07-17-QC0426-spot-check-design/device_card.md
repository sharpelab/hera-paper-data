# Device card — QC0426 (trilayer graphene)

*Session device card for QC0426 on the **VTI** cryostat. Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth**: what is wired, the hardware, the outer safety box,
the provided gate operating limits, and the provided contact
configuration. The CNP location and (n, D) calibration are established
in-session (see the session brief).*

## Identity
- **Device id**: `QC0426`
- **Material**: trilayer graphene (`3LGr`).
- **Owner**: qingrui
- **Fridge**: VTI (variable-temperature insert). Base (sample)
  temperature ≈ 1.2–1.3 K.
- **Status**: cold, wired — hardwired breakout, no contact mux; no CNP
  location on record.

## Gate stack
- **Top gate** (`k_tg`): hBN dielectric. **Driven by a Keithley 2400**
  (`k_2400_tg`) — sweeps use `k_tg.volt` (5 mV step pacing; the measure
  notebook's setup cells bind `k_tg`).
- **Back gate** (`k_bg`): graphite on hBN, driven by the second
  **Keithley 2400** (`k_2400_bg`).
- **Si global back gate** (`k_si`): doped-Si gate through **SiO₂**,
  driven by the **SRS DC205** — bound directly to the driver's ramped
  parameter **`dc205.smart_voltage`** (set ramps at `ramp_rate = 0.5`
  V/s, get reads back `VOLT?`; data column **`dc205_smart_voltage`**).
  The DC205 has **no current readback** — gate-leakage monitoring lives
  on the Keithley `curr` channels (TG/BG) only. `ramp_voltage` steps
  span/50: a full ±50 V traverse moves in ~1 V steps, paced by
  `ramp_rate`. The graphite back gate screens Si from the channel — Si
  couples only to the contacts (contact-doping gate). Operating limit
  provided (below).
- **Gate-stack geometry** (fabrication facts; **geometry prior only** —
  the capacitance *calibration* is the session's to establish via
  `cnp-and-dline-calibration`):
  ```python
  from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages
  c_tg = stack_capacitance([(15.6, 3)])           # 15.6 nm hBN
  c_bg = stack_capacitance([(12, 3), (0, 3.9)])   # 12 nm hBN, no SiO2 term
  ```
  Treat anything derived from these (lever arms, n/D scales, CNP-line
  slope) as uncalibrated until the session's own gate map confirms it.

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `k_tg.volt` | **[−3.0, +3.0] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−4.5, +4.5] V** | provided |
| `dc205.smart_voltage` / `dc205.voltage` (Si) | **[−50, +50] V** | provided; DC205 must be on its ±100 V range (RNGE 2) |
| **B field (session cap)** | **\|B\| ≤ 8.0 T** | committed on the `magnet.field` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |
| **T setpoint (session cap)** | **`set_both` target ≤ 50 K** | provided; committed as a SAFETIES setpoint typo-guard cap. `ratio = 0.95` per the rig card — deviations consent-gated |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **k_2400_tg** (GPIB0::24), back via **k_2400_bg**
  (GPIB0::1), hardwired to their sources.
- **Si gate**: **DC205** (`dc205.smart_voltage`, ASRL7, ±100 V
  range), hardwired to its source.
- **AC excitation / lock-ins**: SR830 family (`sr0…sr3` live).
  Current-bias drive: **0.5 V through a 100 MΩ bias resistor**, lock-in
  frequency **≈ 13 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`**
  (Ithaco preamp gain). Per-channel sensitivities are recorded per run in
  `measurement_config`.
- **Lock-in time constant**: 0.3 s, 24 dB/oct, all channels (`sr0`–`sr3`).
  Minimum dwell 4·τ = 1.2 s/pt.
- **Sensitivity by signal scale** (starting points — tune in-session):
  CNP / gate-map (kΩ) ~2e-5 on the voltage channels; high-|n| metallic
  (tens of Ω) `sr1` 2e-6, `sr2` 5e-7, `sr3` 5e-6, `sr0` 1e-2.
- **Bias current** (starting points — tune in-session): 0.5 V / 5 nA
  through the 100 MΩ default; high-|n| metallic regime ~2 V / 20 nA.
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages.
  `sr3` is the Hall channel (`r_xy`).
- **Contacts — hardwired, no mux this cooldown**: device pads bond to
  two Fischer cables and land on the breakout; instrument leads connect
  directly there. Contact roles are **fixed** — rerouting a pair is
  operator work at the breakout, not software.
  - **Contact map**:

    Bonded pads (label = position, T = top arc L→R, B = left side then
    bottom L→R). Only the provided configuration below is wired to
    instruments this cooldown:

    | Label | Pad | | Label | Pad |
    |---|---|---|---|---|
    | T1 | F2-05 | | B1 | F2-37 |
    | T2 | F1-33 | | B2 | F2-21 |
    | T3 | F1-09 | | B3 | F1-28 |
    | T4 | F1-01 | | B4 | F1-12 |
    | T5 | F1-42 | | B5 | F1-20 |
    | T6 | F1-02 | | B6 | F1-44 |
    | T7 | F1-43 | | B7 | F1-03 |
    | | | | B8 | F1-35 |

    Alive: T2, T3, T4, T5, B3, B4, B5, B6, B7. Dead: T1, T6, T7, B1, B8 (B2 high-R). Liveness on the provided configuration is
    re-confirmed at Gate C.
- **Provided contact configuration** (hardwired):

  | role | label |
  |---|---|
  | source | T2 |
  | drain (`sr0`) | B7 |
  | `sr1` (Rxx) | T3–T4 |
  | `sr2` (Rxx) | B4–B5 |
  | `sr3` (Rxy, Hall) | T5–B6 |

## Notes

none

## (n, D) calibration — session 2026-07-17 (cnp-and-dline-calibration, run 4)

Source: run 4 (0 T gatemap, 101×101 full validator box, TG fast vs V_bg rows;
this session's `20260717_ana.ipynb` cells 13–16).

| quantity | value | provenance |
|---|---|---|
| CNP slope dV_tg/dV_bg | −1.2829 (sr1, 49/101 rows, 20.1 mV resid) / −1.2897 (sr2, 46/101 rows, 19.4 mV resid) | data (run 4) |
| c_bg/c_tg | **1.2863** (channels agree 0.5%; geometry prior 1.300, −1.1%) | **data-calibrated** |
| C_TG | 1.7027e−3 F/m² (15.6 nm hBN anchor) | **geometry prior** — pending QH lever-arm upgrade |
| C_BG | 2.1903e−3 F/m² (= C_TG × ratio) | ratio data / scale prior |
| N_OFFSET | −0.0523 ×10¹² cm⁻² (V_tg intercept +0.0492 V at V_bg = 0) | data (run 4) |
| D_OFFSET | 0 — R_CNP(V_bg) minimum at V_bg ≈ 0.00/+0.09 V (D ≈ 0.005 V/nm) | data (run 4, cited feature) |
| closure | max \|n\| residual along ridge ≈ 0 | ✓ |

Upgrade path: absolute scale pending quantum-Hall lever-arm check — fan ray
slopes must quantize (dn/dB = ν·e/h); non-integer Δν spacing ⇒ recalibrate
before any ν claim. R_CNP strongly D-tunable (min 1.3/0.6 kΩ at D=0, >10×
rise by |V_bg| ~ 2 V, both channels/signs) — hint only, fed to the
per-channel stacking read.
