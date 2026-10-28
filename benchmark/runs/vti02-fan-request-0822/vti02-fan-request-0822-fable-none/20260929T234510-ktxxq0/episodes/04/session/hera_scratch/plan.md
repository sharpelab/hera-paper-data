# vti-02 stacking-order campaign — plan (rewritten 2026-08-23, post-handoff)

*(Note: this file was missing at handoff — reconstructed from the notebooks and
session_notes. Steps 0–3 are done; state below reflects data on disk.)*

**Goal:** ABAB vs ABCA vs ABCB call on vti-02 (tetralayer graphene), region-resolved
(one wired pair: sr1 = B_1–B_2), evidence-cited, per the output contract.

## Done

0. **Bring-up + gates A/B/C** — setup + SAFETIES operator-run; VERIFY ALL GREEN
   (measure cell 32); liveness `gate-current-sanity-check` runs 0–3 (gates quiet,
   R(0) ≈ 70–330 Ω).
1. **0 T gatemap** (runs 4 aborted / 5 good) → `cnp-and-dline-calibration`:
   ratio c_bg/c_tg = 0.773, n_offset = −0.089×10¹², D_offset = −0.013 V/nm
   (scale = geometry prior; `hera_scratch/cal_run5.json`). Single CNP ridge, gap
   opens with |D| — consistent with all three stackings; not discriminating.
2. **SdH spot checks at D = 0** — run 6 (n = +3.2×10¹², B 0→10 T): high-B F ≈ 33.3 T
   ≈ F_full(4-fold); low-B ladder 7.1/14/22/29.5 T. Run 7 (n = −1.2×10¹², 10→0.3 T):
   F ≈ 20 T > F_full = 12.4 T ⇒ compensated e+h pockets. Multi-band low-energy
   structure confirmed; onsets 0.3–0.7 T.

## Now

3. **Landau fan at D = 0** (operator-requested, this is the stacking discriminant):
   fast n = −1.2 → +3.2×10¹² (111 pts, Δn = 0.04) co-swept (Vtg, Vbg) along the
   calibrated D = 0 line; slow B = 0.5 → 10 T, 50 mT (191 rows). sr1 100 µV
   (10 kΩ FS). ~9 h. Establishes: LL filling sequence (steps of 4 vs 8 vs mixed),
   F(n) branch slopes, gap-closing/crossing pattern vs stacking model:
   - **ABAB**: two bilayer-like bands share n → two SdH branches, F_l + F_h = n·h/4e;
     compensated pockets near CNP; LL crossings between the two ladders.
   - **ABCA**: one heavy 4-fold band carries all n → single branch at F_full;
     strong symmetry-broken states / ν=0 insulator likely at high B.
   - **ABCB**: monolayer-like Dirac + heavy band → one √B-anomalous ladder + one
     heavy ladder, distinctive crossing pattern.
   Checkpoints: first 2–3 rows (rail/leak/dead channel), then ~hourly via the armed
   hera-watch digest; interim fan re-form at ~3 T and ~6 T (continue/adjust/abandon).
4. **Fan analysis**: re-form grid, per-n FFT (F vs n branch map), LL-minima filling
   assignment (ν vs n·h/eB), compare the three stacking templates → verdict draft.
5. **Contingent** (only if the D = 0 fan is ambiguous): short D ≠ 0 fan or a ν-vs-D
   cut at fixed B to separate ABCB (layer-asymmetric) from ABAB; or a T-dependence
   (LK mass) on the dominant branch. Priced when reached.
6. **Close-out**: output-contract cell in ana (per-region verdict, evidence, hedges),
   then `return-to-initial` (B→0, gates→0, heaters off, readback → session_notes).

## What would change my mind / kill criteria

- Fan first rows rail or gates leak (>1 nA) → abort, resize sensitivity or window.
- No fan-line structure resolvable by ~3 T despite runs 6/7 → Δn too coarse; stop,
  re-grid finer over a narrower n window.
- F(n) branches inconsistent with all three templates → consider domain mixing under
  the measured pair (region-resolved caveat in the verdict; only one pair is wired).
