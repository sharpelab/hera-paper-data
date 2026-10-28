## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, governed by `tetralayer-stacking-fs-count`)

**Why this fan.** The spot checks (runs 6–7, ana) show clean SdH on both sides with sub-1 T onsets. They cannot decide the stacking at one density. At n = +3.2×10¹², tones sit at 7.1, 22.3 and 29.5 T, and nothing at F_L = 33.1 T. The 22.3 and 29.5 T tones read either as harmonics of 7.1 T or as an ABAB heavy pocket, and each pairing closes the Luttinger sum at a different lever-arm scale (0.89 or 1.11). Only the **n-dependence** separates them: a harmonic tracks k·f exactly, a pocket follows its own Onsager curve, and f₁ + f₂ = F_L(n) across density pins the scale. **Side: electron.** At D = 0 the hole side ends at −1.27×10¹² (TG limit), inside the near-CNP exception regime. The electron side reaches +3.25×10¹², where the ABAB heavy tone sits 3.5–7.5 T below F_L.

**Design (binding checks computed, one fan):**
- **B_lo = 0.90 T**: the run-6 `sdh_onset` gives 0.91 T.
- **n_max = 3.25×10¹²**: the D = 0 line meets the TG limit here (V_tg = 0.998 V).
- **n_min = 2.0×10¹²**: the model heavy-tone vs F_L split (3.55 T) is ≥ 2·δF_heavy (1.5 T). The partner tone reaches ≥ 5 periods from 2.5×10¹².
- **N_n = 30**: the ray-Nyquist floor, 2 points per 4eB/h = 0.087×10¹² at B_lo.
- **N_B = 103, uniform in 1/B**: Δ(1/B) = 1/(3·F_L(n_max)) = 0.0099 T⁻¹, which puts the Nyquist frequency at 50 T. The 1/(2F_L) floor (69 rows) would put a scale-1.1 singleton (37 T) past Nyquist, folding onto the heavy-tone band. 103 rows also keep the folded heavy 2nd harmonic out of the 0–40 T claim band.
- **Resolution**: δF = 1.0 T over the 0.91–10 T record.
- **Dwell**: fast_delay **2.1 s = 7τ** (τ = 0.3 s, 24 dB/oct, the settling floor). The n-axis carries oscillations, so under-settling would cost the heavy tone.
- **Dynamic range**: sr1 fixed at **50 µV = 5 kΩ FS**. The spot checks peaked at 530/590 Ω at 10 T (11–12 %) on either side of this density window. The worst corner, n = 2.0 × 10 T, is expected below 1 kΩ, so headroom is ≥ 5×.

**Price:** 200 min computed:
- grid: 3090 pts × 2.22 s = 114 min (read overhead 0.10 s/pt from run 5)
- traverse: 9.1 T bare at 0.137 T/min = 66 min
- row overhead: settle 3 s (run 6) + slow_delay 3 s + flyback 1 s = 13 min
- magnet positioning 0 → 0.9 T: 7 min

The ETA adds ~10 %, the session's overrun on inherited estimates. **Coverage trade:**
- The hole side is excluded (preview in run 7 stands).
- n < 2.0 is excluded: those columns have heavy/F_L splits under 2δF and partners under 3.5 periods. Going down to 1.5×10¹² would cost +12 columns ≈ +45 min for no resolvable tones.
- Column 2 sits at n = 3.207, next to run 6. It gives a uniform-1/B vs uniform-B grid-change reproduction at no extra cost.

**Guards (E1):**
- Gate current > 1 nA or T_sample > 2 K → interrupt, with gates parked.
- sr1 clips are logged, not aborted: one clip corrupts only its own column.
- An interrupt does not stop a magnet ramp; the worst case is the supply finishing its ≤ 0.9 T step.

**Ends at 10 T with gates at 0.** The next step (LK mass split or a ride-down) starts from 10 T, so no re-traverse. **Checkpoints:**
- **First rows** at 0.9 T (≈ 10 min in): R 50–100 Ω, phase ≈ 0, pA gate currents, T at base.
- **Row ≈ 50** (B ≈ 1.6 T, ~1 h 20 m in): per-column FFT on the landed rows for the light tone vs n.
- **Row ≈ 80** (B ≈ 3.3 T, ~2 h 15 m in): δF ≈ 1.4 T; heavy tone vs F_L in the high-n columns. Continue / abandon at this point. Abandon if no oscillation content appears or sr1 rails.
