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
- **Status**: cold, wired; CNP + (n,D) calibration established 20260619 (below).

## Stacking — ABC (rhombohedral), strong (20260619, FS-count)
SdH Fermi-surface counting at D=0 (`trilayer-stacking-fs-count`): a **single SdH tone
tracking F_L=(h/4e)n** across density (F/F_L = 1.07±0.09 sr2, 1.04±0.04 sr1; |n|=4.3–6.5e12,
hole, Landau fan `data/7`) in **both** Rxx channels → one Fermi surface carrying the full
density → **ABC**. No ML+BL pair (an ABA BL tone would sit below F_L with a resolved ML
partner). **Confirmed both signs**: electron side n=+5e12 (`data/8`) also shows a single tone
at F_L (47–50 T vs F_L 52 T, SNR 8–11, both channels). Independent support: D-induced CNP gap
(CNP-R rises with |D|). Strength **strong**, not decisive — hedges: Onsager model overlay
unavailable at the operating density (model clamped >3.5e12); a very small ABA ML partner
(≲5–10 T) not strictly excludable; LK-mass + ABC-LL-Streda firming pending. Step-7 verdict: ana 11–12.
**ABC = flat-band/correlated candidate → warrants a low-T (mK) campaign.**

## Gate stack (three gates)
- **Top gate** (`k_tg`): hBN dielectric. **Driven by the SRS DC205** —
  in the data it appears as the column **`DC_bias`** (the
  DC205 voltage), and in sweep calls as `dc205_volt` (a
  `qcodes.Parameter` wrapping `k_tg.ramp_voltage`, `ramp_rate = 2`; the
  measure notebook's setup cells define it).
- **Back gate** (`k_bg`): thick graphite on hBN, driven by a **Keithley
  2400**.
- **Si global back gate** (`k_si` / `k_2410`): doped-Si gate through
  **SiO₂**, driven by a second Keithley (`k_2410`). The graphite back gate
  screens Si from the channel — Si couples only to the contacts
  (contact-doping gate). Operating limit provided (below).
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

## (n, D) calibration — established 20260619, run 1 (`cnp-and-dline-calibration`)

Source: `data/1`, 0 T TG–BG gatemap (37 BG-slow × 131 TG-fast), slug `gatemap`.
Axis orientation: ridge position = V_tg (fast) fitted vs V_bg (slow rows), so the
fitted slope = dV_tg/dV_bg = −c_bg/c_tg.

| Channel | CNP line (V) | c_bg/c_tg | rows used |
|---|---|---|---|
| sr1 T3–T4 | V_tg = −1.2906·V_bg + 0.057 | 1.2906 | 34/37 |
| sr2 B4–B5 | V_tg = −1.2900·V_bg + 0.099 | 1.2900 | 34/37 |
| **pooled (device)** | **V_tg = −1.2903·V_bg + 0.078** | **1.2903** | 68 pts |

- **Ratio data-calibrated** (channels agree 0.05%; geometry prior 1.300 confirmed to
  0.7%). **Absolute n,D scale = geometry prior**: anchor `c_tg` on 15.6 nm hBN (κ=3) →
  `c_tg = 1.702e-3 F/m²`, `c_bg = ratio·c_tg = 2.196e-3 F/m²` (effective t_bg = 12.09 nm).
  Magnitudes carry ~10–15%; **upgrade path: quantum-Hall lever-arm** (ray slopes
  dn/dB = ν·e/h must quantize) — recalibrate before any ν assignment.
- **Calibration object**: `GateCalibration.from_thicknesses(15.6e-9, 12.09e-9, 0.0,`
  `n_offset=-8.28e14, D_offset=0.0)`. Closure: |n| on the fitted CNP line ≈ 0 (machine
  precision); ridge-fit residual ~60 mV.
- **D = 0 located at (V_tg, V_bg) = (0, 0)** from the CNP-R minimum (not assumed):
  CNP resistance is minimal (~1.5 kΩ) at D≈0 and rises symmetrically with |D|, clipping
  the lock-in 2e-5 ceiling (≈4.37 kΩ) at the box corners. This **D-induced gap** is
  *consistent-with* ABC/rhombohedral (supporting, not decisive — FS-counting is the call).
  CNP-R(D) magnitude at high |D| is a **lower bound** here (clipped); a higher-full-scale
  re-measure would quantify it.
- **D = 0 line designer**: `V_tg = 1.2903·V_bg` (through (0,0)). Realized window within
  validators: V_bg ∈ [−4.5, +4.5] → V_tg ∈ [−5.81, +5.81] (no clipping). **Max |n| at
  D=0**: hole −12.4e12 cm⁻² (V_bg −4.5), electron +12.3e12 cm⁻² (V_bg +4.5).
- **Channel health**: both Rxx pairs (sr1, sr2) stay metallic (tens of Ω) across the
  full n-range at D=0 — no insulating arms. sr2 is the cleaner channel at high |n|
  (tighter scatter); sr1 carries more small-signal offset.

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `dc205_volt` / `k_tg` | **[−6.0, +7.0] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−4.5, +4.5] V** | provided |
| `k_2410.volt` (Si) | **[−50, +50] V** | provided |
| **B field (session cap)** | **\|B\| ≤ 8.0 T** | committed on the `magnet.mag` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **DC205** (`DC_bias`), back via **k_bg** Keithley,
  Si via **k_2410** Keithley.
