# vti-02 — plan (stacking order: ABAB vs ABCA vs ABCB)

*Written 2026-08-23 by the incoming HERA instance (the previous instance's plan text was not on disk;
steps 0–3 below are reconstructed from the measure/ana notebooks and session_notes). Kept current as data lands.*

## Discriminators (what separates the three stackings in a transport device with one Rxx pair)
- **Band count at D = 0 (SdH tones vs n):** ABAB = two bilayer-like bands (light λ− / heavy λ+) → two independent
  SdH tones F1(n) + F2(n) = F_L(n), ratio F2/F1 drifting with n (non-parabolicity). ABCA = one chiral band →
  a single tone ≈ F_L(n) at |n| ≳ 1e12 (no light independent pocket). ABCB = two bands but no inversion
  symmetry → polar: electron/hole and ±D asymmetric spectra, gapped/insulating CNP at D ≈ 0.
- **Harmonic vs independent:** a tone at k·F1 is a harmonic iff it tracks exactly k·F1(n) at every n AND its
  amplitude/onset obeys the harmonic hierarchy (weaker, later onset than lower harmonics). Independent tones do neither.
- **Landau-level pattern (fan map):** ABAB → two ladders with LL crossings (Rxx maxima/minima lines that cross and
  reconnect); ABCA → one ladder (lines through the CNP with Δν = 4 at high n). QH minima slopes also give the
  absolute n scale (lever-arm check).
- **D response (conditional step):** ±D symmetry of R and of the fan (ABCB would break it).

## Steps
0. **Gate C** — DONE (runs 0–3): alive, no leakage, two series R maxima (regions A, B).
1. **0 T gatemap + calibration** — DONE (runs 4 aborted/5): ratio c_bg/c_tg = 0.773, n_offset −0.089e12, D_offset
   −0.013 V/nm; absolute scale = 9.5 nm prior (unverified). Region B ridge offset 0.43e12 (series mosaic confound).
2. **Feasibility model table** — DONE (in measure md cells 39/41).
3. **SdH spot checks, D = 0** — DONE (run 6 n=+3.2, run 7 n=−1.2), read in ana 2026-08-23:
   e-side tones 7.3 / 14.6 / 22.3 / 29.6 T; 22.3 violates the harmonic hierarchy of 7.3 (stronger, earlier onset
   than 14.6) → likely independent; 7.3 + 22.3 ≈ 29.6 = QH-zero spacing → absolute n ≈ 0.90× nominal. h-side:
   broad 5–8 T + 12.3 T; unresolved. **Lean ABAB (weak)** — single density, 22.3 ≈ 3×7.4 coincidence unbroken.
4. **Landau fan at D = 0** — THIS STEP (run 8): B 1→10 T (91 rows, uniform in 1/B, F_nyq 50 T, dF 1.1 T) ×
   n −1.20→+3.20e12 (89 pts, D = 0 co-swept), ~4.3 h, ends at 10 T.
   Establishes: F_i(n) tracking (harmonic vs independent), F1+F2 = F_L(n) closure, LL crossing pattern,
   region-B ladder (converges to n_A ≈ −0.43), absolute n scale from QH-minima slopes.
   Checkpoints: first rows (1.0 T, levels vs runs 6/7 at 1 T); row ~45 (1.8 T) partial FFT for F1(n);
   row ~70 (3.3 T) F1(n), F2(n); full analysis at completion.
5. **Conditional — finite-D fan pair (±D)**, riding the magnet down from 10 T. Run if step 4 leaves ABAB vs ABCB
   open (two bands present) or ABCA vs ABCB open (gapped CNP); ±|D| symmetry is the ABCB test. Size after step 4.
6. **Conditional — LK T-dependence** (masses of F1/F2) if band identity needs m* (ABAB light/heavy ≈ 0.03/0.06 mₑ).
7. **Call** — final ana cell per the output contract.

## What would change my mind
- Fan FFT: the ~22 T tone tracks exactly 3×F1(n) for all n and fades with the hierarchy → it is a harmonic; then
  the e-side has one light pocket + full-density tone → re-open ABCA (trigonal/Lifshitz pockets) / ABCB.
- Single tone ≈ F_L(n) dominating at all |n| ≥ 1e12 with no independent light tone → ABCA.
- e/h asymmetric band count, or tones not closing to F_L(n) → ABCB or mosaic (region B) — check the region-B ladder first.
