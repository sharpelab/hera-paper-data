# vti-02 stacking call — plan (HERA, picked up 2026-08-23 ~05:30 after handoff)

Goal: ABAB / ABCA / ABCB for the one measured pair (sr1 = B_1–B_2), evidence-cited, or a calibrated "cannot tell".

## Done (inherited)
- **Gate C** runs 0–3: alive, no leakage; two R maxima through each gate → two series regions (A, B), Δn ≈ 0.43e12.
- **Step 1** run 5 0 T gatemap → calibration: c_bg/c_tg = 0.773 (data), c_tg = 9.5 nm prior (absolute scale UNCALIBRATED),
  n_offset −0.089e12, D_offset −0.013 V/nm. D = 0 window n = −1.27 … +3.27e12. CNP ridge R grows 240 Ω → 2.4 kΩ with |D|
  (≈ symmetric in ±D) — a D-tunable gap: weakly disfavours pure ABAB (semimetal), but not decisive alone.
- **Step 3** runs 6/7 SdH spots at D = 0 (my read, 2026-08-23, hera_scratch/ana_spots.py):
  - run 6 (n = +3.2e12, F_L = 33.1 T prior): tones ≈ 30 T (dominant at B > 2–3 T) and ≈ 7.5 T (persists to 0.3 T),
    plus 14–15 / 22 T (harmonic or combination); Rxx → ≈ 0 at 6.0 / 7.2 T (QH regime).
  - run 7 (n = −1.2e12, F_L = 12.4 T): 12.3–12.9 T strongest at B > 3 T; 6.6, 4.7, 8.5 T lower-B tones.
  - Ambiguity: 7.5 + 30 = 37.5 T = 1.13 F_L. Either (i) ABAB pair with the absolute lever arm 13 % above the prior,
    (ii) ABCA singleton ≈ F_L (lever arm −9 %) + 7.5 T from a light pocket / region B / harmonic, or (iii) something mixed.
    A single-n spot cannot separate these: the n-dependence F_i(n) and the fan-line slopes can.

## Next
- **Step 4 — Fan A (D = 0), THIS STEP.** Rxx vs (n, B): n fast −1.25 … +3.25e12 along D = 0 (91 pts, 0.05e12),
  B slow 1 → 10 T, uniform in 1/B (d(1/B) = 1/120 T⁻¹) to 4.9 T then 0.2 T steps (122 rows). ≈ 5.5 h, ends at 10 T.
  Establishes: (a) **absolute n calibration** from the QH-minimum lines n = ν·eB/h through the CNP (independent of stacking
  once ν identified — sum rule cross-check); (b) **per-column FFT F_i(n)** → number of Fermi surfaces vs n, slopes
  dF_i/dn, sum rule ΣF_i = F_L, onset density of a second band; (c) LL crossing pattern at high B (ABAB: two interleaved
  bilayer-like LL families crossing; ABCA: single family, large ν = ±8 zero-LL gap; ABCB: asymmetric / gapped CNP).
- **Step 5 — Fan B (D ≠ 0), ride the magnet down 10 → 1 T.** Same (n, B) fan at fixed finite D (target |D| ≈ 0.2 V/nm,
  sign chosen from the Fan A read; window shrinks — compute from the validators). Establishes D-response of the tones /
  crossings: ABAB — D mixes the two bilayer-like bands, tones shift, no big CNP gap; ABCA — layer-polarised gap, pockets;
  ABCB — ±D asymmetric. Priced ≈ 5 h. Decided after Fan A.
- **Step 6 (optional) — temperature**: LK masses on the Fan-A tones at one density (m* ratio light/heavy ≈ 2.6 for ABAB)
  if Fan A leaves ABAB vs ABCB open. Only if needed.
- **Close-out** per brief (return-to-initial).

## What would change my mind
- Fan A tones with **fixed ratio** that track as harmonics (F_2 = k·F_1 exactly at all n) → the 30/7.5 pair is one
  Fermi surface + harmonic, not two bands → pushes toward ABCA (single tone = F_L).
- Two tones with **different, non-proportional n-dependence** and ΣF = F_L (after absolute calibration) → ABAB (or ABCB).
- Second tone appearing only above an onset density, or on one carrier side only → ABCB / band-edge structure.
- Region-B (×1.13) duplicates of every tone → series mosaic; read region A as the dominant set.

## Risks
- CNP at high B may go insulating (ν = 0) and rail sr1 at 100 µV (10 kΩ FS) — accept on a few columns.
- τ = 0.3 s / 24 dB with 1.0 s dwell → ≈ 1-point lag along n (consistent direction every row; correct post hoc).
