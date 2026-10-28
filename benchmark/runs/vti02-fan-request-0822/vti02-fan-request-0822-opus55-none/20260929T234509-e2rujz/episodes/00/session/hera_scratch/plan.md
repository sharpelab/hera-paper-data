# vti-02 stacking call — plan (HERA, E1)

*Written at the agent handoff (2026-08-23 ~05:30). The previous instance's plan
was not on disk; steps 0–3 below reconstruct what the notebooks show was run,
steps 4+ are forward. Kept current as data lands.*

Goal: ABAB vs ABCA vs ABCB for the B_1–B_2 pair (sr1), region-resolved where the
data allows (two series regions A/B seen at 0 T, run 5).

## Done
0. **Gate C** — runs 0–3 (`gate-current-sanity-check`): alive, no leakage,
   two resistance maxima per gate → two series regions.
1. **0 T gatemap + calibration** — run 5 (run 4 aborted, railed). Ridge A
   ratio c_bg/c_tg = 0.773 (data), c_tg = geometry prior (absolute n-scale
   *uncalibrated*), n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex).
   Ridge B parallel, electron-doped by 0.43e12 vs A. R_CNP grows with |D|
   (240 Ω → 2.4 kΩ at D ≈ +0.25): a D-tunable gap; not a discriminator alone.
   Hedge: the D_offset uses the R_CNP(D) minimum as D = 0 — circular if the
   device is ABCB (built-in polarization shifts the gap minimum); offset is small.
2–3. **SdH spot checks at D = 0** — run 6 (n = +3.2e12 nominal, 0→10 T),
   run 7 (n = −1.2e12, 10→0.3 T). Both oscillate from ~1–1.5 T.
   Run 7: tones ≈ 4.4 and 7.1 T (F_L nominal 12.4 T; sum 11.5 = 0.93 F_L).
   Run 6: tones ≈ 7.3 T (+ harmonics?) and 22.4 / ~30 T (F_L nominal 33.1 T).
   Two-pocket structure on both sides with fractions ≈ 0.25/0.75 (e) and
   0.38/0.62 (h), consistent with the ABAB bilayer-like pair (ideal 0.28/0.72)
   and with an n-scale ≈ 0.9–0.93× the geometry prior. **But** a single fixed-n
   trace cannot separate a second pocket from a harmonic or from region B's
   shifted density — that is what the fan is for.

## Next
4. **D = 0 Landau fan** (`landau-fan`) — run 8. n fast along the D = 0 line
   (−1.24 … +3.24e12 nominal, 150 pts, 0.03e12), B slow 0 → 10 T, 73 rows
   (0, 0.5; 1–1.5 T at Δ(1/B) = 0.03; 1.5–4.5 T at Δ(1/B) = 0.012 → F_Nyq 42 T;
   4.5–10 T at 0.25 T). ~5 h 15 m. Establishes:
   - absolute n-scale from QH fan-line slopes (calibrates c_tg; fixes F_L);
   - number of LL families and whether they **cross** (ABAB: two
     bilayer-like families with a crossing lattice; ABCA: one family, 16-fold
     zero LL, E ∝ B^… no inter-family crossings away from CNP; ABCB: gapped
     CNP at D = 0 and its own multi-pocket pattern);
   - per-column 1/B FFT → F_i(n) tracks: fractions F_i/F_L vs n on both sides
     (ABAB ≈ 0.28/0.72 at high n; ABCA single F ≈ F_L at high n, 3 trigonal-
     warping pockets at low n);
   - region B as a second fan with its own origin (n ≈ −0.43e12 nominal) →
     region-resolved read.
   Checkpoints: first rows (B = 0 row vs run 5 D = 0 cut; leakage; rail);
   ~2 T (fan lines visible? converge at CNP?); ~4.5 T (column FFT, tone tracks).
5. **Ride down at finite D** (decided on the fan read) — e.g. a fan or n-cut at
   D ≠ 0 descending 10 → 0 T, or an (n, D) map at fixed high B; targets:
   ABCB's D-asymmetric gap / LL crossings tuned by D (ABAB crossings move with
   D), ABCA's D-driven gap growth. Never re-traverse the field.
6. **Call** in ana (per-region verdict, evidence with run ids, hedges).
7. **Close-out** `return-to-initial`.

## What would change my mind
- Fan shows a single LL family with F ≈ F_L at high n and no crossings → ABCA,
  despite runs 6/7 two-tone reads (then the second tones = harmonics / region B).
- Fan-line slopes put the true n-scale far from 0.9× → re-derive fractions.
- Region B fan dominates one side → the two-tone read belongs to two regions,
  not two bands.
- CNP insulating at D = 0 with a minimum at D ≠ 0 → ABCB candidate; needs step 5.
