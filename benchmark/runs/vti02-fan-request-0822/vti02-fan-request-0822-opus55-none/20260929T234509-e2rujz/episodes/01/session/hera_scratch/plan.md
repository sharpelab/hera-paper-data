# vti-02 — stacking-order plan (ABAB / ABCA / ABCB)

*Written 2026-08-23 by the picking-up instance (the prior instance left no plan.md; steps 0–3
reconstructed from the notebooks, cells 33–42 measure / 10–13 ana).*

Contact pair: one — sr1 = B_1–B_2 (source T_0, drain B_3). One verdict line owed.
Calibration (run 5, region A ridge): c_bg/c_tg = 0.773 (data), c_tg = 2.796e-3 F/m² (9.5 nm PRIOR —
absolute density scale unverified), n_offset −0.089e12, D_offset −0.013 V/nm (from R_CNP(D) vertex —
assumes the minimum sits at D = 0, which a polar ABCB would violate; hedge).
Region B: parallel CNP ridge, electron-doped by 0.43e12 vs A — series-mosaic confound inside the pair.

## Discriminators (coarse TB model, hera_scratch/tb_model.py, D = 0; m*=0 rows are filled pockets, ignore)
| stacking | Fermi surfaces (fraction of n) | m*/me | fan fingerprint |
|---|---|---|---|
| ABAB | two: ≈0.26 light + ≈0.73 heavy (e); ≈0.31 + 0.68 (h) | 0.025 / 0.06 | two LL families crossing (diamond grid); F_l + F_h = F_total; ratio ≈2.6–2.9 e, ≈2.2 h, NOT integer |
| ABCA | one dominant ≈0.9–1.0 (e high n); trigonal pockets near CNP | 0.07–0.3 (heavy) | single family, heavy mass → weak low-B SdH; big D-gap; ν=0 insulator |
| ABCB | one dominant ≈0.9 + tiny light pocket ≈0.02–0.07 | 0.06–0.1 / ~0.01 | single dominant family; ±D asymmetry, possible D hysteresis (polar) |

## Steps
0. **Gate C** (runs 0–3) — DONE: alive, no leakage; two R maxima per gate.
1. **Gatemap + cal** (run 5; run 4 railed/aborted) — DONE: ridge A strongly D-gapped (240 Ω → 2.4 kΩ at D +0.25 V/nm).
   Only one sign of D well covered (−0.08…+0.30); ±D symmetry is unmeasured beyond |D| 0.08.
3. **SdH spot checks** (run 6 e n=+3.2, run 7 h n=−1.2, D = 0) — DONE (analysis hera_scratch/ana_sdh67.py):
   e: tones 7.2, 22.2, 29.5 T (+14.1); >4 T single 33 T. h: 3.5, 8.5, 12.3 T (+6.8 = 2×3.5).
   Pattern "two tones + their sum" on both sides → ABAB-like; confound on e-side: 22.2 ≈ 3×7.2 (harmonic).
   Implied scale: F_total tones give n_true ≈ 0.92 (n_prior − 0.095e12) — prior c_tg ~8 % high. UNVERIFIED.
4. **Landau fan, D = 0, full n** (NOW). n −1.20…+3.20e12 (111 pts, 0.04), B 0.8→8 T uniform 1/B (113 rows,
   Δ(1/B)=0.01), ends at 8 T. Establishes: (a) absolute density scale from QH-minimum slopes (dn/dB = νe/h,
   gate-cal-free) → corrected F_L(n); (b) per-column FFT → F_i(n) tracks: two independent linear families with
   n-varying, non-integer ratio summing to F_total = ABAB; one dominant family at ≈F_total = ABCA/ABCB;
   (c) LL-crossing pattern in the 2D image (ABAB diamonds) vs single fan; (d) region-B replica shifted by −0.43e12.
   Checkpoints: rows 0–3 (signal, rails, gate currents, path); row ~20 (0.95 T, light-band LLs visible?);
   row ~58 (1.5 T, partial FFT: light/heavy tones and ratio vs n); row ~100 (4 T, QH minima → scale).
5. **D-dependence at fixed high B** (conditional, from 8 T where the fan ends): n–D map or ±D cuts at fixed n —
   ABAB: LL crossings move with D, no big gap at CNP; ABCA: strong symmetric gap; ABCB: ±D asymmetry/hysteresis
   (sweep D up and down). Also settles D_offset hedge.
6. **LK mass check** (only if 4 leaves harmonic-vs-two-band ambiguous): T-dependence of the light vs heavy tone
   amplitudes at one n (two masses 0.025/0.06 = ABAB; harmonics decay as k·m*).
7. **Close-out** (return-to-initial) per brief.

## What would change my mind
- Fan F_i(n): the ~0.25 tone's partner sits at exactly 2× or 3× everywhere (incl. hole side) and no independent
  line family in the 2D image → single band + harmonics → not ABAB; then ABCA vs ABCB via step 5.
- Hole-side ratio ≈2.2 and e-side ≈2.7 persisting, with F_l+F_h = F_total at every n → ABAB strong.
- Region-B replica carrying a different tone set → region-split verdict (mosaic), hedge the single-pair call.
