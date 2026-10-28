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

## Session write-back — 2026-08-21/22 (HERA, E1)

**Calibration (cnp-and-dline-calibration, run 4):** CNP line V_tg = −0.727·V_bg + 0.040 (ridge = V_tg vs V_bg rows, rows V_bg −1.25…−0.2, rms 18 mV; ridge mildly curved — local slope −0.8 at D ≈ +0.3 to −0.65 near D ≈ +0.05). **c_bg/c_tg = 0.727 (data-calibrated)** vs 0.864 geometry prior. Anchor c_tg at the stack prior → c_bg = 2.033 × 10⁻³ F/m²; n_offset = −0.07 × 10¹² cm⁻² (design frame); D_offset = 0 (ridge-R minimum at geometric D = +0.006 V/nm). **Absolute scale: 0.93 ± 0.03 of the prior frame, pinned by the Luttinger sum (runs 5/8)** — i.e. c_tg ≈ 2.60 × 10⁻³, c_bg ≈ 1.89 × 10⁻³ F/m² in absolute terms; a QH-ray lever-arm pin was not possible on B_1–B_2 (Hall admixture α ≈ 0.2). D = 0 line realized (prior frame): n −1.11…+3.42 × 10¹², V_tg −0.30…+1.00, V_bg −0.41…+1.38.
**Device facts found:** CNP ridge gaps with D (R_xx 3 kΩ at D = +0.3 V/nm, ~230 Ω near D = 0); a V_bg-independent, Si-insensitive R_xx maximum at V_tg ≈ −0.2 V (a TG-only-gated stretch of the B_1–B_2 path) — the hole side at D ≈ 0 is geometry-limited on this pair; Si couples to the contact regions (ν = 0 resistance, high-n R) only. SdH onset 2.4 T at n ≈ 2.8 × 10¹² electrons; tones 0.21·F_L / 0.77·F_L / F_L; LK masses 0.039 / 0.048 / 0.065 (window-dependent) m_e. Stacking call (B_1–B_2): **ABAB — strong** (ana notebook final cell).
**End state (close-out, return-to-initial):** B = 0.003 T; V_tg = V_bg = 0; Si = 0 V (RNGE 2, output on); LS335 ranges off, T_sample 1.25 K; drive 1.0 V @ 13.777 Hz; sr0 20 mV / sr1 2 µV, τ 0.3 s, 24 dB/oct; NPLC 1; persistent switch on, output enabled (untouched). Nothing deliberately held.
