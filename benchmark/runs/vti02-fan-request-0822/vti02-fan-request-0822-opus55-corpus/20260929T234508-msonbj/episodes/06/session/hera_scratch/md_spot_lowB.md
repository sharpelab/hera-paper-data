## HERA — Step 3c: low-field onset extension at n = +3.2×10¹², D = 0 (`sdh-spot-check`) — pins the fan's B_lo

**Arc:** Steps 1–3 done (run 5 calibration; spot checks: run 6 electron n = +3.2, run 7 hole n = −1.2). Step 4, the fan, is next. It goes on the **electron side**. There the D = 0 line reaches n = +3.27×10¹² and the templates separate. The hole side is gate-limited to |n| ≤ 1.27×10¹², inside the near-CNP exception regime (run 7: ABAB pair 5.9/6.5 T, balanced, unreadable).

**Why this cell first.** In run 6, `sdh_onset` found the carrying 7.3 T tone *censored* at the 1.0 T record edge. The 50 mT points below 1 T are sub-Nyquist for it. That tone sits exactly at the model's ABAB light pocket (7.31 T, scale 1.00). The fan's binding case is that partner at the lowest density: it needs ≥ 5 periods, i.e. f_light·(1/B_lo − 1/10) ≥ 5.
- With B_lo = 1.0 T this forces n ≥ 2.85×10¹². That window is too narrow for the n-dependence harmonic screen: 4×f_light crosses the heavy branch near 2.6×10¹².
- A 2.0–3.2×10¹² window needs B_lo ≤ 0.66 T.

Per `landau-fan` step 1, a censored onset is pinned by a cheap low-field extension, not guessed. This run takes about 15 min against a ≈ 6 h fan, and its ≈ 1.8 h n-lever is what's at stake.

**Design.** Gates at the run-6 point (V_tg, V_bg) = (+0.984, +1.166). B 0.4 → 1.1 T ascending, uniform in 1/B: 128 pts, Δ(1/B) = 0.0125 T⁻¹ (Nyquist 40 T > F_L = 33.1 T). Dwell = the driver's 3 s settle (10τ at 0.3 s / 24 dB), as in run 6. sr1 at 2 µV (200 Ω FS): run 6 had R ≤ 57 Ω below 1.2 T, 3.5× headroom. Timing from runs 6/7 (step = ramp + 3.1 s): 0.7 T/0.137 T/min + 128 × 3.1 s + 3 min positioning ≈ 15 min. It ends at 1.1 T with gates at n = 3.2, the fan's first column. **Read:** `sdh_onset` on this record stitched to run 6 (1–10 T) → B_lo → n_lo → the fan lands.
