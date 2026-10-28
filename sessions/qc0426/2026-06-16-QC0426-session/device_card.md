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
- **Back gate** (`k_bg`): hBN dielectric, driven by a **Keithley 2400**.
- **Si global back gate** (`k_si` / `k_2410`): doped-Si gate through
  **SiO₂**, driven by a second Keithley (`k_2410`). Operating limit
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
    provided config below): source T2 ⇒ tap 7 → line 3; drain T7 ⇒
    tap 8 → line 13; sr1 T3–T4 ⇒ taps 1/2 → lines 4 and 6.
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
  | drain (`sr0`) | T7 | 13 |
  | `sr1` (Rxx) | T3–T4 | 4, 6 |
  | `sr2` (Rxx) | B4–B5 | 22, 20 |
  | `sr3` (Rxy, Hall) | T5–B6 | 7, 19 |

  ContactMux form: `mux.select({"source": "T2", "drain": "T7", "sr1+":
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
