# vti-02 stacking call — plan (HERA, E1)

*Written 2026-08-23 on pickup (the previous instance left no plan.md; steps 0–3 below
reconstructed from the notebooks / session_notes and marked done). Kept current as data lands.*

## Goal
ABAB vs ABCA vs ABCB for 4LG vti-02, region-resolved on the one measured pair
(sr1 = B_1–B_2), with evidence citing run ids, or a calibrated "cannot tell".

## Discriminants (what each stacking predicts in data this rig can take)
| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| SdH tones at fixed n, D = 0 | two (light + heavy bilayer-like bands), F_l + F_h = F_L, F_l/F_h ~ 0.3–0.4, both ∝ n | one at F_L (3-pocket F_L/3 near CNP) | multiple, e–h asymmetric |
| Landau fan at D = 0 | two LL families → dense LL-crossing pattern (ν-lines interrupted / degeneracy alternating) on both sides | one chiral family: ν = ±8, ±12, ±16 … without crossings at |n| ≲ 3e12; big ±8 gap at low B; ν = 0 insulating early | crossings, but e–h and ±D asymmetric |
| R_CNP vs D (B = 0) | modest rise, symmetric in ±D | strong gap opening (kΩ→MΩ), symmetric; possible spontaneous gap at D = 0 | asymmetric in ±D / extremum off D = 0 |
| fan / map at fixed B vs ±D | symmetric | symmetric (layer-polarized transitions) | asymmetric |

## Steps
0. **Gate C liveness** — DONE, runs 0–3: alive, no leakage, Rxx 60–330 Ω.
1. **0 T gatemap + (n, D) calibration** — DONE, run 5: ridge A ratio c_bg/c_tg = 0.773, n_offset −0.089e12,
   D_offset −0.013 V/nm (R_CNP(D) vertex). c_tg still the **geometry prior** (density scale unverified →
   step 3 calibrates it from QH slopes). A second parallel ridge B (slope 0.691) sits at n_A = −0.43e12:
   a second region in series inside the pair — watch for a second LL family converging there.
   R_CNP rises 300 Ω (D≈0) → 2.4 kΩ (D = +0.25): moderate, not ABCA-strong; ±D window is only
   [−0.11, +0.32] V/nm at the CNP (TG floor −0.3 V).
2. **SdH spot checks** — DONE (runs 6, 7), ana pending (land during step 3).
   Run 6 (n = +3.2e12): tones 7.1 + 22.2 T (sum 29.3) and 29.5 T; nominal F_L = 33.1 T → if 29.5 = F_L,
   density scale is ×0.89. Two tones summing to F_L = ABAB-like pair; not yet decisive (harmonic ambiguity).
   Run 7 (n = −1.2e12): 6.6, 4.7, 12.3, 8.5 T; QH zeros already at 2 T.
3. **Landau fan at D = 0** — THIS STEP. n fast −1.25 → +3.20e12 (0.025e12, 179 pts) along the D = 0 line,
   B slow 0 → 10 T (0.05 T to 2 T, 0.1 T to 6 T, 0.2 T to 10 T; 93 rows), ≈ 7.2 h.
   Establishes: ν sequence per side, LL-crossing pattern (the main ABAB vs ABCA discriminant),
   the density scale (c_tg) from QH-line slopes, SdH tones vs n from low-B columns, region-B family.
   Checkpoints: first rows (B = 0 row vs run 5 D = 0 cut, rail, leakage); 2 T (lines + ν assignment +
   crossing read); 6 T (continue to 10 T vs stop and start step 4 at 6 T).
4. **±D asymmetry at fixed B** (ABCB discriminant, and D-tuned crossings) — (n, D) map at the field the fan
   ends at, inside the symmetric window |D| ≤ 0.11 V/nm (plus the +D side to 0.3 for the record).
   ABAB/ABCA symmetric; ABCB asymmetric.
5. **Only if 3–4 are ambiguous:** SdH amplitude vs T (LK masses) at one density: light ~0.03, heavy ~0.06 mₑ
   for ABAB vs one mass for ABCA. Costs hours of T settling; last resort.
6. **Call** in ana (output contract), then **close-out** (`return-to-initial`).

## What would change my mind
- Fan shows a single crossing-free family with gaps at ±8, ±12, ±16… and early ν = 0 → ABCA (overturns the run-6 lean).
- Clear ±D asymmetry at fixed B / R_CNP(D) → ABCB over ABAB.
- Two families in the fan that are **region A + region B** (converging at n_A = 0 and −0.43e12) rather than two
  bands of one region → the two-tone read of run 6 must be re-examined (a region-mixing artifact, not ABAB).
