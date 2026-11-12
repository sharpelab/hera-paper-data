# vti-02 — stacking-order campaign plan (HERA)

Goal: ABAB vs ABCA vs ABCB for the one wired region (T_0 → B_3, Rxx on B_1–B_2), region-resolved, evidence-cited.
Written 2026-08-23 05:30 by the second instance (the first instance ran steps 0–3 without landing this file).

## Discriminators the plan is built on (chiral decomposition, D = 0)
- **ABCA** (J = 4 single block): one Fermi surface → one SdH tone F = nh/4e; zero-energy LL 16-fold → 4-fold-regular gap
  sequence ν = 8, 12, 16, … above it; fan lines straight through the origin; no LL crossings at D = 0.
- **ABAB** (J = 2 + 2, bilayer-like light + heavy, m ratio ≈ 0.38): two tones at fixed n with F_l + F_h = nh/4e and
  n_l/n_h ≈ m_l/m_h (fixed fraction) → two interpenetrating straight fans, LL **crossings** (localized Rxx spikes off any
  single ν-line), irregular apparent-ν sequence.
- **ABCB** (J = 3 + 1, trilayer-like + monolayer-like Dirac): two tones, but the Dirac block's density fraction varies with
  n (∝ E² vs E^{2/3}) → its LL lines **curve** in the (n, B) plane; monolayer half-integer sequence (ν = ±2, ±6, …) on top.
- Confound carried from run 5: a second region (B) in series, electron-doped by 0.43e12 → every feature doubled at
  n + 0.43e12 (×1.13 at n = 3.2e12). Doublets ≠ two bands; check the offset is constant in n (mosaic) vs ∝ n (band).

## Steps
0. **Gate C liveness** (runs 0–3) — DONE. Alive, no leakage, two CNPs through both gates (series mosaic, Δn ≈ 0.4e12).
1. **0 T gatemap → (n, D) calibration** (run 4 aborted/rail; run 5) — DONE. ratio c_bg/c_tg = 0.773, c_tg = geometry prior,
   n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex). D = 0 window inside validators: n = −1.27 … +3.27e12 (TG-limited).
   D-tunable gap on the CNP ridge (240 Ω → 2.4 kΩ at 0.25 V/nm) — not a stacking read.
2. **SdH spot checks at D = 0** (run 6 e-side n = +3.2e12 0→10 T; run 7 h-side n = −1.2e12 10→0.3 T) — DONE, analyzed 05:20.
   Onset ≈ 1.0–1.3 T both sides; Rxx → 0 QH minima from 1.4 T. Run 7: one dominant tone 12.6 T = nh/4e for 1.22e12
   (nominal 1.2 → absolute n scale good to ~2 %). Run 6: tones 29.4 (strongest), 22.3, 14.8, 7.3 T — 29.4 + 7.3 = 36.7 T
   (n 3.55e12, +11 %) reads as an ABAB-like pair with 22.3 the difference tone, OR 29.4 alone as a single band at 2.84e12
   (−11 %) with the rest background/mixing. Ambiguous at one density → the fan. Plus a 500 Ω Rxx anomaly at 8–9.5 T
   (ν ≈ 15–17): LL crossing? mosaic? — a fan localizes it.
3. **Landau fan at D = 0** (run 8) — NEXT. B slow 0.8 → 10 T, 167 rows (uniform 1/B, 0.008 T⁻¹, to 4.27 T; then 0.15 T),
   fast n = −1.24 … +3.20e12 in 0.04 (112 pts) co-swept on the run-5 D = 0 line. ≈ 8 h. Read: ν-lines through the origin
   (absolute n calibration from their slopes), gap sequence regularity, crossings, curvature, mosaic doublets.
   Ends at 10 T with gates at 0.
4. **Decide from the fan** (ana). If the fan alone discriminates → step 6. If not:
   5a. per-column SdH FFT of the fan (tone count vs n — fixed-fraction vs varying-fraction partition);
   5b. a second fan at finite D (e.g. +0.15 V/nm, inside the validators) riding the magnet down — gap opening at D
       is common to all three, but the LL crossings move differently; only if 5a is inconclusive (detour, ~8 h);
   5c. T-dependence of one or two SdH tones (LK masses) via set_both — heavy/light mass ratio for ABAB; costly, last resort.
6. **Call** in ana (output contract: per-region verdict + strength, evidence with run ids and numbers, hedges).
7. **Close-out** on the operator's `return-to-initial`.

## What would change my mind
- Fan shows a single regular 4-fold sequence with no crossings → ABCA; 5a as confirmation only.
- Two straight fans with crossings, constant density fraction → ABAB.
- Curved lines / half-integer monolayer sequence → ABCB.
- If the region-B doublets swamp the read → cannot tell (moderate), and say so; a rewire is operator work, not a detour.
- Any rail/leak/T excursion in the fan's first rows → abort, resize, re-run (the run-4 lesson).
