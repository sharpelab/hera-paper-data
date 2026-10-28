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
- **Active contact pairs**: 5-4, 6-4, 28-4, 7-4, 7-31. **No contact mux —
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

## Session results — 2026-06-21 (HERA, zf1 bottom device)
- **(n, D) calibration:** CNP-slope cap ratio **c_bg/c_tg = 1.189** (geometry
  prior 1.180; fit residual 17 mV), from the 0 T survey gatemap (file_id 2). CNP
  at TG=0 → BG=+0.026 V. n_offset = −c_bg·0.0259/e. **Ratio data-calibrated;
  absolute n/D scale still geometry-prior** (awaits a QH lever-arm).
- **Superconductivity FOUND — region SC1:** gate-tuned 2D SC at **n ≈ −5.0×10¹¹
  cm⁻², D ≈ −0.67 V/nm** (TG ≈ −5.64, BG ≈ +4.20 V — at the BG cap; D<0).
  Constellation: Rxx→0.57 Ω (file 10), I_c ≈ 8–11 nA (file 11), B_c⊥ ≈ 2.5 mT →
  ξ ~ 360 nm (files 12–13, normal-controlled), central supercurrent lobe /
  field-null ≈ −1 mT (files 14–15), Tc ~ 0.1–0.2 K (files 16–23, COARSE —
  thermometry stalled). Arc rides the BG=+4.2 cap (dome extent gate-cut).
- **WIRING note:** 4T Rxx channel = **sr3 (30-31)**, the campaign Rxx readout.
  2T (sr2, 5-4) saturates at 1 nA (drive feedthrough) — low-drive only.
- **RIG caveat:** temperature workers were stale this session (logfile T frozen
  at 33.7 mK, T_fridge=0); sample-T during heating is unreliable — re-verify the
  worker before any quantitative T-campaign.
