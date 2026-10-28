# vti-02 stacking-order plan (ABAB / ABCA / ABCB)

*Written 2026-08-23 05:30 by the incoming HERA instance. The previous instance ran
steps 0–3 without a plan.md on disk; they are recorded here after the fact from the
notebooks, session_notes and data/0–7.*

One measured region: the only wired pair is sr1 = B_1–B_2 (source T_0, drain B_3,
hardwired). The run-5 map shows two parallel CNP ridges in series (A dominant;
B electron-doped by 0.43e12 relative to A). So "region" = the B_1–B_2 pair, with a
series-mosaic confound: region-B tones appear at n×(1+0.43/n).

## Discriminants (what each stacking predicts)
- **ABAB (Bernal)**: two bilayer-like bands (light + heavy), so two SdH tones at every n
  with F₁ + F₂ = F_L(n), each ∝ n, and a non-integer ratio that drifts slowly with n.
  Two interpenetrating LL families, so LL crossings appear in the fan. D mixes the bands:
  the crossing pattern moves with D, and the CNP gap is weak.
- **ABCA (rhombohedral)**: one low-energy band (flat, ~p⁴), so one tone F = F_L at
  moderate/high n and a single LL family without crossings at D = 0 away from the CNP.
  D opens a large CNP gap (R_CNP grows by orders of magnitude). Heavy mass near the CNP.
- **ABCB (mixed)**: no inversion symmetry, so the response is D-asymmetric (the CNP
  gap/LL pattern is not ±D symmetric about the true D = 0). Multi-band (two tones,
  different ratio from ABAB).

## Steps
0. Bring-up / VERIFY / E1 grant. **Done** (session_notes).
1. Gate C liveness, runs 0–3. **Done**: alive, no leakage, Rxx 60–330 Ω.
2. 0 T gatemap + `cnp-and-dline-calibration`, run 5. **Done**: c_bg/c_tg = 0.773 (data);
   c_tg = geometry prior (absolute n scale uncalibrated); n_off −0.089e12; D_off −0.013
   V/nm (R_CNP(D) vertex). R_CNP grows 300 Ω → 2.4 kΩ at D = 0.25 V/nm (moderate).
   Hedge: D_off was *defined* by ±D symmetry, so the map cannot test ABCB asymmetry
   except through the small raw-vertex offset (+0.013 raw).
3. SdH spot checks at D = 0, runs 6 (n +3.2) and 7 (n −1.2). **Done**: electron side has
   a light tone 7.1 T (onset < 0.3 T) plus a heavy 4-fold ladder (F ≈ 30 T, 0.91 of
   calibrated n); F₁ + F₂ ≈ 1.12 F_L. The hole side is multi-tone and irregular. Not a call.
4. **D = 0 Landau fan** (run 8, current step). Rxx along the D = 0 line
   n ∈ [−1.2, +3.2]e12 (101 pts, fast) × B 0.5 → 10 T (121 rows, slow: 1/B-uniform
   0.5–5 T, 0.25 T steps 5–10 T). Establishes:
   (a) the tone count and F_i(n) per column; the sum rule F₁ + F₂ = F_L vs integer ratios;
   (b) the absolute lever arm from QH-minimum slopes in (n, B) (dn/dB = ν·e/h), which
       also fixes whether the 12 % overshoot in step 3 is calibration;
   (c) whether LL crossings are present (two families) or absent (one family);
   (d) the low-B light-band fan: do the minima track total n (one band) or a fraction
       of it (a sub-band)?
   ~5.5 h, ends at 10 T.
5. **Finite-D test** (after 4; riding the magnet down from 10 T). Either an Rxx(n, D) map
   at fixed high B (~8 T) over the reachable D window, or a fan at D ≈ ±0.2 V/nm on the
   ride down. Tests the D-response: ABAB crossings shift with D, ABCA gaps, ABCB ±D
   asymmetry. The choice depends on what step 4 shows.
6. (Optional) T-dependence of the SdH amplitude at one n (LK masses m₁, m₂). Only if
   steps 4–5 leave ABAB vs ABCB ambiguous. The rig's T_e ≈ 8 K limits it.
7. Call in ana (output contract) → close-out `return-to-initial`.

## What would change my mind
- A single tone at F_L for all n with no crossings, and the light tone following k×
  harmonics of it → ABCA (despite steps 2–3).
- F₁/F₂ locked at an integer ratio across n → harmonics, not two bands.
- Tones that do not extrapolate to n = 0 on ridge A's calibration but do on ridge B's
  (+0.43e12) → a mosaic artifact, not band structure.
- Strong ±D asymmetry in step 5 → ABCB over ABAB.
