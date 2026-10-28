# vti-02 stacking call — plan (HERA, E1)

*Picked up mid-session 2026-08-23 ~05:30 from the previous instance (no plan.md was on
disk; steps 0–3 reconstructed from the notebooks, step numbers kept as cited there).*

Goal: ABAB vs ABCA vs ABCB for the one measured pair (sr1 = B_1−B_2), region-resolved,
evidence-cited, or a calibrated "cannot tell".

## Discriminators (what each stacking predicts)

- **ABAB (Bernal)** — centrosymmetric; two bilayer-like bands (effective γ1·λ, λ = 1.618 / 0.618)
  → at D = 0 **two SdH families on each carrier side**, each F_i ∝ n, density shares ≈ 0.72 / 0.28
  (∝ λ in the parabolic limit; the light share grows toward low n), ΣF_i = F_L = n·h/4e.
  Two-band mixing tones F2 ± F1 are expected in Rxx. Interpenetrating LL families with crossings in
  the (n, B) fan. Semimetal CNP, modest R_CNP(D) growth.
- **ABCA (rhombohedral)** — centrosymmetric; one chiral band per valley → **one SdH family**,
  F = F_L above the low-n trigonal-warping pockets (three pockets → F_L/3 per pocket at low n);
  strong D-gap (R_CNP rising steeply with |D|).
- **ABCB (mixed)** — polar (no inversion / mirror-z): **±D asymmetric** transport (R_CNP(D) and fan
  features not symmetric about the symmetric point; possible D-hysteresis); multi-band like ABAB
  but shares not locked to the Bernal λ ratio.
- Density-scale is independent of stacking: QH ν-line slopes dn/dB = ν·e/h in the fan fix the absolute
  c_tg; then ΣF_i vs F_L tests whether the tones account for all carriers.

## Steps

0. Gate C liveness — **done** (runs 0–3): alive, no leakage, Rxx 60–330 Ω, two series CNP maxima.
1. 0 T gatemap + (n, D) cal — **done** (run 5; run 4 aborted/railed). ratio c_bg/c_tg 0.773 (data),
   c_tg = 9.5 nm prior (scale unverified), n_offset −0.089e12, D_offset −0.013 V/nm. D = 0 line spans
   n = −1.27 … +3.27e12. Region B (parallel ridge, +0.43e12 electron-doped vs A) = series-mosaic confound.
   R_CNP(D) symmetric about D_offset, 240 Ω → 2.4 kΩ at |D| ≈ 0.25 V/nm.
2. Feasibility model (previous instance, in its cell markdown): ABAB pair at n = +3.2: ≈ 7.5 / 25.6 T;
   ABCA 33.1 T; hole n = −1.2: ABAB ≈ 5.3 / 7.1, ABCA 12.4 T (LK-marginal).
3. SdH spot checks — **done** (run 6: n = +3.2e12, 0→10 T; run 7: n = −1.2e12, 10→0.3 T).
   Run 6 FFT (1.5–10 T, ΔF 1.8 T): 7.1, 15.9, 22.9, 30.0 T — reads as F1, F2−F1, F2, F1+F2 of a two-band pair
   (7.1 + 22.9 = 30.0; shares 0.24 / 0.76) — suggestive of ABAB, not evidence (harmonics of 7.1 T within ΔF); ΣF = 30.0 vs F_L(prior) 33.1 → c-scale ≈ 0.91
   (to be fixed by ν-slopes). Alternative to exclude: 7.1 T family + harmonics (14.2/21.3/28.4) — the
   n-dependence separates harmonics (k·F1) from mixing tones (F2 ± F1). Run 7 (hole): 5.3 T dominant +
   10.6 / 14 T, messier (near-CNP band physics); onset ≈ 0.7 T.
4. **D = 0 Landau fan (this step)** — slow B 1 → 10 T uniform in 1/B (81 rows, Nyquist 44 T,
   ΔF 1.1 T at 1–10 T), fast n −1.25 → +3.25e12 along D = 0 (121 pts, 25e9 step for |n| ≤ 0.75, 50e9 beyond),
   sr1 100 µV. ~4 h 50 m. Establishes: F_i(n) for every tone on both sides (band count, shares,
   harmonics vs mixing), ν-line slopes → absolute density scale → Luttinger sum, LL-crossing pattern.
   Ends at 10 T → step 5 rides the magnet down.
5. **±D test at fixed high B / D-fan** (conditional on 4) — ABCB discriminator + ABAB/ABCA D-response:
   (n, D) map at 10 T (or fan at D = ±D1 riding 10 → 1 T): symmetry of LL spectrum under D → −D;
   ABAB: D-driven LL crossings symmetric in ±D; ABCA: gap at CNP opens fast; ABCB: asymmetric.
6. (Optional, only if the band-count read is ambiguous) LK masses at one n: T = base, 5, 10, 15 K,
   mass ratio of the two families (ABAB ≈ 2.6).
7. Call → ana final cell (per-region verdict / evidence / hedges). Then close-out (return-to-initial).

## What would change my mind

- Fan shows **one** family with F = F_L(ν-calibrated) and the 7.1/22.9 tones vanish or track as
  k·F1 harmonics → ABCA (or a domain of it).
- Tones with **n-offset** relative to each other (≈ +0.43e12 region-B offset) → two regions contributing;
  the call becomes region-mixed.
- ±D asymmetry beyond the D_offset calibration (step 5) → ABCB.
- Shares far from ~0.25/0.75 with ΣF = F_L → multi-band but not Bernal-locked → ABCB candidate.
