# vti-02 stacking-order campaign — plan (updated 2026-08-23 05:25)

Goal: region-resolved stacking call ABAB / ABCA / ABCB (or calibrated "cannot
tell") on the single provided pair (Rxx = B_1−B_2, source T_0, drain B_3),
evidence-cited, landed as the final ana cell per the output contract.

## Done

1. **Gate C liveness** — runs 0–3 (`gate-current-sanity-check`): all four 1D
   legs alive, leakage < ~120 pA transients, R peaks ≤ 330 Ω at D≈0. ✓
2. **0 T gatemap** — run 4 (aborted: sr1 railed on the high-|D| CNP ridge at
   20 µV), run 5 (100 µV, clean). ✓
3. **CNP + (n,D) calibration** — ana cell 13 / `hera_scratch/cal_run5.json`:
   c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (9.5 nm geometry prior),
   n_offset = −0.089e12 cm⁻², D_offset = −0.013 V/nm. D = 0 line inside the
   validators spans n = −1.27 … +3.27e12. ✓
4. **SdH spot checks** — run 6 (electron n=+3.2e12, B 0→10 T): light tone
   7.1 T (onset < 0.3 T) + high-F content 22–30 T, degenerate between
   harmonics of 7.1 and a heavy band (ABAB model pair 7.5/25.6 T); giant
   feature B > 7.5 T (R → 530 Ω). Run 7 (hole n=−1.2e12, 10→0.3 T): tones
   4.7 / 6.6 T (ABAB model pair 5.3/7.1 T). Both sides lean two-band
   (Bernal-like); frequency sums don't close cleanly (7.1+26 ≈ 33 ✓e-side;
   4.7+6.6 = 11.3 vs 12.4 h-side). Ana cell landed 2026-08-23. ✓

## Now

5. **Landau fan at D = 0** (this is the stacking call's centerpiece):
   fast axis n = −1.25 → +3.25e12 (181 pts, Δn = 0.025e12), gates co-swept
   along the calibrated D = 0 line (`multimegasweep`); slow axis B = 1.0 →
   10.0 T ascending, 75 mT (121 rows). sr1 at 200 µV (20 kΩ FS — CNP at high
   B will clip ≥ ~21 kΩ; the clip marks the ν=0 gap, the 50–600 Ω SdH
   features stay ≥ 0.25 % FS). ~9 h. Discriminators the fan reads:
   - number of independent gap-line families vs n (one 4-fold band → ABCA;
     light+heavy two-band → ABAB; Dirac-like + heavy → ABCB);
   - LL-crossing pattern between subband ladders (ABAB: crossings between
     light/heavy bilayer-like ladders; ABCB: monolayer-like ladder with
     √B-spaced crossings);
   - ν = 0 / low-ν CNP structure and its B-evolution;
   - electron/hole asymmetry of the dominant filling sequence;
   - resolves the run-6 harmonic-vs-heavy-band ambiguity (harmonics track
     k·f₁(n); a real band has its own n-slope).
6. **Fan analysis** — reform (n, B) map, d²R/dn² or log R fan plot, gap-line
   slope inventory (ν per line), per-window FFT vs n; compare against the
   three stacking models' LL spectra. Decide whether a targeted follow-up is
   needed (e.g. D≠0 cut at fixed B — gap opening at CNP distinguishes ABCA
   (large D-gap) from ABAB (mass tuning, semimetallic) — or a T-dependence
   for masses via LK if frequencies alone don't close).
7. **Verdict** — final ana cell per the output contract.
8. **Close-out** — `return-to-initial` (B→0, gates→0, heaters off, readback
   into session_notes.md).

## What would change my mind / kill criteria

- Fan first rows (B ≈ 1 T): dead channel, rail at 200 µV outside the CNP
  stripe, sustained gate leak > 1 nA (auto-trip) → abort, fix, re-run.
- By ~3 T: no n-dependent Landau structure beyond gatemap features → abort
  (T_e-limited; rethink with higher B window or different pair).
- Single-frequency closure (F = F_L) emerging on both sides → ABCA lean;
  follow with D-response check before calling.
- Leakage growth with B or T excursions → stop, notify (safety).
