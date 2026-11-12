## Runs 6–7 — SdH spot checks at D = 0 (`sdh-spot-check`): electron n = +3.2×10¹², hole n = −1.2×10¹²

Raw Rxx(B) first, then the read. Channel arithmetic: R = sr1_X / (sr0_X / −1e6). Run 6: 0 → 10 T, 50 mT steps up to 1 T and 10 mT above. Run 7: 10 → 0.3 T in 20 mT steps. Settle: 3 s driver settle = 10τ at τ = 0.3 s, 24 dB. Both runs are clean: no rail (peak ≤ 12 % of full scale), gate leakage ≤ 0.2 nA, T 1.17–1.29 K. `sdh_fft` doesn't zero-pad on the uniform-B path, so its peaks snap to 1/span bins. Peak positions here come from a zero-padded FFT instead (same B-space background removal).

**Read — electron side (run 6, n = +3.2×10¹², F_L = 33.1 T).**
- The robust peak set is a comb at **k × 7.35 T**: 7.3, 14.9, 22.3, 29.4 and 58.5 T. It's stable across windows [1.0–1.4, 3.0–7.3] T and background degrees 4/5/7. Weak extras: 35.8–36.6 T (≈ 0.1 relative amplitude) and, in the low window only, 18.4 / 32.9 T.
- **Dominant tone:** 7.3 T, the lightest-looking tone. It is still above threshold at the Nyquist-valid record edge (0.85 T, censored). The heavier comb members set in at 1.3–1.8 T.
- **Against the templates:** the 7.35 T tone sits on the model's ABAB light orbit at scale 1.0 (7.31 T, 0.22·F_L). The trilayer ABA partner at this density would be about 1.9 T, so adjacent-N is disfavored for this tone. ABCA has no pocket there.
- **The ≈ 29.4 T tone is the open question.** It sits exactly at 4 × 7.35, so three origins are possible:
  - a harmonic;
  - the ABAB heavy tone, but at an inconsistent scale: the pair sums to 36.8 T (s ≈ 1.11), while the model's heavy/light ratio at 3.2 is 3.53, not 4.0;
  - an ABCA-domain or region-B (n + 0.43×10¹², run 5) tone.
- One density cannot separate these. A harmonic tracks k·f(n) exactly, while a real pocket follows its own Onsager curve with a Luttinger-summed partner. That is the fan's job.
- High-field caveats (≥ 5 T, QH regime): Rxx dips slightly negative near 6 T, i.e. a few-% Hall admixture on this pair. The large rise above 7.7 T is excluded from the SdH read, and the high-field structure is weak evidence per Step 6.

**Read — hole side (run 7, n = −1.2×10¹², F_L = 12.4 T).** Onset 0.72 T (tone 6.6 T). The widest window, [0.8, 8] T (δF 0.9 T), resolves **4.7 + 7.1 T**, which sums to 11.8 T ≈ 0.95·F_L. That is a two-pocket-shaped hole Fermi surface; the model's ABAB pair here is 5.9 / 6.5 T. Weaker peaks sit at 12.3 T (≈ F_L, a sum tone or harmonic) and 14.3–14.8 T (≈ 3 × 4.7). The split is window-dependent: [1.5, 8] T merges it to 5.9 T. ABCA at this density has m* ≈ 1.1 mₑ, so it is LK-dead here. This is the recipe's near-CNP hole exception regime, and the TG −0.3 V limit caps the side at |n| ≤ 1.27×10¹². **Suggestive of two hole pockets, not decisive.** It is reported as consistent-with and feeds the final call as corroboration only.

**Take.** The electron side is the only side that reaches the design densities, and it carries clean multi-tone SdH, so the fan goes there. Handed to the fan:
- Light-tone onset ≤ 0.85 T (Nyquist-valid, censored);
- heavy-comb onset 1.3–1.8 T;
- F_max ≈ 37–40 T (sum-scale 1.11, and region B's F_L at n + 0.43);
- a 58.5 T harmonic that Δ(1/B) must not fold into the 20–30 T band;
- R(B = 0) ≈ 52–66 Ω and MR ≈ 10× by 9 T, so 50 µV (5 kΩ full scale) holds.
