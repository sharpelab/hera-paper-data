# vti-02 stacking call — plan

*(Rebuilt 2026-08-23 by the incoming instance: the file was not on disk at handoff.
Steps 0–3 reconstructed from the notebooks + session_notes; step numbers match the
citations in measure cells 35/39/41.)*

Goal: ABAB vs ABCA vs ABCB for vti-02, region-resolved (one hardwired pair, B_1–B_2 on sr1),
or a calibrated "cannot tell".

## Done
- **0. Gate C** — runs 0–3 (`gate-current-sanity-check`): alive, no leakage, Rxx 60–330 Ω,
  two series CNPs (regions A and B).
- **1. 0 T gatemap + calibration** — run 5: ridge A slope → c_bg/c_tg = 0.773; c_tg at the 9.5 nm
  prior (absolute n-scale **not yet** data-calibrated); n_offset −0.089e12; D_offset −0.013 V/nm
  (R_CNP(D) vertex). Region B: parallel ridge, electron-doped by 0.43e12 relative to A (a series
  confound). Ridge-A R_CNP grows 240 Ω → 2.4 kΩ by D ≈ 0.3 V/nm (a D-tunable gap; not a stacking read on its own).
- **2. Feasibility model** (prior instance, in cell 39 md): at n = +3.2e12 F_L = 33.1 T; ABAB pair
  ≈ 7.5 / 25.6 T (m* 0.028 / 0.061), ABCA singleton 33.1 T (m* 0.074). At n = −1.2e12 F_L = 12.4 T;
  ABAB ≈ 5.3 / 7.1 T; ABCA m* ~ 1 (LK-dead).
- **3. SdH spot checks** — run 6 (n = +3.2e12, 0→10 T), run 7 (n = −1.2e12, 10→0.3 T).
  Run 6: deep minima (R → 1–4 Ω) from 1.5 T, minima at ν_nom ≈ 89, 72, 67, 54, 49, 41, 36, 31, 22, 18
  (irregular, not a 4-spaced ladder → more than one LL family or LL crossings). FFT: 7.1–7.5 T plus
  22–30 T content; sdh_onset reads 14/22/29.5 T as harmonics of 7.1, but a 7.4 T comb with a
  non-sinusoidal waveform and two independent bands (ABAB 7.5 + 25.6) are **not separable in a
  single trace** (resolution ~2.5 T, no n-dependence). Run 7: tones 4.7, 6.6, 8.5, 12.3 T;
  onset down to 0.7 T.

## Next
- **4. Landau fan at D = 0 (region-A calibration)** ← now. n fast −1.25 … +3.25e12 (the full D = 0
  window inside the validators), Δn = 0.03e12 (151 pts); B slow 1.25 → 10 T, uniform in 1/B
  (Δ = 0.007 T⁻¹) to 5 T then 0.2 T steps to 10 T (112 rows). ~7.5 h.
  Establishes:
  (a) tone map F(n) from per-column 1/B FFT — number of independent Fermi surfaces, their dF/dn,
      and the sum rule ΣF_i = F_L(n);
  (b) harmonic vs independent: a harmonic of F1 has dF/dn = k·dF1/dn; an independent band does not;
  (c) absolute density scale — QH-minimum slopes dn/dB = ν e/h calibrate c_tg (currently the prior), which
      the sum rule needs;
  (d) LL-crossing pattern (ABAB's two bilayer-like families cross; ABCA gives one family, plus F_L/3
      trigonal-warping pockets at low |n|);
  (e) the region-B series family: lines converging on n_A ≈ −0.43e12, not on the CNP → identified
      and excluded from the band read.
- **5. (conditional) D-dependence** — decided after step 4: a fixed-B (n, D) map or a D ≠ 0 fan riding
  the magnet down from 10 T. LL crossings that move with D (ABAB layer-polarisation), a large
  D-gap (ABCA), or R_CNP(D) / LL-pattern asymmetry in ±D (ABCB is polar — note that D_offset was
  *defined* by R_CNP(D) symmetry, so the geometric offset, +0.013 V/nm raw, is the ABCB-relevant
  number).
- **6. (conditional) LK masses** — only if step 4 leaves ABAB-heavy (25.6 T, 0.061) vs ABCA (33 T,
  0.074) ambiguous: elevated-T B-sweeps at one or two n (≤ 20 K, set_both ratio 0.95).
- **7. Call** in ana (per-region verdict, evidence, hedges) → close-out `return-to-initial`.

## What would change my mind
- Two independent tones with ΣF = F_L(calibrated) and fractions roughly fixed across n, plus
  crossing LL families → ABAB.
- One tone at F_L across the electron side (and F_L/3 pockets at low |n|) with a single LL family → ABCA.
- Tones that don't close the sum rule after the step-4c density calibration, or a strong ±D asymmetry
  → ABCB or mosaic; region-B lines that don't converge at −0.43e12 → rethink the series picture.
- All content harmonic of one fundamental that tracks F_L/k with no second family → a
  degeneracy-lifting pattern, not two bands; reopen.
