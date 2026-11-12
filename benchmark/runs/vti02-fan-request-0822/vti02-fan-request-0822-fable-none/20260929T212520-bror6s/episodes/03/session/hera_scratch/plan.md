# vti-02 stacking-order campaign — plan (reconstructed at handoff, 2026-08-23)

*Original plan.md was missing from hera_scratch at handoff; reconstructed from the
notebooks + session_notes. Goal: ABAB vs ABCA vs ABCB call per the output contract.*

## Done

1. **Gate C — liveness + gate-current sanity** (runs 0–3): provided pair alive,
   R(D≈0) peaks ≤ 330 Ω, leakage at pA baseline.
2. **0 T gatemap → (n, D) calibration** (run 4 aborted/railed; run 5 good):
   ridge fit gives c_bg/c_tg = 0.773 (c_tg anchored at 9.5 nm geometry prior),
   n_offset = −0.089×10¹², D_offset = −0.013 V/nm (R_CNP(D) vertex).
   `hera_scratch/cal_run5.json`. Realized D = 0 window inside validators:
   n = −1.27 … +3.27×10¹² (hole side TG-limited).
3. **SdH spot checks at D = 0** (run 6 e-side +3.2×10¹² B 0→10 T; run 7 h-side
   −1.2×10¹² B 10→0.3 T): ana cells 14–17. Electron: single robust F ≈ 7.4 T
   + harmonics (ABAB light-band value; no 33.1 T single-surface tone). Hole:
   non-harmonic pair 4.7 + 6.6 ≈ F_full = 12.4 T. Lean: multiband both signs —
   ABAB-consistent, ABCA-disfavored, ABCB open.

## Now

4. **Landau fan at D = 0** (run 8): n fast −1.25…+3.25×10¹² (141 pts), B slow
   1→10 T, 120 rows uniform in 1/B (per-column `sdh_fft`-ready; Nyquist 66 T,
   window resolution 1.1 T). Establishes: (a) F(n) per band — slopes/partition
   distinguish two-parabolic-band ABAB from single-band ABCA from mixed ABCB;
   (b) the LL gap sequence + crossing pattern in (n, B). ≈ 7.5 h. Ends at 10 T,
   gates parked at 0.

## Next / conditional

5. **Fan analysis**: re-formed fan in (n, B); per-column FFT → F vs n map;
   ν-line indexing of the strong gaps (n = ν eB/h); compare tone partition
   n₁(n), n₂(n) against ABAB (two bilayer-like bands), ABCA (single, F = nh/4e),
   ABCB (Dirac + heavier band → one ~linear-in-n light F with small slope
   changes). Verdict evidence assembled here.
6. **If the call is still ambiguous**: a D ≠ 0 wedge at fixed n (gap response to
   D differs strongly between stackings) *riding the field down* from 10 T —
   design only if step 5 leaves ABAB vs ABCB open. Budget ≤ 3 h.
7. **Close-out**: `return-to-initial` (B→0, gates→0, heaters off, readback).

## What would change my mind

- Fan shows a single F(n) = nh/4e line with no second family → ABCA after all
  (spot-check low-F content would then be 2D-substructure artifacts).
- F(n) families not summing to nh/4e → degeneracy ≠ 4 (broken symmetry) or
  calibration error → re-derive cal from the fan's own CNP trace before any call.
- A light band persisting to the hole side with monolayer-like (√n) frequency
  scaling → ABCB weight.
- CNP drift vs run 5 (features shifted in gate voltage) → re-calibrate, re-run
  affected segments.
