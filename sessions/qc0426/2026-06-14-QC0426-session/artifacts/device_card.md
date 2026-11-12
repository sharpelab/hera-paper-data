# Device card — QC0426 (trilayer graphene) — round 2

*Session device card for QC0426 on the **VTI** cryostat — round-2 HERA
live session (replication from a cooled start). Deployed into the
measurement directory alongside the working notebooks. This card carries
**physical truth only**: what is wired, what the hardware is, and the
outer safety box. Operating ranges, calibrations, and characterization
are **deliberately absent — establishing them is the session** (see the
session brief). This session's data ids start at 0 in `./data/`.*

## Identity
- **Device id**: `QC0426`
- **Material**: **trilayer graphene** (`3LGr`), **stacking order under
  investigation** — ABA (Bernal) and ABC (rhombohedral) trilayer have
  qualitatively different Landau-fan / quantum-Hall signatures and
  displacement-field dependence, and classifying the stacking from the
  fan-vs-D structure is this device's campaign goal. Form reads from the
  data; do not assert a stacking this card does not state.
- **Operator**: qingrui
- **Fridge**: **VTI (variable-temperature insert)** — *not* the
  dilution-fridge toploader. Base temperature this cooldown is
  **≈ 1.2–1.3 K**, not millikelvin.
- **Status**: **cold, wired, transport-uncharacterized for your
  purposes.** Loaded 2026-06-01; the device arrives as a characterizable
  unknown. Gate operating limits are provided (below); no CNP location
  and no contact rankings are on record — the device-init recipe chain
  (contact survey + CNP calibration) establishes those.

