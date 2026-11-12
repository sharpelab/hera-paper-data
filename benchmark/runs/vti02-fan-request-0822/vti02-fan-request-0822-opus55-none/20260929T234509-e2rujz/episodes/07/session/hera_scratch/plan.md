# vti-02 stacking call — plan (HERA)

*Written 2026-08-23 05:25 at instance handoff. The previous instance's plan was never written to disk.
Steps 0–3 are rebuilt here from the notebooks; step numbers match the ones cited in the measure markdown.*

Goal: ABAB vs ABCA vs ABCB for tetralayer vti-02, per contact pair (only one voltage pair is wired, B_1−B_2 on sr1),
with evidence citing data/<id> + calibrated confidence.

## Done
- **0 — Gate C** (runs 0–3): alive, no leakage, Rxx 60–330 Ω. Two series CNPs (regions A, B).
- **1 — 0 T gatemap + calibration** (run 5; run 4 aborted for a rail): ratio c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m²
  (**geometry prior, absolute scale unverified**), n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex).
  Parallel ridge B is electron-doped by 0.43e12 relative to A. It is a series mosaic and can put ghost tones at n + 0.43e12.
  The CNP resistance is D-tunable (240 Ω → 2.4 kΩ at D ≈ 0.25 V/nm). This does not settle the stacking by itself.
- **2 — Feasibility (model)**: at n = +3.2e12, F_L = 33.1 T. ABAB gives a pair ≈ 7.5 / 25.6 T; ABCA gives a single ≈ 33 T.
- **3 — SdH spot checks at D = 0** (run 6 e-side n = +3.2e12, 0→10 T; run 7 h-side n = −1.2e12, 10→0.3 T):
  there are strong oscillations on both sides, and the light tones persist to ≲ 1 T.
  Run 6 FFT (2–10 T, ΔF ≈ 2.5 T): 30 T (strongest), 7.5 T, 22.5 T, 15 T.
  Run 7: 5–7 T, 12.3 T (≈ F_L 12.4 T under the prior lever arm).
  So far this is only a preview. The 7.5 + 22.5 ≈ 30 T split looks like ABAB, but F_L is prior-scaled, so the 30 T peak could also
  be the full-density ABCA tone if c_tg is ~10 % low. The fan must fix the absolute lever arm from QH slopes.

## Next
- **4 — Landau fan at D = 0** (run 8): B slow 1→10 T (uniform in 1/B from 1 to 4 T, 85 rows; 0.15 T steps from 4.15 to 10 T, 40 rows)
  × n fast along D = 0, from −1.25 to +3.25e12 at 0.03e12 (151 points). fast_delay 0.6 s. Priced ≈ 5.2–5.75 h. Ends at 10 T.
  Establishes:
  (a) the **absolute lever arm** from the QH-minimum slopes, dn/dB = ν e/h, which gives F_L(n);
  (b) **F(n) per column**, i.e. the frequency-vs-density map, ΔF ≈ 1.1 T over 1–10 T, with a Luttinger-sum check;
  (b) is the primary discriminator:
      - ABCA: one family, F = F_L above the trigonal-warping Lifshitz point. Below it: F_L/3, with 12-fold degeneracy.
      - ABAB: two families with F_light + F_heavy = F_L. F_light/F_L ≈ 0.2–0.25 on the electron side.
      - ABCB: two families with a different partition, plus a strong e–h asymmetry.
  (c) the **QH sequence near CNP and the LL crossings**. Crossings between two LL families point to ABAB/ABCB.
      A crossing-free 4-fold ladder beyond ν = ±8 points to ABCA.
- **5 — Finite-D fan, riding the magnet down 10 → 1 T** (priced after step 4). It will sit at |D| ≈ 0.15–0.2 V/nm on one or both signs.
  The ABCA LL spectrum and gap are strongly D-dependent (layer-polarized). ABAB changes only mildly. ABCB is polar,
  so its response to ±D is asymmetric. Only needed if step 4 leaves ABAB vs ABCB or ABCA ambiguous.
- **6 (optional) — LK mass at 2–3 densities** from T ≤ ~20 K. ABAB light and heavy masses are ≈ 0.03 / 0.06 mₑ at n ≈ 3e12;
  ABCA has a single heavier mass. Only if F(n) is ambiguous.
- **7 — Call** in the ana notebook, per the output contract.

## What would change my mind
- Suppose the fan lever arm moves F_L by ≳ 10 % from the prior, and the 30 T tone then matches F_L with no partner summing to it.
  Then the ABAB lean from run 6 flips toward ABCA.
- If the tones are ghost-shifted by the ridge-B mosaic (a copy at ×(n+0.43)/n), each tone pair has to be checked
  against that before it is called as a second band.
- If Rxx goes negative, a Hall admixture is present: B_1−B_2 is not a clean longitudinal pair (run 6 reached −33 Ω at 6 T).
  That affects the QH-minimum depths, not the frequencies.
