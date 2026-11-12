# vti-02 — stacking-order campaign plan (HERA, E1)

*Goal: ABAB vs ABCA vs ABCB, region-resolved (one contact pair: sr1 = B_1−B_2), evidence-cited. Reconstructed at handoff
(2026-08-23 ~05:20) from the measure/ana notebooks and the hera_scratch proposals — no plan.md existed on disk.*

## Discriminants (what each stacking predicts, transport-only)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| Fermi surface at fixed n, D = 0 | two pockets (light + heavy bilayer-like), F1 + F2 = F_L | one pocket, F = F_L (flat band, heavy) | two pockets (Dirac-like light + bilayer-like heavy), F1 + F2 = F_L, strongly e/h asymmetric |
| zero-energy LL degeneracy → first QH gaps | 8 + 8 = 16-fold → gaps at ν = ±8 | 4N = 16-fold → ν = ±8 | 4 + 8 = 12-fold → ν = ±6, asymmetric |
| LL crossings in the (n, B) fan | yes (two cyclotron masses) | no (single band, clean 4-steps) | yes |
| CNP gap vs D | small, ≈ symmetric in ±D, semimetal at D = 0 | large, symmetric, ∝ |D| | intrinsic gap at D = 0 (no inversion), asymmetric in ±D |

Confound carried from step 1: **two series regions** between B_1 and B_2 (ridge A = calibration region; ridge B parallel,
electron-doped by 0.43e12 raw). Every feature may appear twice, offset in n by −0.43e12 (raw scale).

## Steps

0. **Gate C liveness** — runs 0–3. DONE: alive, no leakage, Rxx 60–330 Ω, two CNP peaks per gate.
1. **0 T gatemap → CNP + (n, D) calibration** — runs 4 (railed, aborted), 5. DONE: c_bg/c_tg = 0.773 (data), c_tg anchored
   at the 9.5 nm prior (**absolute scale unverified**), n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex).
   D = 0 line inside validators: n_raw −1.27 … +3.27e12 (TG-limited both ends).
2. **SdH feasibility model** (mass table) — done by the previous instance in the step-3 markdown.
3. **SdH spot checks at D = 0** — run 6 (electron, n_raw +3.2e12, 0→10 T), run 7 (hole, n_raw −1.2e12, 10→0.3 T). DONE, read
   at handoff (ana cells landing): electron side tones 7.1 / 14.1 / 22.1 / 29.5 T. 22.1 and 29.5 are within the ~1.6 T FFT
   resolution of both "3×/4× harmonic" and "heavy pocket 22 T + sum 29 T". 29.5 T ≈ 0.89 × F_L(raw) — the high-B QH structure
   is periodic at F_L(true n), so the density scale is probably ~11 % high (c_tg, not c_bg, off the prior). Hole side: 4.7 +
   6.6 ≈ 11.3 T ≈ F_L at the rescaled density, messy (near-CNP + region B). Lean so far: two pockets at D = 0 → against ABCA,
   but scale-limited. Onset of SdH ≈ 1.0–1.4 T at T_e ≈ 8 K.
4. **Landau fan at D = 0** ← THIS STEP (operator-requested). n fast along the calibrated D = 0 line over the full window
   (−1.24 … +3.21e12 raw, 0.025 step, 179 pts), B slow: 0 T baseline row then 0.6 → 10.0 T at 0.2 T (49 rows). sr1 100 µV
   (10 kΩ FS). ≈ 4 h 20 m, ends at 10 T. Establishes: (i) absolute n scale from the fan-line slopes (ν = n h / eB → the lever
   arm, closing step 1's scale hole); (ii) the first-gap sequence around the CNP (±8 vs ±6, e/h symmetric or not);
   (iii) LL crossings present/absent; (iv) the region-B replica (fan lines converging to n ≈ −0.43e12 raw) — separates
   region-B features from crossings. Checkpoints: B = 0 row vs run 5's D = 0 cut; ~3 T (row ~13, ~1 h); ~6 T (row ~28, ~2.3 h).
5. **D-dependence at fixed high B** — ride the magnet down from 10 T after a (n, D) map at 10 T (or at ~6 T): the gap sequence
   vs D — symmetric/large (ABCA), small/semimetal (ABAB), asymmetric intrinsic (ABCB). Sized after step 4 (n window near
   the CNP only, |D| ≤ 0.3 V/nm, ~1.5–2 h).
6. **Optional: LK temperature ladder** at one electron-side spot for the two masses (only if the pocket partition is the
   deciding evidence and step 4/5 leave it ambiguous). ≤ 100 K, `set_both(T, 0.95)`.
7. **Call** in the ana notebook (per-region verdict / evidence / hedges), then `return-to-initial` close-out.

## What would change my mind

- Fan shows a single clean 4-step LL sequence with no crossings and F = F_L → ABCA (the two-pocket read of run 6 was harmonics).
- First gaps at ν = ±6 with strong e/h asymmetry, or a D = 0 gap that grows asymmetrically in ±D → ABCB.
- Fan-line slopes give n_true ≠ 0.89 × n_raw → re-derive every frequency ratio before reading pocket partitions.
- Region-B replica lines coincide with what looks like a crossing → not a crossing; discount.
- Rail at the CNP at high B (> 10 kΩ) is informative (insulating ν = 0), not a fault — do not re-run at a coarser sensitivity.
