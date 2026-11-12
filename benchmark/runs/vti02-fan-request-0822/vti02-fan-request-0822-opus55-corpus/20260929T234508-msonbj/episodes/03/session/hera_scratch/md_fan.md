## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`) — per-column FFT for the stacking call

The spot checks (ana, runs 6–7) leave a fork at n = +3.2×10¹². The tones {7.3, 22.3, 29.4 T} read either as an **ABAB pair** (model 7.31 / 25.78 T) with a sum tone at 29.5 T (density scale ≈ 0.89), or as **one 7.3 T tone plus harmonics**. The fan separates them through n-dependence. From n = 1.6 to 3.2×10¹² the ABAB heavy/light ratio should move ≈ 6 → 3.5, a harmonic comb stays locked at 3×/4×, and an ABCA singleton tracks F_L. The high-field rows pin the absolute density scale from the QH ν-rays (n = ν·eB/h), which the Luttinger read needs (investigation: "pin the scale before you reject").

**Design (landau-fan step 1 checks, computed):**
- **Nyquist, B-axis:** uniform in 1/B with **Δ(1/B) = 0.0080 T⁻¹** (sampling rate 125 T, Nyquist 63 T). That is 3.8 samples per period of F_L(3.2) = 33.1 T, and it keeps run 6's 58.6 T second harmonic un-aliased.
- **Nyquist, n-axis:** **Δn = 0.04×10¹²**, which is 2.4 points per ν-ray at B_lo (0.097×10¹² at 1 T).
- **Field window:** **B_lo = 1.0 T** is the `sdh_onset` value on run 6's 10 mT record. It is censored: the 7.3 T tone is still alive at the record edge. **B_hi = 10 T.** The FFT claim window is 1–5 T (δF = 1.25 T; above ~5 T the QH minima turn harmonic-rich). The 5–10 T rows are for the ν-ray scale and the ν = 8/12/16 layer-number ladder.
- **Settling:** fast_delay 1.8 s = 6τ (τ = 0.3 s, 24 dB) per the fan recipe's per-column-FFT rule. Along-n lag costs ≲ 12 % of the fastest tone's amplitude at its onset and vanishes above it. slow_delay 3 s = 10τ after each flyback.
- **Dynamic range:** sr1 **50 µV = 5 kΩ full scale**, inherited from the spot checks. Worst corner is low n × 10 T: R₀(1.6) = 83 Ω (run 5) × low-n MR ×4–10 ≈ 0.3–1 kΩ, which leaves ≥ 5× headroom. A rail warning prints; it does not interrupt.

**Coverage trade, stated:**
- **Hole side excluded.** The D = 0 line stops at −1.27×10¹² (TG −0.3 V limit), which is inside the near-CNP exception regime, so no hole density there separates the templates.
- **n < 1.6×10¹² excluded.** There the ABAB heavy tone sits within ~15 % of F_L, and the partner (< 2.3 T) can't be resolved in this window.
- **Partner onset below 1 T not pinned.** Extending to B_lo = 0.8 T would buy +28 % partner record for **+31 rows ≈ +45 min**. Not taken: at n ≥ 2.8 the partner already gets ≥ 5 periods, and the discriminating heavy / F_L tones only start at 1.4–1.8 T.

**Price:** 114 rows × (41 × 1.9 s + ~9 s turnaround), with t_pt calibrated from run 5 (1.10 s/pt at fast_delay 1.0) and turnaround from run 5's 5.8 s plus the 3.1 s magnet settle from run 6. That gives 2.75 h of grid, plus the 9 T traverse (66 min), the 0→1 T positioning (7 min) and ~5 % overrun margin.

**Checkpoints:**
- **First rows (B ≈ 1.0 T):** signal, noise, leakage, T.
- **~1.5 h (B ≈ 2 T, row 63):** partial per-column FFT on 1–2 T. Stop if no column shows oscillation content by then; the read would be resolution-limited.
- **~3.2 h (B = 5 T, row 101):** the claim window is complete, so run the preliminary per-column F(n) read.

**End state:** B = 10 T, gates parked at 0. The next step (LK split / grid-change reproduction) rides the field down.
