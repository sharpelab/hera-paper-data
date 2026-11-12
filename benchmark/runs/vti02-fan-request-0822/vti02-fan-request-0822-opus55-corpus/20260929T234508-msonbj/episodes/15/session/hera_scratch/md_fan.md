## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, per `tetralayer-stacking-fs-count`)

**What the spot checks say (runs 6/7).** Electron side, n = +3.2×10¹² (F_L = 33.1 T): stable tones at **7.3, 14.7, 22.2 and 29.4–31 T**. The 29.4–31 T line grows with B (onset ≈ 1.8 T, a breakdown/sum-tone signature), and it has high-B harmonics at 58.6 and 88.4 T. The 7.3 T tone matches the ABAB light pocket (model 7.3 T). **The catch:** `sdh_onset` puts the whole set on one integer comb of 7.3 T, so from one density "22 T = the ABAB heavy pocket (model 25.8 T at scale 1)" cannot be told apart from "22 T = 3 × light". The investigation calls this out as the ratio-only harmonic-screen trap. Hole side, n = −1.2×10¹²: tones at 5.3, 7.0 and 12.4 T (= F_L), onset 0.71 T. That density sits in the near-CNP semimetal exception regime, and the D = 0 line stops at −1.28×10¹² (TG −0.3 V limit).

**Decision: fan the electron side, n = +3.2 → +1.6×10¹² at D = 0.** Only density dependence can break the tie: a harmonic tracks k·f_light(n) exactly, while a real pocket follows its own Onsager curve. From the model: 3×light runs 6.9 → 21.9 T across the window, ABAB heavy 14.2 → 25.8 T, F_L 16.6 → 33.1 T. The window also separates the two readings of the ~30 T line. A global lever-arm scale gives s·F_L(n). A region-B pocket (ridge B, offset 0.43×10¹² in run 5) gives F_L(n − 0.43). These agree at n_hi and differ by ≈ 3 T at n_lo. **Coverage trade:** the hole side is excluded because it can't reach the design regime (|n| ≳ 2×10¹²). Its 12.4 T = F_L tone stays an open item for the LK/B-window-split Verify. Running the fan through the CNP to −1.28 would add ~40 % more columns plus a low-n dynamic-range risk.

**Design (computed, `hera_scratch/fan_design.py`).**
- **B_lo = 1.0 T**: the honestly sampled low edge of run 6. `sdh_onset` reads the carrying 7.3 T tone as censored there, and the heavy/F_L tones start at 1.4–1.8 T.
- **n_lo = 1.6**: the lowest density where ABAB-heavy vs F_L still clears 2δF.
- **B_hi = 10 T** (the session cap): needed for the high-B half of the mandatory F_L-tone-origin B-window split.
- **B-axis sampling:** uniform in 1/B, 121 rows, Δ(1/B) = 0.0075 T⁻¹ = 1/(4.0·F_L(n_hi)). I chose 1/4 rather than 1/3 because of the harmonics seen in run 6: at 1/3 the 88 T line would alias to 11.6 T, into the decision band. At 1/4 aliases land above F_L, and the primary tone read uses a [1, 5] T window below the harmonics' onsets.
- **Resolution:** δF = 1.11 T. At n = 3.2 heavy vs F_L differ by 7 T; at n = 1.6 by 2.4 T.
- **n-axis:** 35 points, Δn = 0.047×10¹². That is 2.05 per LL spacing at B_lo, the ray-Nyquist floor.
- **Sensitivity:** fixed at 50 µV = 5 kΩ FS, as in runs 6/7. R₀(n = 1.6) = 82 Ω (run 5), and the high-B maxima were 522/576 Ω (runs 6/7, down to ν ≈ 5), so there is ≥ 6× headroom at the low-n × high-B corner.
- **Settling:** fast_delay 2.4 s = 8τ at 0.3 s / 24 dB (≈ 4 % residual of the adjacent-column step). slow_delay 3 s = 10τ after the flyback and field step.
- **Price:** 7.5 min ramp to 1 T, 66 min traverse, 121 × 7.4 s row overhead, and 4235 pts × 2.6 s (calibrated on run 5: fast_delay + 0.17 s). That gives 4 h 32 m bare, **≈ 4 h 50 m** realistic.

**Guards (auto-interrupt; interrupt does not stop a magnet ramp):** |I_gate| > 1 nA, T_sample > 1.6 K, or > 20 points above 95 % FS. **Checkpoints:**
1. First rows at 1 T: FS fraction, leakage, T, and R(n = 3.2) against run 6's 13 Ω at 1 T.
2. Row ~80 (B ≈ 2.5 T, ~3 h in): interim per-column FFT. Does the n = 3.2 column reproduce run 6's 7.3/22 T? At n ≈ 2, does the "22 T" branch sit near 17 T (pocket) or near 11 T (3× light)?

**End state:** the gates park at 0 and the field stays at 10 T on purpose; the LK down-leg (Verify) starts from there.
