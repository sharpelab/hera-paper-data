# Device card — vti-01 (trilayer graphene)

*Session device card for vti-01 on the **VTI** cryostat. Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth**: what is wired, the hardware, the outer safety box,
the provided gate operating limits, and the provided contact
configuration. The CNP location and (n, D) calibration are established
in-session (see the session brief).*

## Identity
- **Device id**: `vti-01`
- **Material**: trilayer graphene (`3LGr`).
- **Owner**: Jordan
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
  c_tg = stack_capacitance([(14.9, 3)])           # 14.9 nm hBN
  c_bg = stack_capacitance([(21.4, 3), (0, 3.9)])   # 21.4 nm hBN, no SiO2 term
  ```
  Treat anything derived from these (lever arms, n/D scales, CNP-line
  slope) as uncalibrated until the session's own gate map confirms it.

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `k_tg.volt` | **[−0.8, +0.8] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−5.0, +5.0] V** | provided |
| `dc205.smart_voltage` / `dc205.voltage` (Si) | **[−20, +20] V** | provided; DC205 must be on its ±100 V range (RNGE 2) |
| **B field (session cap)** | **\|B\| ≤ 10.0 T** | committed on the `magnet.field` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |
| **T setpoint (session cap)** | **`set_both` target ≤ 100 K** | provided; committed as a SAFETIES setpoint typo-guard cap. `ratio = 0.95` per the rig card — deviations consent-gated |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **k_2400_tg** (GPIB0::1), back via **k_2400_bg**
  (GPIB0::24), hardwired to their sources.
- **Si gate**: **DC205** (`dc205.smart_voltage`, ASRL7, ±100 V
  range), hardwired to its source.
- **AC excitation / lock-ins**: SR830 family (`sr0` GPIB0::22, `sr1` GPIB0::14, `sr2` GPIB0::19, `sr3` GPIB0::18).
  Current-bias drive through a **10 MOhm** bias resistor, lock-in
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

    Hall bar. `T_SD` and `B_SD` are source and drain at the top and bottom
    of the bar; `L_1`–`L_4` are voltage probes down the left side, `R_1`–`R_2`
    the right. Only the provided configuration below is wired to instruments
    this cooldown:

    | Label | Pad | | Label | Pad |
    |---|---|---|---|---|
    | T_SD | 5 | | L_1 | 29 |
    | L_2 | 13 | | L_3 | 45 |
    | L_4 | 4,12 | | B_SD | 20,44 |
    | R_1 | 1 | | R_2 | 11,27 |

    Alive: T_SD, L_1, L_2, L_3, L_4, B_SD. Dead: R_1, R_2. Liveness on the provided configuration is
    re-confirmed at Gate C.
- **Provided contact configuration** (hardwired):

  | role | label |
  |---|---|
  | source | T_SD |
  | drain (`sr0`) | B_SD |
  | `sr1` (Rxx) | B_SD–L4 |
  | `sr2` (Rxx) | L4–L1 |
  | `sr3` (Rxx) | L3–L2 |

## Notes

none

## Gate calibration — cnp-and-dline-calibration (2026-08-19, run 7)

Written back per the recipe's step 5. Source: run 7 (first 0 T gatemap,
TG ±0.8 × BG ±2.5 V, V_si = 0). Axis orientation: ridge position is V_tg
(fast) fitted against V_bg (rows) — c_bg/c_tg = −slope.

- Per-channel fits (slope, intercept, rms, rows kept): sr1 (−0.7236, +0.0552 V,
  4.3 mV, 20/51); sr3 (−0.7207, +0.0515 V, 3.5 mV, 17/51); sr2 (−0.7223,
  +0.0139 V, 3.5 mV, 20/51 — weak short pair, reported not driving).
  sr1/sr3 spread 0.4% → one calibration.
- **Chosen conversion (two-tier provenance)**: c_tg = 1.7827e−3 F/m²
  (**anchor — geometry prior**, 14.9 nm hBN κ=3); c_bg = 1.2874e−3 F/m²
  (**ratio data-calibrated**: c_bg/c_tg = 0.7222; geometry prior 0.6963, +3.7%).
  n_offset = −5.934e14 m⁻² (−0.0593×10¹² cm⁻²); D_offset = 0 (stated
  assumption — no ±D-symmetric locator yet). Closure residual ≈ 0.
- **Absolute scale pending quantum-Hall lever-arm check** — when field data
  exists, ray slopes must quantize (dn/dB = ν·e/h); recalibrate before any ν claim.
- **D = 0 line (realized, clip-by-dropping at validators)**: n ∈ [−1.837, +1.720]
  ×10¹² cm⁻²; V_tg spans ±0.8 (binding), V_bg only ±1.11 V.
- Session operating facts behind it: drive 100 mV at 13.777 Hz (T_SD contact
  ~109 MΩ sets I ≈ 1 nA; normalize Rxx by sr0 current per point); Si inert,
  parked 0 V. CNP peak R grows with |D| along the ridge (~25 kΩ at V_bg = −1).
- **D_offset update (2026-08-19, runs 7-9 analysis)**: R_CNP along the CNP ridge
  has a clean symmetric minimum on sr1 and sr3 at nominal D = −0.009 V/nm →
  **D_offset = +0.009 V/nm** (feature-cited per the recipe; supersedes the
  stated D_offset = 0 assumption). Magnitude is small; runs 8–9 ("D=0" spot
  checks) sat at |D_true| < 0.01 V/nm.

## End-state block — session 2026-08-18/20 (close-out: return-to-initial)

- Field 0.0026 T (parked ~0); gates V_tg ~0, V_bg 0, V_si 0; heaters off;
  T recooling to base. Acquisition restored to bring-up capture (drive 4 mV
  @ 13.777 Hz; sens/tau per state0 — see session_notes handoff record).
  Nothing deliberately held. PS heater on / output enabled (untouched).
- Session results carried on this card: gate calibration section above
  (ratio 0.7222, n_offset, D_offset +0.009 V/nm); TG leak accepted by
  operator (turn-on ~|0.4-0.5| V, ~0.5 nA at +/-0.8 V); T_SD source contact
  ~109 MOhm ohmic blocker (Si-inert) — campaign ran at 100 mV drive with
  per-point sr0 current normalization.
- Science call (ana notebook, cell 33): sr1 region ABA/Bernal (strong);
  sr3 consistent-with; sr2 uninformative; ML pocket unresolved (hedged).
- **End-state amendment (2026-08-20 evening, post-extension)**: runs 19-20
  (tau=300ms quality fan + ML descent) added; final state re-parked to the
  bring-up capture — drive 4 mV, B 0.006 T, gates/Si 0, heaters off, T base.
  Science update: ML pocket resolved; call upgraded to ABA (strong, two-branch),
  Luttinger scale lambda = 1.14 (QH lever-arm check pending) — ana cells 34-38.
