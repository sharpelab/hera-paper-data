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
| **T setpoint (session cap)** | **`set_both` target ≤ 100 K** | provided; committed as a SAFETIES setpoint typo-guard cap. `ratio = 0.95` per the rig card — deviations consent-gated |

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

## Session calibration — 2026-07-19 (HERA, run 4)

*Written back per `cnp-and-dline-calibration` step 5. Source: run 4 (101×101
B=0 gatemap, full validator window, base T, Si = 0).*

- **Per-channel CNP fits** (ridge V_tg vs V_bg rows; smoothed argmax, edge-clipped
  rows excluded, 2σ robust fit): sr1 slope −1.2817, intercept +0.0484 V, rms 19.7 mV
  (47/101 rows); sr2 slope −1.2887, intercept +0.0543 V, rms 18.9 mV (48/101 rows).
  Cross-channel agreement 0.5% → one calibration.
- **Chosen conversion** (two-tier provenance): **ratio data-calibrated**
  c_bg/c_tg = 1.2852; **absolute scale geometry prior** — anchor c_tg = 1.7027e-3 F/m²
  (15.6 nm hBN stack prior), c_bg = 2.1884e-3 F/m². Geometry sanity: fitted ratio −1.1%
  vs prior 1.300 — pass.
- **Offsets**: n_offset = −0.0546×10¹² cm⁻² (= −5.46e14 m⁻²); D_offset = 0 (stated
  assumption, no D-locating feature examined). Quality: rms ≈ 0.02×10¹² cm⁻² in n.
- **D = 0 line**: realized window |n| ≲ 6.3×10¹² cm⁻² (TG-limited). Reference points:
  n = +6e12 cm⁻² → (V_tg, V_bg) = (+2.849, +2.216); n = −6e12 → (−2.797, −2.176).
- **Upgrade path**: absolute scale pending SdH/QH lever-arm check — ray slopes must
  quantize (dn/dB = ν·e/h); recalibrate before any ν assignment if not.
- CNP ridge peak R rises ~10× with |D| both sides (sr1 rails at its 10.9 kΩ sens
  ceiling) — domain-aware magnitude observation only, per the investigation.

## Stacking call — 2026-07-19 (HERA session, region-resolved)

Mixed-stacking mosaic: **ABA (strong)** in the B4–B5 and hole-side-probed segments
(ML+BL pair, Luttinger partition 1.000±0.06 across density, distinct LK masses
0.019/0.057); **ABC component (strong)** in the T3–T4-probed segment (F_L singleton,
no BL, LK mass 0.052–0.057 excludes breakdown). Full contract + hedges: session
`zack/20260718-QC0426`, ana cell 29; data runs 4–15.

**Revision 2026-07-19 (late):** sr1/ABC component demoted strong → consistent-with
(leakage-proof LK refit: FL mass no longer excludes a pair mixing tone — parents'
sum overlaps within ~1σ). ABA calls unaffected (masses ML 0.015–0.017 / BL
0.042–0.047, distinct). Open fork: F_L-tone origin; firming: ladder v2 (runs 16–21+)
+ Streda read. See ana cells 29–31.

**Revision 2026-07-20 (final for session):** ladder v2 (runs 16–22, X-designed top per
new guidance, multi-cosine amplitudes): ML 0.0157–0.0178, BL 0.0434–0.0446,
FL 0.0577–0.0680 — FL consistent with the parents' sum (±1.1σ) → **F_L-tone origin
is an unresolved fork** (mass favors mixing; amplitude/selectivity/B-split favor an
ABC pocket). Verdicts: ABA-dominant (strong); T3–T4 ABC candidate (weak).
Discriminator for a future session: the mass-free Streda/Chern read (Step 6).
Ana cell 29 (revised) + cells 30–33.
