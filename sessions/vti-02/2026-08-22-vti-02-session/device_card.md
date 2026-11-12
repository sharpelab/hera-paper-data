# Device card — vti-02 (tetralayer graphene)

*Session device card for vti-02 on the **VTI** cryostat. Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth**: what is wired, the hardware, the outer safety box,
the provided gate operating limits, and the provided contact
configuration. The CNP location and (n, D) calibration are established
in-session (see the session brief).*

## Identity
- **Device id**: `vti-02`
- **Material**: tetralayer graphene (`4LGr`).
- **Owner**: Aaron
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
  c_tg = stack_capacitance([(9.5, 3)])           # 9.5 nm hBN
  c_bg = stack_capacitance([(11, 3), (0, 3.9)])   # 11 nm hBN, no SiO2 term
  ```
  Treat anything derived from these (lever arms, n/D scales, CNP-line
  slope) as uncalibrated until the session's own gate map confirms it.

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `k_tg.volt` | **[−0.3, +1.0] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−1.3, +2.0] V** | provided |
| `dc205.smart_voltage` / `dc205.voltage` (Si) | **[−25, +25] V** | provided; DC205 must be on its ±100 V range (RNGE 2) |
| **B field (session cap)** | **\|B\| ≤ 10.0 T** | committed on the `magnet.field` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |
| **T setpoint (session cap)** | **`set_both` target ≤ 100 K** | provided; committed as a SAFETIES setpoint typo-guard cap. `ratio = 0.95` per the rig card — deviations consent-gated |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **k_2400_tg** (GPIB0::1), back via **k_2400_bg**
  (GPIB0::24), hardwired to their sources.
- **Si gate**: **DC205** (`dc205.smart_voltage`, ASRL7, ±100 V
  range), hardwired to its source.
- **AC excitation / lock-ins**: SR830 family (`sr0` GPIB0::22, `sr1` GPIB0::14, `sr2` GPIB0::19, `sr3` GPIB0::18).
  Current-bias drive through a **100 MOhm** bias resistor, lock-in
  frequency **13.777 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`**
  (preamp gain). Per-channel sensitivities are recorded per run in
  `measurement_config`.
- **Drive / bias channel**: **`sr1`** — the lock-in whose
  oscillator provides the current-bias drive; `I_bias` = its live amplitude
  / the bias resistor. `hera-watch` reads the drive here.
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
    |  -  | -  | | T_0 | 29 |
    | B_1 | 12 | | T_1 | 41 |
    | B_2 | 04 | | T_2 | 01 |
    | B_3 | 27 | | T_3 | 42 |
    |  -  | -  | | T_4 | 43 |

    Alive: T_0, B_1, B_2, B_3. Dead: T_1, T_2, T_3, T_4. Liveness on the provided configuration is
    re-confirmed at Gate C.
- **Provided contact configuration** (hardwired):

  | role | label |
  |---|---|
  | source        | T_0 |
  | drain (`sr0`) | B_3 |
  | `sr1` (Rxx)   | B_1 - B_2 |
  | `sr2` (Rxx)   | n.c. |
  | `sr3` (Rxx)   | n.c. |

## Notes

Lock-in gains: `sr1` 1 (unity); `sr2`, `sr3` n.c.

## Session write-back — 2026-08-23 (HERA autonomous session, runs 0–14)

### (n, D) calibration (`cnp-and-dline-calibration`, run 5 gatemap)
- **Ratio (data-calibrated):** c_bg/c_tg = **0.773** (CNP ridge A, operating window |V_bg| < 0.5 V, rms 19 mV; high-D rows give 0.763). Fit axes: ridge position = V_tg (fast) vs V_bg (rows).
- **Anchor:** c_tg = 2.796×10⁻³ F/m² (9.5 nm hBN prior) → c_bg = 2.161×10⁻³ F/m².
- **Offsets:** n_offset = −0.089×10¹² cm⁻²; **D_offset = −0.013 V/nm** (physical D = 0 from the R_CNP(D) symmetry vertex).
- **Absolute scale (lever-arm, SdH grade):** true density = **0.886 ± 0.03 ×** the values from the capacitances above — pinned by three independent reads (run 6 Luttinger sum; run 7 broken-symmetry integer ladder; run 8 QH minima spacing). Quote n_true = 0.886 × n_cal.
- Realized D = 0 line inside the validators: n_cal ∈ [−1.27, +3.27]×10¹² (TG-limited both ends).
- **Second CNP ridge (region B):** parallel, electron-doped by 0.43×10¹² relative to A, weak weight — a series domain in the B_1−B_2 channel; carried as a mosaic hedge.
- CNP at D ≈ 0 is metallic (~240 Ω); the CNP gaps under displacement field (R_CNP ≈ 2.4 kΩ at |D| ≈ 0.25 V/nm, saturating) — not a stacking read on its own.

### Stacking call
**B_1−B_2 region: ABAB (Bernal), strong** — see the 20260822 ana notebook, "THE CALL" (evidence, hedges, deciding measurements). The channel's B_1−B_2 pair straddles a flake corner and carries a ρxy admixture — not a clean longitudinal pair (fine for SdH frequency work; note for quantitative ρxx).

### End state (close-out `return-to-initial`, 2026-08-23 ~15:05)
- Field 0 T (explicit endpoint); gates V_tg = V_bg = 0, V_si = 0 (DC205 output on, RNGE 2); heaters off (both ranges 0), sample cooling to base after the 30 K LK rung.
- Acquisition restored to `state0` (drive 1 V @ 13.777 Hz; sr0 20 mV/0.3 s/24 dB; sr1 2 µV/0.3 s/24 dB — **note** sr1's bring-up sensitivity is far under the kΩ-scale signals this session used 50–100 µV for; next session should re-size).
- Validators live: TG [−0.3, +1.0] V, BG [−1.3, +2.0] V, Si ±25 V, |B| ≤ 10 T, T ≤ 100 K.