- **AC excitation / lock-ins**: SR830 family (`sr0…sr3` live).
  Current-bias drive: **0.5 V through a 100 MΩ bias resistor**, lock-in
  frequency **≈ 13 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`**
  (Ithaco preamp gain). Per-channel sensitivities are recorded per run in
  `measurement_config`.
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages.
  `sr3` is the Hall channel (`r_xy`).
- **Contact switching — QSwitch (QDevil) mux** — ContactMux live:
  - Wiring topology (final per the operator's
    routing slide): device pads bond to two Fischer cables; the
    QSwitch takes **F1 only**, and F2-riding contact pads are shorted
    onto spare F1 conductors at the breakout. **F1 fischer index =
    QSwitch line number.** TG and BG do **not** pass through the
    QSwitch (hardwired to their sources — fixed, unswitchable). Si
    passes through the QSwitch and back to the breakout box.
  - **Contact map** (label = position, T = top arc L→R, B = left side
    then bottom L→R; all switchable):

    | Label | Pad | Line | | Label | Pad | Line |
    |---|---|---|---|---|---|---|
    | T1 | F2-05 | 1 | | B1 | F2-37 | 8 |
    | T2 | F1-33 | 3 | | B2 | F2-21 | 17 |
    | T3 | F1-09 | 4 | | B3 | F1-28 | 23 |
    | T4 | F1-01 | 6 | | B4 | F1-12 | 22 |
    | T5 | F1-42 | 7 | | B5 | F1-20 | 20 |
    | T6 | F1-02 | 12 | | B6 | F1-44 | 19 |
    | T7 | F1-43 | 13 | | B7 | F1-03 | 18 |
    | | | | | B8 | F1-35 | 15 |

    Alive: T2, T3, T4, T5, B3, B4, B5, B6, B7. Dead: T1, T6, T7, B1, B8
    (B2 high-R).

  - **Gates**: TG (DC205) and BG (K2400) **hardwired — no relay can
    touch them**. **Si (K2410) rides QSwitch lines 16 and 11** with
    standing closed relays ("keep 16/11 closed inside the QSwitch" —
    routed through the switch and back to the breakout box). Lines
    16/11 are **excluded from ContactMux's managed set** (never in the
    `lines` map), and **`qsw.reset()` is always forbidden** — it opens
    the standing closures and drops the Si gate.
  - **Instrument taps (BNC 1–8)**: 1 = sr1.V1, 2 = sr1.V2, 3 = sr2.V1,
    4 = sr2.V2, 5 = sr3.V1, 6 = sr3.V2, **7 = sr1.amplitude (AC
    source)**, **8 = sr0.V1 × −1e6 (measured AC current)**. ContactMux
    form: `breakouts = {"source": 7, "drain": 8, "sr1+": 1, "sr1-": 2,
    "sr2+": 3, "sr2-": 4, "sr3+": 5, "sr3-": 6}`.
  - `settle_s` **4 s**.
- **Provided contact configuration**:

  | role | label | QSwitch line |
  |---|---|---|
  | source | T2 | 3 |
  | drain (`sr0`) | B7 | 18 |
  | `sr1` (Rxx) | T3–T4 | 4, 6 |
  | `sr2` (Rxx) | B4–B5 | 22, 20 |
  | `sr3` (Rxy, Hall) | T5–B6 | 7, 19 |

  ContactMux form: `mux.select({"source": "T2", "drain": "B7", "sr1+":
  "T3", "sr1-": "T4", "sr2+": "B4", "sr2-": "B5", "sr3+": "T5", "sr3-":
  "B6"})`.
