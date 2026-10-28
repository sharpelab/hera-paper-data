## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.25 … +3.25×10¹², B 1 → 10 T

**Plan step 4** (`hera_scratch/plan.md`). The operator asked for this fan; it is the main stacking measurement. Runs 6/7 (spot checks at D = 0) show strong oscillations on both sides that persist to ≲ 1 T. Run 6's e-side FFT splits as 7.5 + 22.5 ≈ 30 T, which leans ABAB. But F_L is still scaled by the geometry prior (c_tg is not calibrated), so that 30 T peak could also be the single full-density ABCA tone if the lever arm is ~10 % off. The fan settles this on its own data:
- **(a)** QH-minimum slopes dn/dB = νe/h give the absolute lever arm, and from it F_L(n).
- **(b)** A per-column FFT in 1/B gives the **F(n) map**:
  - ABCA is one family with F = F_L;
  - ABAB is two families that sum to F_L;
  - ABCB is two families with a different split and e–h asymmetry.
- **(c)** The QH sequence and LL crossings near the CNP.

**Geometry.** The gates are co-swept along the calibrated D = 0 line (run-5 cal): n from −1.25 to +3.25×10¹² at 0.03×10¹², 151 points. That is the whole D = 0 line inside the validators (TG-limited at both ends: V_tg −0.291 … +0.998 V). The field rows are uniform in 1/B from 1 to 4 T (85 rows, Δ(1/B) = 0.0089 T⁻¹, Nyquist 56 T > F_L,max ≈ 34 T), then 0.15 T steps from 4.15 to 10 T (40 rows), where the QH fan and crossings live. The FFT resolution is ΔF ≈ 1.1 T. B_lo = 1 T because the light tones survive below 1 T (run 6/7 onsets); going lower buys ΔF slowly and costs rows. The field goes up from where the magnet sits (0 T) and **ends at 10 T** for the step-5 ride-down, so nothing is traversed twice.

**Settings.** `sr1` is fixed at 100 µV (10 kΩ FS). Runs 6/7 peaked at 590 Ω; the ν = 0 CNP columns at high B may rail, which costs only a few columns that the FFT does not use. fast_delay is 0.6 s, which gives a group lag of ~1.5 points (≈ 0.05×10¹²). The lag is the same in every row, so FFT frequencies and QH slopes are unaffected. After each flyback, slow_delay = 3 s = 10 τ.

**Guards.** The sweep interrupts on any of:
- |I_gate| > 1 nA;
- T_sample > 2 K;
- a per-row field readback more than 20 mT off its setpoint.

**Price.** Calibrated from run 5 (1.10 s/pt at 1 s dwell) and runs 6/7 (ΔB/0.137 T/min + 3.1 s per field step): 151 × 0.70 s + 3.6 s flyback + 3 s + field step per row gives 131 s/row below 4 T and 181 s/row above, plus the 7.3 min pre-ramp to 1 T. That comes to 5.2 h; with the usual overrun, **≈ 5 h 45 m**.

**Checkpoints.**
- **First rows:** rail, leakage, drain current ≈ 10 nA, oscillations visible across n.
- **~Row 20 (1.3 T) and ~row 45 (1.9 T):** fan lines emerging.
- **Row 85 (4 T, ~3.3 h):** partial F(n) map over 1–4 T (ΔF 1.3 T).
- **End:** full analysis.

Abandon if sr1 rails away from the CNP, or if no Landau structure has appeared by 2 T (that would contradict runs 6/7).
