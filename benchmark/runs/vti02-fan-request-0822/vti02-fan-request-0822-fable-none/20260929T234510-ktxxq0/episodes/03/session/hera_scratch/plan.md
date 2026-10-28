# vti-02 stacking-order campaign — plan

*Reconstructed at handoff pickup (2026-08-23): the file was missing from
`hera_scratch/` although steps 1–3 are complete on disk (runs 0–7, ana cells,
session_notes). Steps below restate what was done from the record, then carry
the arc forward.*

**Goal:** stacking order of vti-02 (tetralayer graphene): ABAB vs ABCA vs ABCB —
region-resolved (one wired pair: sr1 = B_1−B_2), evidence-cited, or a calibrated
"cannot tell". Output contract: final ana cell.

## Steps

1. **[DONE] Gate C liveness** (`gate-current-sanity-check`, runs 0–3): contacts
   alive on the provided configuration, gate leakage ~−90 pA median, no trips.
2. **[DONE] 0 T gatemap → (n, D) calibration** (`gatemap` runs 4 aborted / 5;
   `cnp-and-dline-calibration`, ana cell 13): ratio c_bg/c_tg = 0.773, c_tg
   anchored at 9.5 nm prior, n_offset −0.089×10¹², D_offset −0.013 V/nm
   (`cal_run5.json`). Two parallel CNP ridges (A main, B: mosaic region
   +0.43×10¹² offset). D-tunable gap at CNP (240 Ω → 2.4 kΩ by |D| ≈ 0.25 V/nm).
   D = 0 window inside validators: n = −1.27 … +3.27×10¹² (TG-limited).
3. **[DONE] SdH spot checks** (`sdh-spot-check`, runs 6 electron +3.2×10¹² /
   7 hole −1.2×10¹², D = 0, base T): multi-tone SdH both signs.
   - e-side: dominant F = 7.1 T (onset < 0.3 T, harmonics to 4×), plus low tones
     3.0 / 4.2 / 5.2 / 9.5 T; single-FS F(|n|) = 33.1 T ≫ any tone → multi-pocket.
   - h-side: tones 4.7 / 6.6 / 8.5 / 12.3 T; F(|n|) = 12.4 T.
   - Oscillations resolvable from ≲ 1 T to 10 T at T_e ≈ 8 K → a fan is
     well-conditioned. Frequency inventory alone is not a clean stacking read
     (harmonic/mosaic ambiguity) — the fan's gap sequence is the discriminator.
4. **[ACTIVE] Landau fan at D = 0** (`landau-fan`): fast axis n = −1.25 …
   +3.25×10¹² along the calibrated D = 0 line (226 pts, 0.02×10¹²), slow axis
   B = 0 → 10 T (201 rows, 50 mT). Establishes: (a) integer-ν gap sequence and
   its degeneracy pattern (4-fold-dominant vs 8/16-fold zero-LL structure,
   LL-crossing pattern vs B — the ABAB/ABCA/ABCB discriminator), (b) ν = 0 /
   CNP behavior in B, (c) an independent lever-arm check from fan-line slopes
   (n-scale is currently a geometry prior), (d) region-B mosaic lines at ×1.13 n
   if present. Ends at 10 T (never re-traverse; next step rides down).
5. **Targeted follow-ups** (chosen from the fan read): temperature ladder /
   LK masses at 2–3 spots riding B down (m* set distinguishes model tables), or
   a finite-D fan slice if the D = 0 read is ambiguous (ABCA's D-gap vs ABAB's
   crossing shifts). Sized after step 4.
6. **Verdict** — final ana cell per the output contract; then close-out
   (`return-to-initial`).

## What would change my mind / kill criteria

- Fan first-rows railing or leak trip → abort, resize, re-run.
- Calibration failure: fan-line slopes off the run-5 n-scale by ≫ 10 % →
  re-anchor c_tg from the fan itself before any ν labeling.
- Fan gap sequence ambiguous between models at base T → step 5 masses carry
  the call; if both ambiguous → calibrated "cannot tell" with the hedges named.
- CNP drift between runs (compare fan B≈0 rows vs run 5) → recalibrate.
