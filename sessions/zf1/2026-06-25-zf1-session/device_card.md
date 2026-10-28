# Device card — zf1

*Per-device card for the zf1 dual-device chip on the **toploader** rig.
Deployed into the measurement directory; mutates per cooldown.*

## Identity
- **Device id**: `zf1`
- **Material**: Bernal bilayer graphene + WSe₂ (Aaron, 2026-06-06;
  bilayer above WSe₂)
- **Owner**: isaac (`izheng`)
- **Fridge**: toploader. Sample base ≈ 30 mK, electron T ≈ 40 mK
  (rotator probe loaded)
- **Dual-device chip**: top + bottom halves, separately gated. Bottom
  half is wired and used; top half is not.
- **Status**: cold; single cooldown (inserted 2026-04-15)

## Gate stack (geometry prior)
- **Dual graphite gates** (top + back), **no SiO₂** (Aaron, 2026-06-06).
- `t_tg` ≈ **23.6 nm**, `t_bg` = **20 nm** (cap ratio **1.18**);
  `κ_hBN` = 3.
- geometry is a prior only; treat derived n/D scales as uncalibrated
  until a gate map confirms them.

## Gate operating limits (validators, this cooldown)
- `k_tg.volt` ∈ **(−7, +6) V**
- `k_bg.volt` ∈ **(−4, +4.2) V**

Asymmetric on TG — hBN leakage onset higher on +V.

## Measurement setup / wiring
- **Current channel**: `sr830_1`, gain **−1e6** (Ithaco 1211), through a
  **100 MΩ** bias resistor.
- **Voltage channels**: `sr830_2`–`sr830_4`, gain **×100** ([VERIFY]
  preamp model) — divide the reading by 100. Gain is per channel, not per
  contact pair (a pair read 2-terminal on a voltage channel is still ×100).
- **AC drive**: `sr830_1.amplitude` 0.1 V → **1 nA** at the device
  (through the 100 MΩ resistor); lock-in frequency 7.777 Hz.
- **Provided config** (bottom device): `sr1="5-4"` (current),
  `sr2="5-4"` (2T), `sr3="30-31"` (4T longitudinal).
- **Active contact pairs**: 5-4, 6-4, 28-4, 7-4, 7-31, 30-31. **No contact mux —
  wired direct.**
- **DC current bias**: `dc205_1` through the 100 MΩ resistor → ±150 nA at
  ±15 V. Set `dc205_1.volt → 0` before reconfiguring or ending a
  measurement.
- **Gates**: `k_tg`, `k_bg` (Keithley 2400).
- **Unused**: Yokogawa `y200`, `k_tg2` (rotator θ-winding).

## Field (this cooldown)
- **Out-of-plane (perpendicular).** Rotator (ANC350 θ/φ) parked.
- **Trapped flux**: ~2mT — magnet already energised this cooldown, so
  nominal zero already carries trapped flux. Does not impede SC
  identification.

## Heater → temperature (this cooldown)
Open-loop; verify T from the readback, not the voltage. Ceiling **6.5 V**
sustained (7 V one-shot only).

| `heater.volt` (V) | T (mK) |
|---|---|
| 0 | ~30 (base) |
| 4.5 | ~250 |
| 6.0 | ~423 |
| 6.5 | ~480 |
| 7.0 | ~494 (one-shot) |

## (n, D) calibration — in-session, run 4 (2026-06-25)
Source: run 4 survey gatemap, CNP-ridge fit on the 4T channel (30-31),
`cnp-and-dline-calibration`. Two-tier provenance:
- **Ratio (data-calibrated):** fitted CNP slope dV_bg/dV_tg = −0.844 ⟹
  c_tg/c_bg = 0.844, vs geometry prior t_bg/t_tg = 0.847 — **agree 99.5%**.
  The geometry-prior capacitances are confirmed; (n, D) ratio is trustworthy.
- **Absolute scale (geometry prior):** c_tg = 1.1255e-3, c_bg = 1.3281e-3 F/m²
  (κ_hBN=3, t_tg=23.6 nm, t_bg=20 nm). Pending a Tesla-field QH lever-arm check
  (deferred — out of this round's 100 mT cap).
- **n_offset = −0.36×10¹¹ cm⁻²** (CNP → n=0; CNP at V_bg=0 is V_tg=+0.05 V).
  D_offset = 0 (no feature locating D=0 yet — stated assumption).
- Fit quality: 66/67 ridge rows, residual 26 mV, CNP closure max|n| 0.47×10¹¹ cm⁻².
- CNP-at-n=0 sanity gate (the rendered map) passes across all D; CNP gap broadens
  with |D| (bilayer gap opening). A 2T-only diagonal stripe (absent on 4T) is
  contact-related, not bulk.
