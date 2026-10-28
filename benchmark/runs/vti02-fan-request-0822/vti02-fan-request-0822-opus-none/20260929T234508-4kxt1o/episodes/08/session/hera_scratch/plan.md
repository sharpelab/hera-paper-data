# vti-02 — stacking-order plan (ABAB / ABCA / ABCB)

*Written 2026-08-23 at handoff, reconstructing the arc the first instance ran
(steps 0–3 below are done) and committing the rest. Kept current as data lands.*

Region resolved: **one region only** — the provided hardwired configuration
(source T_0, drain B_3, Rxx on B_1–B_2). `sr2`/`sr3` are n.c., so the output
contract's "per-region verdict" has exactly one line. Rewiring is operator work
at the breakout, not a detour I can take.

## What discriminates the three stackings, on this rig

| | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| Fermi surfaces at D = 0, finite n | **two** (decoupled bilayer-like bands, masses in ~1:2–3) | **one** (single quartic band) | two, *asymmetric* in carrier sign |
| SdH spectrum | two fundamentals F₁, F₂ with F₁+F₂ = n·h/4e, plus intersubband combinations F₂±F₁ | single F = n·h/4e (+ harmonics only) | two, with e/h asymmetry |
| D = 0 CNP | semimetallic, low R | gaps strongly and symmetrically with ±D | gaps asymmetrically in ±D |

The primary, cheapest discriminator is therefore **how many Fermi surfaces
carry the density, and whether the partition obeys the Luttinger sum rule as n
is varied** — which is what a Landau fan at D = 0 measures directly.

## Steps

0. **Gate C — liveness** (`gate-current-sanity-check`, runs 0–3). DONE: four
   gate legs to the card limits, no leakage. Device alive on the provided pair.
1. **0 T gate map** (`gatemap`, run 4 aborted → run 5). DONE: CNP ridge located,
   D = 0 fixed by the R_CNP(D) symmetry vertex (raw D = +0.013 V/nm).
2. **(n, D) calibration** (`cnp-and-dline-calibration` on run 5). DONE, but the
   *scale* is still the geometry prior (c_tg = 2.796 mF/m² from 9.5 nm hBN);
   only the **ratio** c_bg/c_tg = 0.773 is data-derived. Absolute n is therefore
   uncalibrated to ~10 %.
3. **SdH spot checks** (`sdh-spot-check`, runs 6 e-side n = +3.2e12, 7 h-side
   n = −1.2e12). DONE. Result: huge, clean oscillations (73 % of R pk-pk above
   7 T on the electron side, onset ≲ 0.3 T). Run 6 FFT peaks 7.06 / 15.88 /
   22.94 / 30.0 T. **Two readings fit within that window's δF = 1.76 T**:
   (a) one surface at 7.06 T plus harmonics 2×/3×/4×; (b) two surfaces
   F₁ = 7.06, F₂ = 22.94 with combinations F₂−F₁ = 15.88 and F₂+F₁ = 30.0.
   (a) is not a tetralayer band structure at all; (b) is the ABAB signature.
   **Not decidable at a single density** — this is what forces step 4.
4. **Landau fan at D = 0** (`landau-fan`, THIS STEP). B slow, uniform in 1/B,
   0.7 → 10 T, 110 rows; (V_tg, V_bg) co-swept along D = 0, n = −1.20 →
   +3.20 ×10¹² cm⁻², 89 points. Establishes, per column:
   - **F(n) for every tone.** A real Fermi surface has F ∝ |n| through the
     origin with a fixed fraction; a harmonic sits at exactly k×F₁ (slope k×);
     an *aliased* harmonic (F > F_Nyq = 41 T) runs with **negative** slope vs
     |n| — three unmistakably different tracks. This is the decisive test and
     it is why the fan beats any number of single-density spots.
   - **The Luttinger sum rule** ΣF_i = |n|·h/4e as a line vs n → an absolute,
     in-session calibration of the density scale, replacing the geometry prior.
   - **The filling sequence** of the LL gap lines at B ≳ 2 T (degeneracy 4 vs 8
     vs a 4N-fold CNP level), and whether the D = 0 CNP gaps at high B.
5. **D-dependence at fixed n** (next, ~1 h at 10 T riding down, or a fixed-B
   D-cut): symmetric vs asymmetric gapping in ±D separates ABCA from ABCB and
   corroborates ABAB's weak D response. Cheap because the magnet is already
   parked high.
6. **Optional T-dependence** (`heater.set_both`, ≤ 25 K) for a Lifshitz–Kosevich
   effective mass on the resolved tones — converts "two surfaces" into "two
   bilayer-like masses", the strongest ABAB confirmation. Only if steps 4–5
   leave the call at `moderate`, and only if the wall-clock is there.
7. **Call + close-out.** Verdict cell in the ana notebook per the output
   contract; then `return-to-initial`.

## What would change my mind

- **Step 4 shows a single tone tracking F = |n|·h/4e with only exact harmonics**
  → ABCA, and the run-6 combination-frequency reading was an artefact of the
  1.76 T resolution. Strong evidence either way; this is the crux.
- **Two tones, but their fractions drift with n** (not fixed) → not two rigid
  parabolic bands; reconsider ABCB or a Lifshitz transition, and hedge.
- **Electron/hole asymmetry in the number or fraction of tones** → ABCB.
- **Sum rule badly violated** (ΣF ≠ n·h/4e by ≫10 %) → either a missed surface
  (degeneracy ≠ 4, or a third pocket) or the CNP/offset is wrong; re-do step 2
  before trusting any verdict.
- Any leakage trip or a CNP that moves between the fan's endpoint columns and
  runs 6/7 → device drift; stop and re-baseline.

## Not measured / hedges to carry into the call

- One contact pair only → no region-resolved comparison, no Hall channel
  (`sr2`/`sr3` n.c.), so no independent n from R_xy.
- Absolute n rests on the sum rule (step 4) rather than on an R_xy calibration.
- Electron temperature ≈ 8 K on this rig; light-mass tones are LK-suppressed at
  low B, so a *missing* light tone at small |n| is a sensitivity statement, not
  a band-structure one.
