# vti-02 stacking-order campaign — plan (recreated 2026-08-23, post-handoff)

**Goal:** ABAB vs ABCA vs ABCB call on vti-02 (tetralayer graphene), evidence-cited, per the
output contract. One wired pair (sr1 = B_1–B_2), so one region's verdict.

## Done

1. **Gate C liveness** — runs 0–3 (`gate-current-sanity-check`): all four wired contacts alive,
   no leakage inside the operating box. Ana cell 11.
2. **0 T gatemap** — run 4 (aborted: 20 µV railed on the high-|D| CNP ridge), run 5 (100 µV,
   clean). Ana cell 13.
3. **CNP + (n, D) calibration** — from run 5: c_bg/c_tg = 0.773 (data), c_tg anchored at the
   9.5 nm prior; n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex). `cal_run5.json`.
   Realized D = 0 window inside validators: n = −1.27 … +3.27e12. A second, parallel ridge
   (region B, doped by +0.43e12) exists — the voltage window is dominated by region A.
4. **SdH spot checks** — run 6 (electron n = +3.2e12, 0→10 T), run 7 (hole n = −1.2e12,
   10→0.3 T). Ana cells 14–16. Both sides oscillate from ≤ 0.7 T; electron side: light 7.1 T
   tone + 2–4× content (harmonics vs heavy subband unresolved at spot resolution); hole side:
   multi-band (4.7, 6.6, 12.3 ≈ F_full). Fan is feasible from low B; 10 T reaches the light
   pockets' quantum limit.

## Now

5. **Landau fan at D = 0** (`landau-fan`, this step): fast axis n = −1.25 → +3.20e12 (201 pts,
   Δn ≈ 2.2e10, TG+BG co-swept along the calibrated D = 0 line), slow axis B = 0 → 10 T in
   0.1 T (101 rows). What it establishes: (a) frequency-vs-n slopes → pocket degeneracies and
   subband populations (splits harmonics from genuine heavy pockets — harmonics scale with the
   parent, subbands have their own slope/intercept); (b) filling-factor sequence and gap
   structure fanning from the CNP → zero-LL degeneracy; (c) LL-crossing pattern → number of
   coexisting subbands vs n. These three are the stacking discriminators: ABAB = two
   bilayer-like subbands (light+heavy, crossings on both sides), ABCA = single heavy/flat band
   (one full-density fan, no inter-subband crossings at low |n|), ABCB = asymmetric mix
   (monolayer-like + trilayer-like signatures).
   **Change-of-mind triggers:** leak trip or T rise → interrupt; CNP column railing at 20 kΩ is
   accepted (gap evidence); if by B ≈ 2 T (row ~20) no Landau lines resolve in n, stop and
   re-grid (finer n or coarser B, higher bias).

## Next (contingent on the fan)

6. **D ≠ 0 discrimination** if the D = 0 fan is ambiguous: rhombohedral/mixed stackings gap at
   the CNP under D (run-5 ridge already shows R_CNP growing with |D|: 330 Ω → 2.9 kΩ at
   0.3 V/nm — consistent with a D-tunable gap, which pure ABAB does not produce at B = 0);
   a targeted fan or gap-vs-D map at fixed n = 0.
7. **T-dependence / LK masses** at chosen (n, B) points if masses are needed to separate
   candidates (T_e ≈ 8 K limits heavy-mass LK — price before committing).
8. **Close-out** — `return-to-initial` per the brief.
