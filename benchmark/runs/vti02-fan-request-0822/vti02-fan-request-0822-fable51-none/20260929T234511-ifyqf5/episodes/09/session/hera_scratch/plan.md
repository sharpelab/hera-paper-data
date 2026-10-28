# vti-02 stacking-order campaign — plan (HERA, written 2026-08-23 ~05:30, second instance)

Goal: ABAB / ABCA / ABCB / cannot-tell for the one measured pair (sr1 = B_1−B_2), evidence-cited.
Discriminator: the Landau-level structure in a (n, B) fan at D = 0 — (a) the zero-energy LL degeneracy
(first gaps from the CNP: ν = ±8 bilayer-like, ±16 ABCA / two-bilayer ABAB, mixed set for ABCB),
(b) the number of Fermi pockets at finite n (ABAB: two bilayer-like pockets → two line families with
distinct per-pocket ν; ABCA: one family; ABCB: a light Dirac-like pocket + a heavy one), (c) how the
gaps evolve with D (fan 2).

## Done (previous instance)
1. Gate C runs 0–3: alive on the provided pair, no leakage (pA floor), Rxx 60–330 Ω at B = 0.
2. Gatemap run 5 (run 4 aborted, railed): two parallel CNP ridges (region A dominant, region B
   electron-doped by 0.43e12 — series mosaic confound). Calibration (cal_run5.json): c_bg/c_tg = 0.773
   (data), c_tg = 2.796 mF/m² (9.5 nm prior — absolute n scale still a prior), n_offset −0.089e12,
   D_offset −0.013 V/nm from R_CNP(D) symmetry. D = 0 line inside validators: n = −1.27 … +3.27e12.
3. SdH spot checks at D = 0: run 6 (n = +3.2e12, 0→10 T, 10 mT), run 7 (n = −1.2e12, 10→0.3 T, 20 mT).
   My read (hera_scratch/sdh_spot_runs6_7.png): run 6 has QH minima to Rxx ≈ 0 at ~2.3, 3.4, 4.2, 6.0,
   7.2 T and a 530 Ω hump 8–10 T; tones 7.1 T (dominant, onset < 0.3 T) + 14.1 / 22.1 / 29.5–30 T.
   Either ABAB two pockets (model 7.5 / 25.6 T — observed 7.1 / ~30, sum 37 vs F_L 33: a ~10 % n-scale
   error would fit) or one pocket F_L ≈ 30 T with F_L/2, F_L/4 subharmonics (every 4th gap deep).
   Run 7: tones 12.3 T (≈ F_L 12.4, SNR 124), 6.6, 4.7, 8.5, 9.4; minima at ~2.0, 3.4, 4.6, 5.8, 7.3 T.
   Spot checks cannot separate "two pockets" from "one pocket + subharmonics" — the fan can.

## Next
4. **landau-fan #1, D = 0 (this step).** Fast: (Vtg, Vbg) co-swept along the calibrated D = 0 line,
   n = −1.25 … +3.25e12, 151 pts (0.03e12; TG −0.291 … +0.998 V, BG −0.484 … +1.185 V). Slow: B
   1.0 → 3.8 T at 0.2 T (15 rows) then 4.0 → 10.0 T at 0.1 T (61 rows); 76 rows, 11 476 pts. Uniform
   in B because LL lines are straight in (n, B); coarse below 4 T where ν lines are dense anyway
   (ν = 4 spacing = 4 fast steps at 1 T), fine above where the ν assignment is made (ν = 1 → 8 steps at
   10 T; window covers ν −5 … +13 at 10 T, −10 … +27 at 5 T). sr1 fixed 200 µV = 20 kΩ FS (a rail only
   at ν = 0 at high B, not diagnostic). fast_delay 1.0 s (≈ 1.0 s/pt measured, run 5), slow_delay 3 s.
   Price 4.6 h (+10 % → ~5.1 h), ends at 10 T with gates parked at 0.
   Establishes: LL line intercepts (region A vs B CNPs), ν sequence on both sides, pocket count.
   Checkpoints: first 2 rows (signal, no rail, gate current pA, T); ~every 1–1.5 h re-form partial fan
   (fan_grids) — abandon if featureless or railing across the window.
5. **Land runs 6/7 + fan analysis in ana** (raw → FFT/onset → take), while the fan runs.
6. **Fan #2 riding 10 → 1 T** — choice depends on fan #1: finite D (D ≈ +0.15–0.25 V/nm, where the
   gatemap ridge is gapped: gap-vs-D and LL crossings separate ABAB from ABCB) or, if fan #1 is
   ambiguous on the hole side, a denser hole-side fan. Never re-traverse: fan 2 descends.
7. **Call** in ana (output contract), then `return-to-initial` close-out on operator ask.

## What would change my mind
- Fan #1 shows two line families with different slopes converging on one CNP → two pockets (ABAB-like);
  one family with alternating gap depth → subharmonics (ABCA-like); a ν = ±2/±4 Dirac-like family on top
  of a heavy family → ABCB candidate.
- If the first gap from the CNP at 10 T is at |ν| = 8 on both sides, ABAB (two bilayer-like zero modes
  split by interlayer coupling) vs ABCA (16-fold) is settled by the ν = ±12 presence/absence.
- Region B (n offset +0.43e12) will add a second intercept; lines not extrapolating to n = 0 are B's.
- T_e ≈ 8 K on this rig: absence of odd/symmetry-broken ν is not evidence.
