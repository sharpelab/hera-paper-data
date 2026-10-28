## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, `tetralayer-stacking-fs-count`)

**Why this fan.** The spot checks (ana, runs 6–7) put the fan on the electron side: the hole side is capped at |n| ≤ 1.27×10¹² in the near-CNP exception regime. At n = +3.2×10¹² the peak set is a comb at k × 7.35 T. The 7.35 T tone sits on the ABAB light orbit. The ≈ 29.4 T tone is 4 × 7.35 exactly, so it could be a harmonic, the ABAB heavy tone (the pair sums to 1.11·F_L), or an ABCA / region-B tone. One density can't split these. The n-dependence does, and it is what this fan buys:
- a harmonic tracks 4·f_light(n), about 12.5 T per 10¹²;
- the ABAB heavy tone runs about 7.2 T per 10¹² with a light partner closing the Luttinger sum under one global scale;
- an ABCA singleton runs about 10.3·s T per 10¹² with no partner;
- region B shows as an intercept offset (n + 0.43), not a slope change.

Over the window below, these trajectories separate by ≥ 2.4 δF.

**Design (cost floor, per `landau-fan` step 1).**
- **B_lo = 0.85 T.** This is `sdh_onset` on run 6's Nyquist-valid record. The light tone is censored there, so 0.85 T is a lower bound, not a guess.
- **n = 2.40 → 3.24×10¹².** The top end is the D = 0 line's TG-limit edge (V_tg 0.995 V). The bottom end is where the light partner still gets ≈ 5 periods in [0.85, 6] T (model 4.8 T at 2.4).
- **Coverage trade:** n < 2.4 is excluded. The partner is unresolvable there at this onset, and the heavy-vs-ABCA split falls below 2δF. The hole side is excluded for the reason above.
- **B_hi = 6 T.** Heavy-tone δF = 1.8–2.5 T (onset 1.4–1.75 T), and there is a high-B half for the breakdown / F_L-origin B-window split. Above ~6 T the low-n columns enter the QH regime.
- **Nyquist, B axis:** uniform in 1/B, Δ(1/B) = 0.00828 T⁻¹ gives a 60 T Nyquist. That clears F_max ≈ 40 T at 1/3 sampling, and the observed 58.5 T harmonic doesn't fold. A 1/2-rate grid would alias it onto the 22 T tone. 123 rows.
- **Nyquist, n axis:** ray spacing at 0.85 T is 0.082×10¹². A 0.04 step gives 2.06 points per period, which is the floor. 22 points.
- **Dwell:** fast_delay 1.8 s = 6τ (τ 0.3 s, 24 dB, read and asserted). Each B row is fully settled by the ramp, 3 s settle and slow_delay 3 s. The n-axis lag only mixes neighbouring columns about 0.4 T apart in F, far below δF.
- **Sensitivity:** sr1 is set to 50 µV (5 kΩ full scale) and held fixed. The worst corner, n = 2.4 × 6 T, is about 0.7–0.9 kΩ, so headroom is ≥ 5×. sr1 is at 2 µV after the handoff restore and would rail without this set.
- **Price:** 22 × 1.95 s per point (run-5 overhead + paired set) + 7.5 s row overhead = 50 s per row. That's 103 min of rows, plus 38 min of bare ramp 0.85 → 6 T, plus 6 min positioning. Total 147 min, ≈ 2 h 40 m realistic.

**Ends at 6 T** with the gates parked at 0. The next step (LK mass split / firming) rides the field down instead of re-traversing.

**Checkpoints.**
1. **First rows (~8 min):** sr1 level vs full scale, I ≈ 10 nA, gate current, T, no flat channel. Abort there if anything's off.
2. **B ≈ 1.6 T (row 66, ~67 min):** per-column FFT on [0.85, 1.6] for light-tone presence across n. Abandoning here saves ~1 h 30 m (rail, leak, dead channel or featureless only; the heavy band lives above 1.4 T).
3. **B ≈ 3 T (row 101, ~1 h 47 m):** interim trajectories, light vs heavy vs 4× light.

Leak guard: > 1 nA on either gate interrupts the sweep and parks the gates.
