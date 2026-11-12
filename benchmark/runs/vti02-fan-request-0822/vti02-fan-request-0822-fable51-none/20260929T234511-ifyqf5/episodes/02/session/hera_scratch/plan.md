# vti-02 stacking-order campaign — plan (written 2026-08-23 by the second instance; reconstructed for steps 1–3 from the notebooks)

Goal: ABAB vs ABCA vs ABCB, region-resolved (one contact pair: sr1 = B_1−B_2), evidence-cited, or a calibrated "cannot tell".
Envelope: TG [−0.3, +1.0] V, BG [−1.3, +2.0] V, Si [−25, +25] V (Si untouched — no standalone Si survey, banned), |B| ≤ 10 T, T ≤ 100 K. D = 0 line inside the box: n = −1.28 … +3.26 ×10¹² cm⁻² (TG-limited both ends).

## Discriminants (what each stacking should show at D = 0)
- **ABCA (rhombohedral):** one |k|⁴ band → a single SdH frequency F_L = n·h/4e at low n; 16-fold zero-energy LL (N = 0–3 × spin × valley) → the first gap at ν = ±16, then Δν = 4 above; ν = 4, 8, 12 only emerge as interaction-driven at high B. Huge D-induced gap at the CNP (R_CNP → ≫ 100 kΩ at |D| ~ 0.2 V/nm).
- **ABAB (Bernal):** two bilayer-like sectors (effective γ₁ scaled by (√5 ± 1)/2) → two SdH frequencies whose sum is F_L, light/heavy masses; each sector carries an 8-fold zero LL → ν = ±8 strong; LL crossings between the sectors (gap closings along a fan line at specific B). Weak D-induced gap (semimetal at D = 0; run 5: R_CNP 240 Ω → 2.4 kΩ at D = 0.25 V/nm — small).
- **ABCB (mixed):** monolayer-like (4-fold zero LL, ν = ±2 gaps) + trilayer-like sectors; small intrinsic gap at D = 0; asymmetric fan.

## Steps
1. **[done] Gate C liveness** — runs 0–3: alive, no leakage, two series CNPs (regions A, B; Δn ≈ 0.43×10¹²).
2. **[done] 0 T gatemap → calibration** — run 5: c_bg/c_tg = 0.773 (data), c_tg = geometry prior (2.796 mF/m²), n_offset −0.089×10¹², D_offset −0.013 V/nm. Absolute n scale is a prior (±~10 %) — the fan's ν slopes will fix it.
3. **[done] SdH spot checks** — run 6 (e⁻ +3.2×10¹²): tones 7.3 / 15 / 22 / 30 T — F_L harmonics (16-fold?) vs an ABAB light+heavy pair are degenerate on one trace. Run 7 (h⁺ −1.2×10¹²): 7.1 + 12.6 T — likely regions B and A in series.
4. **[next] Landau fan at D = 0** — B slow 0, 1.0 → 10 T (100 mT, 92 rows), n fast −1.25 → +3.25 (0.03 → 151 pts co-swept TG/BG), sr1 100 µV. Establishes: fan-line ν assignment (fixes n scale), the gap sequence at D = 0 (16 vs 8 vs 2/4 dominant), number of sectors (crossings vs harmonics), the two-region confound (two convergence points). ≈ 6 h 40 m. Ends at 10 T.
5. **Fan analysis** — re-form (fan_grids/resistance_grids), plot Rxx(n, B) and dRxx/dn, overlay ν lines from the CNP, fit slopes → ν; FFT vs n (F(n) linear ∝ n → single band/harmonics; sub-linear pockets → multi-band); tabulate which ν have minima at each B. Land on ana.
6. **Conditional, riding the magnet down from 10 T:** (a) if the D = 0 fan leaves ABAB vs ABCA open → a second fan at finite D (e.g. +0.15 V/nm; ABCA: gap and layer-polarized LL sequence change drastically; ABAB: modest) 10 → 1 T; (b) if the sector count is the open question → a temperature ladder at one n for LK masses (T_e ≈ 8 K on this rig limits this — only if the low-B tones survive to ≥ 10 K).
7. **Call** — final ana cell per the output contract. Then close-out on request (`return-to-initial`).

## What would change my mind
- A fan showing gaps at ν = ±16 first, single-slope harmonics, and an insulating ν = 0 → ABCA-leaning; a second finite-D fan then confirms via the giant gap.
- Two families of fan lines with crossings and ν = ±8 dominant → ABAB.
- ν = ±2 lines from a Dirac sector + an intrinsic D = 0 gap → ABCB.
- Fan lines converging to two n-origins → region B is a series contribution; read the dominant family only and hedge.
- Rails/leakage/T drift at the first rows → abort, resize, re-run.
