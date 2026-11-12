# vti-02 stacking call — plan (HERA, E1)

*Rewritten 2026-08-23 at the instance handoff: no plan.md was on disk; steps 0–3 below
reconstruct what the prior instance ran (cells cite the steps), steps 4+ are forward.*

Goal: ABAB vs ABCA vs ABCB for the single measured pair (sr1 = B_1−B_2), region-resolved
(runs 0–5 show two series regions A, B in that pair: B is electron-doped +0.43e12 vs A).

## Discriminators (what each stacking predicts in what this rig can measure)
- **ABAB (Bernal)**: two bilayer-like bands at each E_F → **two SdH tones per density,
  F_light + F_heavy ≈ F_L = |n|h/4e** (light ≈ 0.23 F_L at high n); LL crossings between
  the two families → irregular (missing) ν = 4N minima and a crossing checkerboard in the
  fan; semimetallic CNP at D = 0; R(n, D) = R(n, −D) (mirror symmetric).
- **ABCA (rhombohedral)**: single band → **one tone at F_L** at high |n| (trigonal-warping
  pockets / F_L/3 only very near CNP); clean ν = 4N sequence, no crossings at high n;
  strongly D-tunable CNP gap; R(n, D) = R(n, −D) (inversion symmetric).
- **ABCB (mixed/polar)**: no mirror or inversion symmetry → **R(n, D) ≠ R(n, −D)**,
  CNP gapped / R_CNP(D) minimum displaced from the symmetric point, possible hysteresis
  in D; LL spectrum not a sum of two bilayer families (tone fractions deviate from the
  ABAB bilayer-pair template).
- Region B (series) contributes tones at its own density (n_A + 0.43e12): same template
  shifted — tones at ×(n+0.43)/n. Must be assigned before counting tones.

## Steps
0. **Gate C** (runs 0–3) — DONE: alive, no leakage, two series CNPs (A, B).
1. **0 T gatemap** (run 5; run 4 aborted/railed) — DONE: ratio c_bg/c_tg = 0.773,
   n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex), ridge B +0.43e12.
   Absolute n scale = geometry prior (c_tg @ 9.5 nm) — pending lever-arm check.
2. **Feasibility / model table** — done in the prior instance's reasoning (not on disk):
   ABAB pair ≈ 0.23/0.77 F_L at n = 3.2e12, ABCA singleton F_L.
3. **SdH spot checks** (runs 6 e-side n = +3.2e12, 7 h-side n = −1.2e12) — DONE, analysis
   landing in ana: run 6 tones 7.0 / 15.8 / 22.8 / 29.9 T (1.3–5 T), 30.0 T alone above
   5 T; 7.0 + 22.8 ≈ 29.9 = full-density tone → **ABAB-like pair**; QH zeros at
   ν ≈ 16, 20, 28, 32, 36, 44, 48, 60, 64 with 24/40/52/56 missing → crossings.
   **Lever-arm check**: F_total = 30.0 T ⇒ n_true = 2.90e12 = 0.907 × nominal.
   Run 7 (holes, near CNP): tones ~4.4 / 6.7 / 12.2 T (1–10 T), messy — semimetal regime.
4. **Landau fan along D = 0** (NOW; operator request): B slow 1 → 10 T (uniform 1/B,
   Δ(1/B) = 0.01 up to 3.1 T, then 0.1 T steps), n fast −1.25 … +3.25e12 (nominal, full
   D = 0 window inside the validators), 181 pts. ~6.9 h. Establishes: tone content F(n)
   per column across both carrier signs (two-tone sum rule vs singleton), the n-scale
   (fan slopes / F_total vs n), region-B tone assignment (×(n+0.43)/n family), LL-crossing
   pattern at high B. Checkpoints: first rows; row ~40 (1.6 T) FFT preview at high n;
   row ~68 (3.0 T) FFT over 1–3 T all n — continue for the QH crossing read or cut.
5. **D-symmetry test** (next, cheap): R(n, ±D) at fixed n (0 T and/or at high B on the
   fan's endpoint) — the ABCB discriminator (asymmetry / hysteresis in D). Run as a
   (n, D) rectangle in calibrated coordinates, both sweep directions for hysteresis.
   Constrained by the box: at D = 0 the window is TG-limited; |D| reach ≈ 0.3 V/nm.
6. **Call** in ana (output contract) — per-region (A, B of the one pair) verdict.
7. **Close-out** (brief `return-to-initial`).

## What would change my mind
- Fan columns at high n show a **single** tone at F_L (no light partner) → ABCA.
- Tone fractions off the bilayer-pair template, or R(n, D) ≠ R(n, −D) / hysteresis → ABCB.
- The run-6 7 T tone turns out to be region B's or a harmonic/difference artefact
  (e.g. doesn't scale ∝ n across the fan) → ABAB evidence weakens.