## Gate stack (three gates, unusual drive wiring)
- **Top gate** (`k_tg`): hBN dielectric. **Driven by the SRS DC205, not
  a Keithley** — in the data it appears as the column **`DC_bias`** (the
  DC205 voltage), and in sweep calls as `dc205_volt` (a
  `qcodes.Parameter` wrapping `k_tg.ramp_voltage`, `ramp_rate = 2`; the
  measure notebook's setup cells define it).
- **Back gate** (`k_bg`): hBN dielectric, driven by a **Keithley 2400**.
- **Si global back gate** (`k_si` / `k_2410`): doped-Si gate through
  **SiO₂**, driven by a second Keithley (`k_2410`). **The Si value is
  per-run — read `measurement_config`, never assume a campaign-wide
  constant.** Operating limit provided (below); pick a value within it
  per run (`silicon-backgate-survey` is not run this session).
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
device. The Si operating *point* (a value within its range) is per-run;
read `measurement_config`.

The SAFETIES cell in the measure notebook must commit **exactly these
numbers**; compare values, don't eyeball:

| Parameter | Operating limit | Notes |
|---|---|---|
| `dc205_volt` / `k_tg` | **[−6.0, +7.0] V** | provided; geometry ceiling is the hard fence behind it |
| `k_bg.volt` | **[−4.5, +4.5] V** | provided |
| `k_2410.volt` (Si) | **[−50, +50] V** | provided; operating point per-run |
| **B field (session cap)** | **\|B\| ≤ 8.0 T** | protocol-enforced (driver has no soft-limit hook) |

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
- **Voltage channels**: `sr1, sr2, sr3` carry four-terminal voltages;
  **contact pairs are per-run** and live in `measurement_config` (with
  the QSwitch live, in the `mc_fragment` the mux writes), never in a
  global block.
- **Contact switching — QSwitch (QDevil) mux**: `drivers.QSwitch` +
  `drivers.contact_mux.ContactMux`. **Bring-up complete and validated
  (2026-06-14)** — ContactMux is live on this rig:
  - Wiring topology (2026-06-12 rewiring, final per the operator's
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
    `lines` map), and **`qsw.reset()` is forbidden once Si is
    energized** — it opens the standing closures and drops the Si
    gate. **Si closures on lines 16/11 confirmed closed at bring-up
    (2026-06-14).**
  - **Instrument taps (BNC 1–8)**: 1 = sr1.V1, 2 = sr1.V2, 3 = sr2.V1,
    4 = sr2.V2, 5 = sr3.V1, 6 = sr3.V2, **7 = sr1.amplitude (AC
    source)**, **8 = sr0.V1 × −1e6 (measured AC current)**. ContactMux
    form: `breakouts = {"source": 7, "drain": 8, "sr1+": 1, "sr1-": 2,
    "sr2+": 3, "sr2-": 4, "sr3+": 5, "sr3-": 6}`. Worked example (per
    the routing slide): source T3 / drain T5 / measure T3–T4 ⇒ tap 7 →
    line 4, taps 1/2 → lines 4 and 6, tap 8 → line 7.
  - COM port: **ASRL4** (confirmed at bring-up 2026-06-14 — reconnected
    on ASRL4, not the expected ASRL3; Microchip VID_04D8 USB-CDC, with
    the DC205 and the logger-held Terranova gauge as the resident FTDI
    serials).
  - `settle_s` (calibrated relay settle at campaign time constant):
    **4 s** (calibrated 2026-06-14).
  - Bring-up: address **ASRL4**, `settle_s` **4 s**, Si 16/11 confirmed,
    validated 2026-06-14.
  ContactMux is **live**; `contact-survey-2t`'s automated flavor is
  available. Any mux anomaly in-session is stop-and-report.
- **Magnet**: **FastBi1K5** — custom Ethernet-driven magnet controller
  (192.168.0.10), **not an AMI430**. Out-of-plane field in **Tesla**
  (`magnet.mag`). Treat "0 T" as the set value, not an absolute field.
  Ramp and blocking behavior are rig-level facts — see the agent
  prompt's magnet discipline section.
- **Temperature / thermometry**: LakeShore controller; VTI base
  **≈ 1.2–1.3 K**.

## Session findings — round 2 (2026-06-14, this session)

*Established live; provisional until the phase-1 exit report blesses them.*

### Contact survey (`contact-survey-2t`, file_id 0–16, B=0, BG=Si=0)
- **Alive** (2T drive current ≈ 5 nA full): T2, T3, T4, T5, T7 (top); B3, B4, B5,
  B6, B7 (bottom).
- **Dead / high-R**: **T1** (~1.3 GΩ, localized — bad in both T1–T7 #0 and T1–T4 #3
  while partners T4/T7 conduct elsewhere), **T6, B1, B2, B8** (dead against
  confirmed-good anchor T4).
- **Method note**: drive is current-bias (0.5 V / 100 MΩ ≈ 5 nA), so the 2T current
  saturates for any device R ≪ 100 MΩ → it separates dead from alive but does **not**
  rank alive contacts by R; CNP and 4T resistances come from the gate map (V = I·R).

### Blessed measurement configuration (CONFIRMED, file_id 16 + 18)
- **source = T2, drain = T7**; **sr1 = T3–T4** (Rxx top), **sr2 = B4–B5** (Rxx
  bottom), **sr3 = T5–B6** (Rxy transverse). sr2's B=0/BG=0 weakness was the low-D
  region only — the gate map (file_id 18) shows it tracks the CNP strongly at large
  |D| (~50 kΩ peak), so it is usable. No swap.
- Re-select verbatim:
  ```python
  ROUTING_4T = {"source":"T2","drain":"T7",
                "sr1+":"T3","sr1-":"T4", "sr2+":"B4","sr2-":"B5", "sr3+":"T5","sr3-":"B6"}
  mux.select(ROUTING_4T)
  ```
- **4T confirm** (file_id 16): drain current full 5 nA; **sr1 CNP peak ~1 kΩ at
  Vtg ≈ 0** (BG=Si=0); sr3 ≈ 0 at B=0 (Hall-consistent); **sr2 weak** (~0.1–0.5 kΩ,
  near noise — bottom edge carries less current with both leads on top; watch / may
  swap).

### CNP / D-line calibration + capacitance ratio (file_id 18, settled 4τ map)
- **CNP line** `Vtg = slope·Vbg + b`, fit per channel, 16/17 rows (BG=+4.5 row
  edge-clipped, excluded). Axis orientation: ridge = Vtg (fast) vs Vbg (slow) rows →
  `slope = −c_bg/c_tg`.
  - sr1 (T3–T4): slope −1.314, b +0.212 V → **c_bg/c_tg = 1.314**, RMS 102 mV.
  - sr2 (B4–B5): slope −1.309, b +0.173 V → c_bg/c_tg = 1.309, RMS 113 mV.
  - Channels agree <0.4% → **one device calibration**.
- **Capacitances** (two-tier provenance — *ratio data-calibrated; absolute scale
  geometry-prior until a QH lever-arm check*):
  - `c_tg = 1.703e-3 F/m²` (geometry prior, 15.6 nm hBN — anchored).
  - `c_bg = 2.237e-3 F/m²` (= 1.3136·c_tg).
  - Geometry-prior ratio 1.300 (15.6/12) vs fitted 1.314 → agree ~1% (Verify
    geometry-sanity PASS).
- **Offsets**: `n_offset = −0.225` (10¹² cm⁻²); `D_offset = 0` (assumed — no
  symmetric-in-±D feature located). CNP at (Vtg,Vbg) = (+0.21, 0).
- **Calibration quality**: max |n| residual on ridge ≈ 0.21×10¹² cm⁻² (coarse
  0.325 V/pt grid + faint CNP near D=0 dominate it).
- **D-line designer** — re-derive:
  ```python
  from sharpelab_nb.gates import stack_capacitance, calc_gate_voltages
  c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg
  n_offset, D_offset = -0.225, 0.0   # n in 1e12 cm^-2, D in V/nm
  Vtg, Vbg = calc_gate_voltages(n, D, c_tg, c_bg, n_offset, D_offset)  # clip-by-drop to validators
  ```
  - **D envelope** (box corners): D ≈ [−1.15, +1.24] V/nm; at n=0, D ∈ [−1.0,+1.0]
    V/nm reachable. Constant-D lines at **|D| ≤ 0.5 V/nm cover full n ∈ [−4,+4]×10¹²
    cm⁻²**; window narrows at larger |D|.
- **Phase-2 signal (do not interpret yet)**: CNP Rxx grows strongly with |D| (~1 kΩ
  at D≈0 → ~78 kΩ at BG=−4.5, ~44 kΩ at BG=+4.5) and is **asymmetric in BG** — a
  displacement-field gap-like response; magnitude/asymmetry is a stacking
  discriminator.
- **Upgrade path**: absolute n/D scale pending QH lever-arm (dn/dB = ν·e/h);
  recalibrate before any ν assignment.

## Notes / caveats
- **VTI base T ≈ 1.2 K**, not mK — sets which QHE features are
  resolvable; factor it into any claim about features that are *absent*.
- **Data isolation is strict this session** (per the brief): no prior
  campaign or session directories exist for you. If a comparison seems
  to need prior data, the recipes' first-session branches apply.
- This session's `data/` ids start at 0; there are no designated
  reference runs.
