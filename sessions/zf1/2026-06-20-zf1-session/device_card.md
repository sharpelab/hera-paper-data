# Device card — zf1

*Per-device card for the zf1 dual-device chip on the **toploader** rig.
Deployed into the measurement directory; mutates per cooldown.*

## Identity
- **Device id**: `zf1`
- **Material**: Bernal bilayer graphene + WSe₂ (Aaron, 2026-06-06; layer
  order unspecified)
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
- [VERIFY] hBN thicknesses + layer order unconfirmed (Aaron, 2026-06-06)
  — geometry is a prior only; treat derived n/D scales as uncalibrated
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
  `sr2="5-4"`, `sr3="30-31"`, `sr4="5-30"`.
- **[CORRECTION 2026-06-20, operator (Aaron)] — the 4-terminal Rxx is
  `sr830_2`, NOT `sr830_3`.** The `sr2="5-4"` contact label in the config
  above is therefore wrong (5-4 = the drive pair = 2-terminal); sr2 is
  wired as a true 4T longitudinal Rxx (its actual contact pair is
  [VERIFY — needs operator]). Empirically consistent: sr2 reads ~3.4 kΩ
  metal / ~30 kΩ at the CNP (a normal 4T graphene Rxx), whereas sr3
  (30-31) reads ~15–25 Ω — not the Rxx channel. **Use `sr830_2` as Rxx
  for all maps / candidate scans / dV/dI.** sr3 role now uncertain
  (small-signal; possibly a near-short / adjacent-pad pair).
- **Active contact pairs**: 5-4, 6-4, 28-4, 7-4, 7-31. **No contact mux —
  wired direct.**
- [VERIFY] probe geometry — which contacts are
  source/drain/longitudinal/Hall is not documented; the config's contact
  *labels* are known-unreliable (see the sr2 correction above).
- **DC current bias**: `dc205_1` through the 100 MΩ resistor → ±150 nA at
  ±15 V. Set `dc205_1.volt → 0` before reconfiguring or ending a
  measurement.
- **Gates**: `k_tg`, `k_bg` (Keithley 2400).
- **Unused**: Yokogawa `y200`, `k_tg2` (rotator θ-winding).

## Field (this cooldown)
- **Out-of-plane (perpendicular).** Rotator (ANC350 θ/φ) parked.
- **Trapped flux**: ~2mT

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
