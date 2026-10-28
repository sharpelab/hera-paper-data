# vti-02 stacking call — plan (HERA, E1)

*Written 2026-08-23 at handoff pickup. The prior instance's steps 0–3 ran without a
plan.md on disk; they're reconstructed here from the notebooks and session_notes.*

## Goal
Call the stacking order (ABAB / ABCA / ABCB / cannot tell) of 4LG vti-02, per region,
from the one measured pair (sr1 = B_1–B_2, source T_0, drain B_3).

## Discriminators (what each stacking predicts)
- **ABAB (Bernal):** two bilayer-like bands (light, heavy; λ = 0.618 / 1.618) share the
  carriers. Away from the CNP: **two SdH branches F1 + F2 ≈ F_L(n)** with F_light/F_L ≈
  0.2–0.3, roughly independent of n. **LL crossings** between the two families (fan
  lines of two slopes-per-ν crossing; gap sequence changes at the crossings). Semimetal
  near the CNP; at D = 0 R_CNP is modest.
- **ABCA (rhombohedral):** one low-energy band. For n ≳ 1e12 there is **a single branch
  F ≈ F_L(n)** (plus harmonics) and no two-family crossings at D = 0. Low |n| gives
  trigonal-warping pockets (F ≈ F_L/3) and a Lifshitz transition. Strong D-induced
  CNP gap (exponential R_CNP(D)), plus gapped/insulating ν = 0.
- **ABCB (mixed, polar):** two bands, but with a frequency ratio / masses unlike ABAB.
  **Non-centrosymmetric**, so R_CNP(D) and the LL spectrum are asymmetric in ±D about
  the physical D = 0.
- **Confounder:** the pair spans two regions in series. Region A is the main ridge.
  Region B is the faint parallel ridge, electron-doped by ≈ 0.43e12 relative to A
  (run 5). A second fan family converging at n_A ≈ −0.43, and extra tones at
  F_L(n_A + 0.43), belong to region B.

## Steps
0. **Gate C — liveness** (runs 0–3): done. Alive, no leakage, two series CNPs.
1. **0 T gatemap** (run 5; run 4 railed, aborted): done. Ridge A slope 0.773, ridge B
   parallel at −0.43e12. R_CNP rises 300 Ω → 2.4 kΩ by D = +0.25 V/nm, a D-tunable
   gap: ABCA-leaning but not decisive (ABCB/ABAB can gap too). −D at the CNP is
   inaccessible inside the validators: ridge A leaves the window at D ≈ −0.08.
2. **(n, D) calibration** from run 5: c_tg 2.796e-3 (prior anchor), c_bg/c_tg 0.773
   (data), n_offset −0.089e12, D_offset −0.013 V/nm. Scale is still the geometry
   prior, so **the fan calibrates n absolutely** (QH minima n = ν eB/h).
3. **SdH spot checks** (run 6: e, n = +3.2e12; run 7: h, n = −1.2e12; D = 0): done.
   Strong SdH/QH on both sides. Run 6 tones: 7.1, 22.2, 29.5 T (7.1 + 22.2 ≈ 29.5 is
   an ABAB-like pair plus the sum, or a harmonic ladder of 7.1 — ambiguous at dF ≈
   1.5 T). F_L model 33.1 T means the n scale may be ~10% high. Run 7 tones: 12.3
   (= F_L 12.4), 6.6, 4.7. Onsets 0.3–0.7 T for the light tone, ~1.3 T for the heavy.
4. **D = 0 Landau fan** (this step). Fast axis n_A along the D = 0 line, −1.25 →
   +3.23e12 (the full in-validator window, 151 pts). Slow axis B: row at 0 T, then
   uniform in 1/B from 0.7 to 3.6 T (δ(1/B) = 0.0115, Nyquist 43 T > F_L max ≈ 39 T incl.
   region B), then uniform 0.15 T from 3.6 to 10 T. ~146 rows, ~7h45m, ends at 10 T.
   Establishes: per-column F(n) branches (the main discriminator), the fan-line
   families and crossings, both regions' fan origins, and the absolute n scale.
5. **Conditional, riding the magnet down from 10 T** (never re-traverse):
   - If the fan is two-branch (ABAB/ABCB-like): a **finite-D fan** at D = +0.15–0.2
     V/nm, 10 → 0.7 T, which tests D-sensitivity of the crossings / gap. The
     accessible D range is asymmetric; state what that means for the ABCB test.
   - If single-branch (ABCA-like): the same finite-D fan to see the D-gap in the LL
     spectrum. Also a low-|n| zoom for the trigonal-warping pockets if F_L/3 appears.
6. **Call** in the ana notebook (per-region verdict, evidence, hedges). Then close out
   (`return-to-initial`).

## What would change my mind
- Per-column FFT shows **one branch F = F_L(n)** at n > 1e12 with no crossings → ABCA,
  regardless of the run-6 pair read.
- **Two branches with F1 + F2 = F_L** and ratio ≈ 0.2–0.3 steady in n, plus fan
  crossings → ABAB.
- Two branches at a ratio inconsistent with ABAB, or ±D asymmetry in step 5 → ABCB.
- The fan-derived n scale moves the ratios; recompute all F/F_L after recalibrating.
