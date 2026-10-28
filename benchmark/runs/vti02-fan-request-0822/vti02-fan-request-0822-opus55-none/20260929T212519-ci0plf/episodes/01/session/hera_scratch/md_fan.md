## HERA — Step 4: Landau fan along D = 0 (`landau-fan`) — the stacking measurement

**Plan step 4** (`hera_scratch/plan.md`), requested by the operator. **Runs 6–7 set the design.** On the electron side (run 6, n = +3.2×10¹² nominal), the 1.3–5 T FFT shows tones at **7.0 / 15.8 / 22.8 / 29.9 T**, and **30.0 T alone above 5 T**. 7.0 + 22.8 ≈ 29.9 is the full-density tone: the two-band sum rule of an ABAB bilayer-pair. The QH zeros sit at ν ≈ 16, 20, 28, 32, 36, 44, 48, 60, 64, with 24/40/52/56 missing (LL crossings). The 30 T tone also puts the true density at **0.907 × the geometry-prior n scale**. The hole side (run 7, n = −1.2) is near-CNP and messy. A single spot can't separate two bands from a series region-B tone (+0.43×10¹²) or a harmonic. The fan tests the sum rule and ∝ n scaling of each tone column by column across both carrier signs. It also gives the high-B crossing pattern.

**Geometry.** Slow axis is B, 1 → 10 T (138 rows): uniform in 1/B at Δ(1/B) = 0.01 T⁻¹ up to 3.1 T (Nyquist 50 T, covering region B's full-density tone), then 0.1 T steps to 10 T for the QH-crossing read. Fast axis is (V_tg, V_bg) co-swept along the run-5 D = 0 line, n = −1.25 … +3.25×10¹² nominal in 181 points (0.025 step). That is the full D = 0 window inside the validators (TG-limited at both ends; V_tg max +0.998 V).

**Coverage trade:** D ≠ 0 is not covered. The ABCB test (R(n, D) vs R(n, −D), hysteresis) is plan step 5, a separate cheaper cell. B < 1 T is also excluded: it only adds light-tone periods and would cost ~40 rows in 1/B.

**Settings.** `sr1` fixed at 100 µV (10 kΩ FS; `state0` had left it at 2 µV). The noise floor is ~3 Ω at 50 and 100 µV alike (runs 5–7). The high-B CNP may rail; the stacking information is at |n| > 0.3. `fast_delay` is 0.6 s = 2τ with forward-only rows, so lock-in lag is a constant n-shift. `slow_delay` is 3 s after each flyback.

**Guards:** |I_gate| > 1 nA or T_sample > 2.5 K interrupts. Gates park at 0 at the end; the field stays at 10 T for the next step to ride.

**Price** (calibrated on this session's runs): 181 × (0.6 + 0.10 s, run 5) + ~10 s row overhead (flyback + 3 s settle, runs 5–7) → ~136 s/row × 138 rows, plus a 65.7 min ramp and 7.3 min for 0 → 1 T. That is 6.4 h modelled, **~6.9 h realistic**.

**Checkpoints:**
- **First rows** (~15 min in, at 1.0 T): drain current ≈ 10 nA, `sr1` not railing away from the CNP, gate currents at pA, B readback tracking the setpoints.
- **Row ~40** (B ≈ 1.6 T, ~1.7 h): FFT preview on high-n columns (light tone present?).
- **Row ~68** (B ≈ 3.0 T, ~2.9 h): per-column FFT over 1–3 T for all n; this is the main tone read. Continuing to 10 T costs ~3.9 h more for the crossing pattern. Cutting there saves it for step 5 if the tone read is already decisive and step 5 can't wait.
