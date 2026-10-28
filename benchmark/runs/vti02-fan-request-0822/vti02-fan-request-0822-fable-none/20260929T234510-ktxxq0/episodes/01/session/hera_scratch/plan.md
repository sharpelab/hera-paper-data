# vti-02 stacking-order campaign — plan (rebuilt at handoff, 2026-08-23)

Goal: ABAB vs ABCA vs ABCB, region-resolved, evidence-cited (output contract in the brief).
E1 engaged (session_notes 2026-08-22). Calibration: run 5 → ratio c_bg/c_tg = 0.773,
c_tg = 2.796e-3 F/m² (geometry-anchored), n_offset = −0.089e12, D_offset = −0.013 V/nm
(`hera_scratch/cal_run5.json`). D = 0 window inside validators: n = −1.27 … +3.27e12.

## Done

1. **Gate C liveness** — runs 0–3 (gate-current-sanity-check): contacts alive, leakage pA-scale. ✔
2. **0 T gatemap + calibration** — run 5 (run 4 aborted, sensitivity rail): one dominant CNP
   ridge (A) + faint parallel mosaic ridge (B, +0.43e12 electron-doped); D-tunable gap on
   ridge A (240 Ω at D≈0 → 2.4 kΩ at |D|≈0.25 V/nm). ✔
3. **SdH spot checks** — run 6 (e, n=+3.2e12): light tone 7.1 T + 2–4× harmonics, content
   near 30 T unresolved (heavy fundamental 25.6 T vs 4×7.1 = 28.4 T needs dF < 3 T).
   Run 7 (h, n=−1.2e12): multi-tone low-|n| regime, strongest 12.3 T ≈ F_L. Ana cells 14–15. ✔

## Now

4. **Landau fan along D = 0** (`landau-fan`) — the stacking discriminator. Fast: n −1.25 →
   +3.25e12, 91 pts (0.05e12), co-swept (TG, BG) on the calibrated D = 0 line. Slow: B 1 → 10 T
   uniform in 1/B, 140 rows (Δ(1/B) = 6.5e-3 → F_Nyq = 77 T; FFT dF = 1.11 T — separates
   25.6 from 28.4 T). sr1 200 µV (20 kΩ FS; CNP column at high B may rail — accepted, itself
   a gap read). Ends at 10 T, gates parked at 0. ≈ 6 h.
   **Reads that decide:** (a) # of fundamental branches vs n and their dispersion
   dF/dn (harmonics stay integer-locked to parents; fundamentals disperse);
   (b) partition F_light(n) + F_heavy(n) vs F_L(n) = 10.34·n[1e12] T (two-band ABAB
   sum rule) vs a single branch at F_L (ABCA) vs an asymmetric/gapped hybrid (ABCB);
   (c) CNP column R(B) at D = 0 — gap growth with B;
   (d) electron/hole asymmetry of the fan.
   **What changes my mind:** a single dominant branch tracking F_L(n) → ABCA lean; three+
   independently dispersing fundamentals or strong e/h asymmetry with intrinsic CNP gap → ABCB;
   two branches summing to F_L → ABAB.

## Next (contingent on the fan)

5. **Mass spot checks (LK ladder)** at the fan's branch-resolved (n, B) points — masses tag
   the bands (ABAB pair m* ≈ 0.028/0.061; ABCA ≈ 0.074+ at this n). Elevated-T protocol per
   rig card (set_both ratio 0.95, hover acceptance). Only if the frequency read is ambiguous
   or needs corroboration.
6. **D ≠ 0 fan or gap-vs-D 1D cuts** — ABCA/ABCB gap responds strongly to D at CNP; ABAB
   opens a layer-polarized gap too but with distinct magnitude/asymmetry. Cheap 1D R_CNP(D, B)
   cuts may substitute.
7. **Verdict + output contract** in ana; then close-out (`return-to-initial`).

## Standing cautions

- Region-B mosaic tones at ×1.13 n contaminate FFT columns — check candidate extra
  branches against a 13 % density offset before calling them bands.
- Absolute n scale is geometry-anchored (c_tg prior); the fan's F_L(n) slope closure is
  itself the lever-arm check — if Σ F ≠ F_L·n consistently, revisit calibration before
  reading physics into it.
- T_e ≈ 8 K: heavy masses (≳0.1 mₑ) are LK-killed; absence of a heavy branch is weak
  evidence only.
