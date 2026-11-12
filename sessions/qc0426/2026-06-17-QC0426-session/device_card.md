# Device card — QC0426 (trilayer graphene)

*Session device card for QC0426 on the **VTI** cryostat. Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth**: what is wired, the hardware, the outer safety box,
the provided gate operating limits, and the provided contact
configuration. The CNP location and (n, D) calibration are established
in-session (see the session brief). This session's data ids start at 0 in
`./data/`.*

## Identity
- **Device id**: `QC0426`
- **Material**: trilayer graphene (`3LGr`).
- **Operator**: zack
- **Fridge**: VTI (variable-temperature insert). Base (sample)
  temperature ≈ 1.2–1.3 K.
- **Status**: **cold, wired, transport-uncharacterized for your
  purposes.** The device arrives as a characterizable unknown. Gate
  operating limits and a workable **contact configuration** are provided
  (below); **no CNP location** is on record — establish it via
  `cnp-and-dline-calibration`.

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

**These are the gate operating limits for the session, provided by the
operator (not range-found this cooldown).** Commit them as the gate
validators at session start; staying inside them is safe for the
device.

The SAFETIES cell in the measure notebook must commit **exactly these
numbers**; compare values, don't eyeball:

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
  (Ithaco preamp gain). **Current is `I = sr0_X / sr0_gain`** — the
  explicit gain division is mandatory. Per-channel sensitivities are
  recorded per run in `measurement_config`.
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages.
  A workable **contact configuration is provided** (below); the
  `mc_fragment` the mux writes records it per run. `sr3` is the Hall
  channel (`r_xy`).
- **Contact switching — QSwitch (QDevil) mux**: `drivers.QSwitch` +
  `drivers.contact_mux.ContactMux`. **Bring-up complete and validated**
  — ContactMux is live on this rig:
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
    the standing closures and drops the Si gate. **Si closures on lines
    16/11 confirmed closed at bring-up.**
  - **Instrument taps (BNC 1–8)**: 1 = sr1.V1, 2 = sr1.V2, 3 = sr2.V1,
    4 = sr2.V2, 5 = sr3.V1, 6 = sr3.V2, **7 = sr1.amplitude (AC
    source)**, **8 = sr0.V1 × −1e6 (measured AC current)**. ContactMux
    form: `breakouts = {"source": 7, "drain": 8, "sr1+": 1, "sr1-": 2,
    "sr2+": 3, "sr2-": 4, "sr3+": 5, "sr3-": 6}`. Worked example (the
    provided config below): source T2 ⇒ tap 7 → line 3; drain B7 ⇒
    tap 8 → line 18; sr1 T3–T4 ⇒ taps 1/2 → lines 4 and 6.
  - COM port: **ASRL4** (confirmed at bring-up — reconnected
    on ASRL4, not the expected ASRL3; Microchip VID_04D8 USB-CDC, with
    the DC205 and the logger-held Terranova gauge as the resident FTDI
    serials).
  - `settle_s` (calibrated relay settle at campaign time constant):
    **4 s**.
  - Bring-up: address **ASRL4**, `settle_s` **4 s**, Si 16/11 confirmed,
    validated.
  ContactMux is **live**. Any mux anomaly in-session is stop-and-report.
- **Provided contact configuration** (the starting measurement config; no
  contact survey needed this session):

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
- **Magnet**: **FastBi1K5** — custom Ethernet-driven magnet controller
  (192.168.0.10). Out-of-plane field in **Tesla**
  (`magnet.mag`). Treat "0 T" as the set value, not an absolute field.
  Ramp and blocking behavior are rig-level facts — see the agent
  prompt's magnet discipline section.
- **Temperature / thermometry**: LakeShore controller; VTI base
  **≈ 1.2–1.3 K**.

## Notes / caveats
- **VTI base T ≈ 1.2 K**, not mK — sets which QHE features are
  resolvable; factor it into any claim about features that are *absent*.
- **Electron temperature ≈ 8 K** (well above the 1.2–1.3 K sample base) —
  the relevant scale for thermal smearing of features.
- **Data isolation is strict this session** (per the brief): no prior
  campaign or session directories exist for you. If a comparison seems
  to need prior data, the recipes' first-session branches apply.
- This session's `data/` ids start at 0; there are no designated
  reference runs.

## Session-established calibration — 2026-06-17 (HERA, run 2 gate map)

**CNP / (n, D) calibration** from the 0 T TG–BG gate map (`data/2`), per
`cnp-and-dline-calibration`. Analysis: `20260617_ana.ipynb` cells 12–13.

- **CNP line (per channel):** sr1 (T3–T4) `V_tg = -1.305·V_bg + 0.174`;
  sr2 (B4–B5) `V_tg = -1.298·V_bg + 0.122`. Channels agree to 0.5% and match
  the geometry prior → **one device calibration** (no cap-ratio mosaic).
- **Adopted conversion:** `c_tg = 1.7027e-3 F/m²`, `c_bg = 2.2135e-3 F/m²`
  (geometry anchor, SiO₂ term zeroed). **ratio c_bg/c_tg = 1.300** (data-confirmed).
  `n_offset = -1.57e11 cm⁻²`, `D_offset = 0`.
- **Provenance (two-tier):** ratio **data-calibrated**; absolute n/D scale =
  **geometry prior**, pending a quantum-Hall lever-arm upgrade (`dn/dB = ν·e/h`)
  once fan data lands.
- **Closure:** |n| ≤ 2e11 cm⁻² along the CNP ridge.
- **D = 0 operating points (in-range):** n=+8e12 → (V_tg,V_bg)=(+3.84,+2.95);
  n=-8e12 → (-3.69,-2.84). Realized D=0 n-window ±1.24e13 cm⁻².
- **CNP R:** 0.8 kΩ (D≈0) … 85 kΩ (|D|≈1 V/nm) — D-gapped, caps below MΩ.
  CNP-R minimum at D≈+0.21 V/nm (possible small built-in D offset; D_offset kept 0).

## Stacking determination — 2026-06-17/18 (HERA): ABA (Bernal), strong

FS-count (`trilayer-stacking-fs-count`), this session's data only. **QC0426 = ABA
(Bernal)** — two coexisting Fermi surfaces (ML Dirac + BL parabolic):
- Two SdH tones partitioning F_L: **f_BL ≈ 0.85·F_L, f_ML ≈ 0.20·F_L**, seen in 4/4
  spot checks (sr1/sr2 × hole/electron, n=±8e12, D=0) and tracked across the electron
  fan (data/6). Luttinger sum f_ML+f_BL = λ·F_L, **λ = 1.06–1.08 constant across n**
  (both channels) → robust, model-independent. ABC (single tone at F_L) excluded.
- Both probed regions (T3–T4, B4–B5) agree → no stacking mosaic in the contacted area.
- Weight = **strong** (not decisive): the LK-mass split (decisive two-band + beat
  exclusion) was blocklisted; Onsager overlay unavailable at operating n (model clamp).
- Full call + hedges: `20260617_ana.ipynb` cell 20.

**n-scale upgrade (lever-arm):** the SdH lever-arm λ ≈ 1.07 and the Hall slope
(n_H/n_gate ≈ 1.05–1.07) agree → the geometry-prior absolute n/D scale was ~7% low.
Multiply the calibrated n (and F_L) by ≈1.07 for absolute values; the cap *ratio*
(1.300) and CNP line are unchanged.
