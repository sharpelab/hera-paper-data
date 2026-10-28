## Runs 6–7 — SdH spot checks (`sdh-spot-check`), D = 0: electron n = +3.2×10¹² (0→10 T) and hole n = −1.2×10¹² (10→0.3 T)

Raw MR first (top), then the 1/B FFT (bottom). Onset comes from `sdh_onset` on the uniformly sampled part of each record. In run 6 that means B ≥ 1 T; below 1 T the 50 mT grid aliases the 7 T tone.

**Read, electron side (run 6), F_L = 33.1 T:** there are oscillations. The resolved tones are **7.3 T** (strongest, and still above threshold at the 1.0 T edge of the record, so its onset is < 1 T), **22.3 T** (onset 1.40 T) and **29.4 T** (onset 1.76 T), plus 14.8 T. Above ~3 T the QH minima turn sharp and their harmonics (43.7, 58.6, 88, 130 T) make everything above 5 T harmonic-rich. The screen marks everything as a comb of 7.3 T (3× = 22, 4× = 29.4), but the recipe warns about exactly this. The ABAB model at scale 1 gives **7.31 / 25.78 T**. The measured light tone matches it, and 7.3 + 22.3 = **29.6 ≈ the 29.4 T tone**. So {7.3, 22.3} is a candidate ABAB pair whose sum sits at 29.5 T, which would imply a density scale ≈ 0.89. On that reading the 29.4 T tone is either a sum/breakdown orbit or an ABCA-domain singleton at F_L. **Fork, unresolved at one density:** "ABAB pair + sum tone at scale 0.89" vs "one 7.3 T tone plus its harmonics".

**Read, hole side (run 7), F_L = 12.4 T:** tones at 6.6 T (onset 0.71 T), 4.7 T, 8.5 T and 12.3 T. This density is in the recipe's near-CNP hole exception regime: the model ABAB pair is 5.9 / 6.5 T, close and balanced. That makes it a **preview only**. Also, its 12.3 T tone sits at F_L on scale 1.0, while the electron-side sum sits at scale 0.89. One global scale can't fit both "F_L-tone" readings, so the scale has to be pinned independently.

**Take → the fan (investigation Step 4):**
- **Side: electron.** On the hole side the D = 0 line ends at −1.27×10¹² (TG −0.3 V limit, fixed), so that side never leaves the exception regime.
- **Density window: n = 1.6 → 3.2×10¹².** Across it the ABAB heavy/light ratio should move ≈ 6 → 3.5. A harmonic comb keeps a fixed 3×. The two readings differ in n-dependence, not at any single density.
- **High-field rows.** The QH ν-rays (n = ν·eB/h) pin the absolute density scale. That settles the 0.89-vs-1.0 question independently of the tone set.
