## Runs 6–7 — SdH spot checks (`sdh-spot-check`), D = 0: onset, tones, side choice for the fan

Raw MR first (top), then background-subtracted vs 1/B, then windowed FFTs (low-B vs high-B split) with the FS-count model lines. Channel arithmetic R = (sr1_X/1)/(sr0_X/−1e6). Run 6 is analysed from 0.8 T up: its 50 mT sub-1 T grid Nyquist-samples a 7.3 T tone only above ≈ 0.8 T.

**Read — electron, run 6 (n = +3.2×10¹² nominal):** onset **≤ 0.8 T**. The 7.2–7.3 T tone is still `censored` at every Nyquist-valid record edge down to 0.80 T, so onset_b is an upper bound. The heavier tones' onsets are 1.4–1.8 T on the 10 mT record. Their apparent 0.8 T censoring comes from the 50 mT segment, which is above their Nyquist, so it is not trusted. Tones over the 1–10 T record (δF ≈ 1.1 T): **7.3, 14.7, 22.2, 29.5 T**. In the low-B window 7.3 T dominates. From ≈ 3 T up, a **≈ 30 T tone** dominates, with its 2×/3× comb (59/88 T) above ≈ 3.8 T: that is the F_L-like, quantum-Hall ν = 4N regime. Model at scale 1: ABAB 7.3 / 25.8 T, ABCA 33.1 T. Rxx dips slightly negative (−25 Ω) in the 6 T minimum, probably a Hall admixture on this contact pair. Frequencies are unaffected, but the channel is not a clean ρxx.

**Why this is not decisive yet:** at this density the candidate readings coincide within δF:
- (i) an ABAB pair {7.3, 22.2} plus its sum/breakdown tone 29.5 = 7.3 + 22.2. The Luttinger sum closes at a single global scale s ≈ 0.89, inside the 0.8–1.2 lever-arm band.
- (ii) one 7.3 T pocket plus its harmonic comb (2×, 3×, 4× = 14.6 / 21.9 / 29.2 T).
- (iii) an ABCA singleton at 29.5 T (s ≈ 0.89) plus an unrelated 7.3 T series.

Near n ≈ 3.2×10¹² the pair ratio sits on the integer 3, so the harmonic screen cannot separate (i) from (ii) at one density. The degeneracy breaks with density: the model partition falls to a light fraction ≈ 0.17 by n ≈ 2×10¹², putting the heavy tone at ≈ 0.83·F_L against 3·f_light ≈ 0.5·F_L. A harmonic tracks k·f exactly; a pocket follows its own Onsager curve and keeps the sum. **That is what the fan is for.**

**Read — hole, run 7 (n = −1.2×10¹²):** a cleaner record, onset **0.71 T**. Tones 6.6 T (dominant), 4.7, 8.5 and 12.3 T, plus harmonics. Model at scale 1: the near-CNP ABAB pair 5.9 / 6.5 T (close, balanced) and ABCA 12.4 T with m* ≈ 1.1 mₑ. This is the investigation's low-|n| hole exception regime, so it is not decisive. It is consistent with the same s ≈ 0.9 (4.7 + 6.6 = 11.3 T ≈ 0.9·F_L). Preview only; no verdict.

**Side for the fan: electron.** The D = 0 hole reach stops at −1.27×10¹² (TG −0.3 V validator), entirely inside the exception regime. The electron side reaches +3.25×10¹², where the templates separate. This follows the investigation's Step 2 design-density rule; spot-check cleanliness is secondary here.
