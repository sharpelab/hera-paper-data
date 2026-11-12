**Read — electron (run 6, n = +3.2):**
- The dominant tone is at **29.4–30.0 T**, i.e. 0.90·F_L at scale 1 (F_L = 33.1 T). Its companions are **22.3 T** and **7.3 T**. These two sum to 29.6 T, the dominant tone.
- Above ~3 T there is a harmonic comb reaching **130 T** (onsets 3.8 / 5.3 / 5.6 T for 59 / 88 / 130 T). The highest frequency present grows roughly as 23·B.
- **Onset:** the fast tones die out at ~1.15–1.2 T (windowed amplitude; `sdh_onset` 5σ gives 1.4 T for 22.3 T and 1.8 T for 29.4 T). The 7.3 T component is weak at low B: amp/noise ≈ 2 at 1.4 T. It is censored at the 1.0 T record edge and not tracked by `sdh_onset`.

Two readings survive one density:
- **(a) ABAB:** the pair (7.3, 22.3) plus a breakdown sum tone at 29.6 T, which is symmetry-allowed in 4L. This needs a global scale ≈ 0.90.
- **(b) Singleton:** one tone at ≈ F_L (scale 0.90), with 22.3 / 7.3 as comb or intermodulation products (≈ ¾ and ¼ of it).

`sdh_onset` labels every tone a harmonic of 7.3 T. The Luttinger-aware screen forbids settling that by ratio. **The discriminator is the n-dependence:** a harmonic tracks k·f exactly, while an ABAB heavy/sum pair drifts in ratio (model heavy/F_L 0.78 → 0.84 from n = 3.2 → 1.8). That comparison is the fan.

**Read — hole (run 7, n = −1.2):**
- This is the cleaner record by onset: **0.71 T** (6.6 T tone, SNR 84).
- Tones: 4.7–5.3, 6.6–7.0 and **12.3 T ≈ F_L at scale 1**.
- This sits in the near-CNP exception regime: the model ABAB pair is 5.9 / 6.5 T, close and balanced. A real ABCA pocket here would carry m* ≈ 1 mₑ and be LK-dead at T_e ≈ 8 K. So a 12.3 T tone with a 1.6 T onset points toward a sum tone, not an ABCA pocket. **Not a call.**

**Hedges:**
- The two sides imply different scales, 0.90 (e) vs ≈ 1.0 (h). This stays open until the global scale is fitted on the whole peak set.
- The electron trace dips negative at 6 T (−30 Ω): B_1–B_2 picks up some Rxy. Frequencies are unaffected, but with +B only there is no symmetrization.

**Side choice → the fan goes to the electron side.** Only the electron side reaches the design densities |n| ≳ 2–3×10¹² on the D = 0 line inside the validators. The hole side stops at −1.27, inside the exception regime.
