## Runs 6–7 — SdH spot checks (`sdh-spot-check`) at D = 0: the fan's design inputs

Run 6: electron side, n = +3.2×10¹², B 0→10 T (50 mT below 1 T, 10 mT above). Run 7: hole side, n = −1.2×10¹², 10→0.3 T at 20 mT. Both use the run-5 calibration and sr1 at 50 µV, and neither went above 12 % of full scale. Raw MR is plotted first, then the onset and the 1/B FFT against F_L and the model F(n) at scale 1.

**Read — electron side (run 6).** Clean multi-tone SdH. The spectrum is stable across windows (1–8, 1–10, 2–10 T) at **≈ 7.3, 14.8, 22.3, 29.5 T**, against F_L = 33.1 T.
- **Onset.** On the fully sampled record (≥ 1 T; below 1 T the 50 mT steps alias anything above 2.5 T), the 7.3 T tone is `censored` at 1.0 T, so it is still alive at the record's low edge. The ~22 T tone's onset is 1.40 T and the ~29.5 T tone's is 1.76 T.
- **Two readings fit this set, and one density cannot separate them.**
  - (a) An ABAB pair (7.3 + 22.3 = 29.6 T) at a global scale of ≈ 0.89, which sits inside the lever-arm prior. Then 29.5 T is the sum tone (breakdown or mixing, expected for ABAB) and 14.8 T is the difference tone or the 2nd harmonic.
  - (b) A harmonic comb of 7.3 T (×2, ×3, ×4 = 14.6, 21.9, 29.2 T).
  - (c) Also possible: the ~29.5 T line is a singleton at F_L from the region-B domain (run 5 ridge B, offset −0.43×10¹², which predicts ≈ 28.7 T here), or ABCA at scale 0.89.
- At n = 3.2 the ABAB pair ratio is ≈ 3, exactly where a ratio-only harmonic screen eats the real heavy tone (investigation Why). **The n-dependence decides:** a harmonic tracks k·f₁(n), the ABAB heavy tone its own Onsager curve (slope ≈ 0.7 of F_L's), and an ABCA singleton F_L(n) (slope h/4e, with a −4.4 T offset if it comes from region B). The Landau fan is built for this.
- Rxx goes negative at ~6 and ~7.2 T (−33 Ω). Only +B was measured, so this is likely Hall admixture on B_1–B_2; it can't be symmetrized and is noted as a hedge.

**Read — hole side (run 7).** Onset 0.71 T, with tones at ≈ 6.6–7.0 T and ≈ 12.3 T (≈ F_L = 12.4 T). The ABAB model gives 5.9 / 6.5 T, the close, balanced near-CNP semimetal pair. It is within the model spread of the observed 6.6–7 T but is not resolved at δF ≈ 0.8 T. ABCA's singleton at 12.4 T has m* ≈ 1.1 mₑ (LK-suppressed), so a 12.4 T line here is more naturally the pair's sum or a harmonic (2 × 6.6 = 13.2) than an ABCA pocket. This is the recipe's low-|n| exception regime, and the D = 0 line reaches only n ≈ −1.1 to −1.3×10¹² on the hole side (TG −0.3 V limit). **So the hole side cannot reach the design densities (|n| ≳ 2×10¹²), and the fan goes on the electron side.** That is a coverage consequence of the gate limits, not a cleanliness verdict.

**Take:** no stacking call from the spot checks alone. The electron-side fan across n ≈ 1.5–3.2×10¹² is the discriminating measurement. It inherits run 6's B_lo = 1.0 T, sensitivity (50 µV) and D = 0 calibration.
