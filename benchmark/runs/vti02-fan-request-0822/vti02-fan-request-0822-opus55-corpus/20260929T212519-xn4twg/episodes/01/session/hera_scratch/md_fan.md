## HERA — Step 4: Landau fan for the stacking call (`landau-fan-vti`), electron side, D = 0

**Why this fan.** The spot checks (ana, runs 6–7) cannot separate the readings at one density. At n = +3.2×10¹² the tones {7.3, 22.2, 29.5 T} fit two readings equally well:
- an ABAB pair plus its sum tone (7.3 + 22.2 = 29.5, closing at a global scale s ≈ 0.89);
- a 7.3 T pocket plus its 3× and 4× harmonics.

The pair ratio sits on the integer 3 there. The degeneracy breaks with density. Toward n ≈ 2×10¹² the ABAB heavy tone moves to ≈ 0.83·F_L while 3·f_light falls to ≈ 0.5·F_L. A harmonic tracks k·f; a real pocket keeps f₁ + f₂ = s·F_L(n) with a single s. The fan tests exactly this, per column (investigation Steps 4–5).

**Design** (`landau-fan` step 1: both-axis Nyquist, cost floor):
- **Side: electron.** At D = 0 the hole side stops at −1.27×10¹² because of the TG −0.3 V validator. That is inside the near-CNP exception regime, where the templates don't separate (Step 2).
- **Density window: n = +3.25 → +2.00×10¹²**, nominal run-5 calibration.
  - The top is the TG validator: V_tg = 0.998 V.
  - The bottom is where the light partner falls below ≈ 4 periods and the heavy tone drifts into the ≈ 0.9·F_L mimic regime.
- **Field window:**
  - **B_lo = 0.8 T.** `sdh_onset` still reports the 7.2 T light tone as censored at 0.80 T. That is the lowest edge where run 6's 50 mT segment is Nyquist-valid, so the onset is ≤ 0.8 T (the hole side measured 0.71 T).
  - **B_hi = 5 T.** The heavy tone's resolution is limited by its own ≈ 1.4 T onset, so raising B_hi buys little: δF 1.9 T at 5 T vs 1.6 T at 10 T.
- **B-axis sampling:** 78 rows uniform in 1/B, Δ(1/B) = 0.0136 T⁻¹. That puts Nyquist at 36.7 T, above F_L(3.25) = 33.6 T at scale 1 (2.2–2.4 points per period).
- **n-axis sampling:** 36 points, Δn = 0.036×10¹², which is 2.2 points per Landau-level period at B_lo.
- **Light-partner period count:** 7.8 periods at n = 3.25, ≈ 5 at n = 2.3, and 4.1 at n = 2.0 (marginal there, flagged).

**Coverage trade.** Excluded:
- **The hole side:** not reachable inside the validators. Changing a validator is session-banned.
- **5–10 T:** the quantum-Hall ν ≈ 12–16 ladder, a weak layer-number complement only. It would cost ≈ 45 min (36 min bare traverse + 7 rows) and can be taken later as a measured ride-down.

Known hazard: above ≈ 3.8 T, the F_L tone's 2× comb (≈ 60 T) aliases to ≈ 13–15 T at this Δ(1/B). Its n-slope is negative, so it is identifiable. Pocket tones are read from the B ≤ 3.8 T window; the high-B window serves only the F_L-tone-origin split.

**Settings:**
- Dwell 1.8 s = 6τ (τ 0.3 s / 24 dB, per-column-FFT rule).
- sr1 at **20 µV = 2 kΩ full scale**. Worst corner: R₀(n = 2.0) = 73 Ω (run 5), and run 6 peaked at ≈ 130 Ω up to 5 T, so headroom is > 5×. The guard prints a warning if |X| exceeds 90 % of full scale.
- Leak trip at 1 nA interrupts the run.
- Gates park at the end; the field is **held at 5 T** for the next step (the LK mass sweeps start from there).

**Price:** 78 rows × (36 × 1.95 s + 7 s turnaround) ≈ 100 min, plus the 0.8 → 5 T traverse (31 min bare) and positioning from 0 T (6 min). Total ≈ 2 h 17 m nominal. The per-point figure is calibrated on run 5 (1.10 s/pt at a 1.0 s dwell) and the per-step field overhead on run 6 (+3.1 s per step).

**Checkpoints:**
1. **First 2 rows:** signal level vs full scale, leakage, dead or flat channels, T.
2. **Row ≈ 43 (B ≈ 1.5 T, ≈ 65 min):** per-column FFT over 0.8–1.5 T. The light tone should appear and move with n. Abandon if no column shows it.
3. **Row ≈ 62 (B ≈ 2.5 T, ≈ 1 h 40 m):** preliminary F(n) — light, heavy vs 3·f_light, and the F_L tone. The last 16 rows are ramp-limited (≈ 40 min).
