# vti-02 stacking-order plan (rebuilt 2026-08-23 after handoff; the original lived only in the landed cell markdowns)

**Goal:** ABAB vs ABCA vs ABCB call (or calibrated "cannot tell") for the region seen by the
provided pair (source T_0, drain B_3, Rxx B_1–B_2). No Hall channel this cooldown → carrier
sign comes from gates; stacking read rests on SdH/LL structure vs (n, B) and its D-dependence.

## Done
1. **Gate C** — runs 0–3 (`gate-current-sanity-check`): alive, R peaks ≤ 330 Ω at D ≈ 0, leakage at
   noise floor (≤ ~0.1 nA excursions). ✔
2. **0 T gatemap + calibration** — run 5 (run 4 aborted, sensitivity rail lesson): CNP ridge →
   `cal_run5.json`: ratio c_bg/c_tg = 0.773, c_tg = 2.796 mF/m² (geometry prior scale),
   n_offset = −0.089×10¹², D_offset = −0.013 V/nm. ✔
3. **SdH spot checks** — run 6 (electron n = +3.2×10¹²: two incommensurate fundamentals 7.0 +
   29.9 T, onset ≤ 0.3 T); run 7 (hole n = −1.2×10¹²: multi-tone 4.7/5.3/6.6/8.5/12.3 T).
   Oscillations resolve at T_e ≈ 8 K; **ABCA disfavored** at |n| ≳ 1×10¹² (no single heavy
   pocket). Sum rule +12% vs cal → density scale to be self-calibrated by the fan. ✔

## Now
4. **Landau fan along D = 0** (run 8): fast n = −1.24 → +3.24×10¹² (113 pts, Δn = 0.04), slow
   B = 0.5 → 8 T, 190 rows uniform in 1/B (F_Nyq ≈ 51 T — keeps the 2×F_heavy ≈ 60 T alias at
   ~41 T, above all fundamentals ≤ 37 T). sr1 at 200 µV (20 kΩ FS — gapped CNP under field can
   greatly exceed the 0 T peak; rail lesson from run 4). ~9 h.
   **Analysis:** per-column FFT in 1/B → F(n) branches; fan image in (n, 1/B) → LL/filling-factor
   lines; dΣF/dn = h/4e recalibrates n scale.
   **Discriminators:** ABAB → two bilayer-like branches, both dispersing, F₁+F₂ = F_L(n),
   band-edge onsets symmetric-ish in n; ABCB → monolayer-like (linear, light, small-F) + heavy
   branch, distinct partition and LL-crossing pattern; ABCA → single branch at full F_L (already
   disfavored). Electron/hole asymmetry of branch structure is part of the fingerprint.
5. **If ambiguous:** D ≠ 0 fan or gatemap at fixed B (the D response of the low-energy bands
   differs strongly: rhombohedral/mixed stacks gap at D = 0 CNP differently than Bernal;
   band-edge Lifshitz features move with D). Also candidate: repeat fan segment at elevated T
   for mass tagging of branches (LK), honoring rig-card settling facts.
6. **Call** — final ana cell per the output contract (per-region verdict = the one wired pair).
7. **Close-out** — `return-to-initial` (field 0, gates 0, heaters off, readback).

## What would change my mind
- Fan shows a single branch carrying full F_L → re-open ABCA.
- Sum rule stays >10% off after slope self-calibration → revisit degeneracy assumption
  (broken symmetry) before assigning stacking.
- Leakage or contact death → stop, notify (rewiring is operator work).
