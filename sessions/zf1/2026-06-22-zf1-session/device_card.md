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

## Session findings (2026-06-22, HERA E0)
- **Cap-ratio CONFIRMED (data):** c_bg/c_tg = **1.185** from the 0 T survey CNP slope
  (`Vbg = −0.844·Vtg + 0.114`, resid rms 0.03 V, ~70 rows; run data/2). Matches the
  geometry prior 1.18. **Ratio: data-calibrated; absolute n/D scale: still geometry-prior**
  (QH lever-arm pending). CNP metallic at D≈0 (0.6 kΩ), gaps with |D|.
- **SUPERCONDUCTOR located (decisive):** proximity SC at **n ≈ −4.65×10¹¹ cm⁻², D ≈ −0.65 V/nm**
  (V_tg=−5.444, V_bg=+4.053; ratio-grade coords). Ic ≈ 18–24 nA (base), B_c⊥ ≈ 2.5 mT,
  Tc ≈ 234 mK (open-loop heater-T), ξ ~ 360 nm (o.o.m.), effective-zero field ≈ +1 mT.
  Narrow arc near the most-negative-D the BG validator (+4.2 V) allows. Full constellation
  (Rxx→0, Ic lobe, field-kill/flat-normal, Ic(T)→0) — see `20260622_ana.ipynb`.
- **THERMOMETRY [VERIFY] CORRECTION:** the live sample MC sensor this cooldown is
  **Probe1_MixingCh_low** (not Probe2 — Probe2 logfile dead since ~Sat 13:10, AVS worker
  likely down). Point `temperature` at Probe1; restart/verify the Probe2 worker. The
  "rotator/Probe2 loaded" line above may be stale — confirm which probe is loaded.
