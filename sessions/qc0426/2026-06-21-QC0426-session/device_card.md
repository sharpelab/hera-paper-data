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
- **Status**: cold, wired; no CNP location on record.

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

## Gate operating limits — gate B contract

Gate operating limits for the session:

| Parameter | Operating limit | Notes |
|---|---|---|
| `dc205_volt` / `k_tg` | **[−6.0, +7.0] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−4.5, +4.5] V** | provided |
| `k_2410.volt` (Si) | **[−50, +50] V** | provided |
| **B field (session cap)** | **\|B\| ≤ 8.0 T** | committed on the `magnet.field` validator (SAFETIES); driver `max_field_T = 14.0` T is the hard backstop |

## Measurement setup (rig instruments wired this cooldown)
- **Gates**: top via **DC205** (`DC_bias`), back via **k_bg** Keithley,
  Si via **k_2410** Keithley.
- **AC excitation / lock-ins**: SR830 family (`sr0…sr3` live).
  Current-bias drive: **0.5 V through a 100 MΩ bias resistor**, lock-in
  frequency **≈ 13 Hz**.
- **Current channel**: **`sr0`** = drain current, **`sr0_gain = −1E6`**
  (Ithaco preamp gain). Per-channel sensitivities are recorded per run in
  `measurement_config`.
- **Lock-in time constant**: 0.3 s, 24 dB/oct, all channels (`sr0`–`sr3`).
  Minimum dwell 4·τ = 1.2 s/pt.
- **Sensitivity by signal scale**: CNP / gate-map (kΩ) ~2e-5 on the voltage
  channels; high-|n| metallic (tens of Ω) `sr1` 2e-6, `sr2` 5e-7, `sr3` 5e-6,
  `sr0` 1e-2.
- **Bias current**: 0.5 V / 5 nA through the 100 MΩ default; high-|n| metallic
  regime ~2 V / 20 nA.
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

## (n, D) calibration — established in-session (2026-06-21, Run 0)

From the 0 T TG–BG gate map (`data/0`, `gatemap`; V_si = 0; 0.5 V/5 nA;
provided contacts), per `cnp-and-dline-calibration`. Fit axis: ridge V_tg
(fast, `DC_bias`) vs V_bg (slow, `k_2400`).

- **CNP line:** `V_tg = −1.306·V_bg + 0.225` V.
- **Per-channel fits** (ridge = Rxx-max argmax, smoothed; 24/25 rows kept, 1 corner clipped):
  - sr1 (T3–T4): slope −1.3063 (±0.0075), intercept +0.2250, rms 89 mV.
  - sr2 (B4–B5): slope −1.3045 (±0.0086), intercept +0.1986, rms 102 mV.
  - Channels agree to 0.2% → one calibration for the device.
- **Capacitance ratio (data-calibrated):** `c_bg/c_tg = 1.306` — matches
  geometry prior (15.6/12 = 1.300) to 0.5%.
- **Capacitances:** `c_tg = 1.7027e-3 F/m²` (geometry prior, anchor),
  `c_bg = 2.2243e-3 F/m²` (= ratio · c_tg). **Absolute scale = geometry
  prior** — n/D magnitudes carry the prior's ~10–15% scale uncertainty
  until a quantum-Hall lever-arm check upgrades it (dn/dB = ν·e/h).
- **Offsets:** `n_offset = −2.391e15 m⁻²` (CNP → n = 0); `D_offset = 0`
  (unexamined assumption — no feature located D = 0 yet). CNP at
  (V_tg = +0.225 V, V_bg = 0) → marginally hole-doped at the origin.
- **Closure:** rms |n| along ridge ≈ 1.0e15 m⁻² (~0.1e12 cm⁻²; coarse-map
  ridge-extraction scatter, 213 mV TG step).
- **D = 0 line:** `V_tg = 1.306·V_bg`; accessible |n| along D = 0 is
  gate-limited to ≈ ±12e12 cm⁻² (FS-count forward model valid to
  |n| ≈ 3.5e12). `GateCalibration(c_tg=1.7027e-3, c_bg=2.2243e-3,
  n_offset=-2.391e15, D_offset=0.0)`.
- **Leakage during the map:** |I_bg|max 244 pA, |I_si|max 587 pA (Si
  offset-level, held at 0 V); both ≪ 1 nA. Run complete (not interrupted).
- **Upgrade path:** absolute scale pending QH lever-arm; re-fit ratio from
  SdH if it disagrees.
