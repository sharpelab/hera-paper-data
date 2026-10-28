## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, `tetralayer-stacking-fs-count` Step 4)

**Why this fan.** Spot check run 6 (n = +3.2×10¹²) shows tones at ≈ 7.3 / 22.3 / 29.4 T (ana, runs 6–7). At a single density they read either as an ABAB pair plus a sum tone at F_L (scale ≈ 0.90) or as a harmonic comb on 7.3 T. The heavy/light ratio sits near 3×, exactly the trap the investigation names. **The density dependence decides.** A harmonic tracks k·f₁(n). The ABAB heavy tone runs at ≈ 0.7× the F_L slope and climbs toward ≈ 0.95 F_L at low n. An ABCA singleton, or the sum tone, stays at F_L(n). The fan is electron-side because only that side reaches the |n| ≳ 2–3×10¹² design densities. The hole side of D = 0 stops at −1.27×10¹² at the TG limit, in the near-CNP exception regime; run 7 is its preview.

**Design, floored per `landau-fan` step 1:**
- **n window: +3.2 → +1.2×10¹², 43 pts.** n_max = 3.2 sits at the TG validator edge. n_min = 1.2 gives a 2×10¹² lever arm, so the heavy-vs-harmonic slopes separate by ≈ 3–4 δF. dn = 0.0476 is the ray-Nyquist floor (≥ 2 pts per Landau ray) at B_lo.
- **Field: 1.0 → 10 T, uniform in 1/B, 91 rows.** d(1/B) = 0.0100 ≤ 1/(3·F_L(3.2)).
  - B_lo = 1.0 T is `sdh_onset`'s onset_b on run 6. It is censored at the 10 mT record edge, so it is a lower bound. It is also what the investigation's ≥ 5-period rule needs for the 7.3 T partner: B_lo ≤ 1.27 T; this gives 6.6 periods.
  - B_max = 10 T, the session cap. It gives the widest window for the mandatory F_L-tone-origin B-window split, and parks the magnet where the LK step rides down from.
- **Settling: fast_delay 3.0 s = 10τ** (τ = 0.3 s, 24 dB/oct). This inherits the spot check's settling; it is not shaved, because under-settling on a fan's fast axis kills the high-F tones (STYLE burn #8).
- **Sensitivity: 50 µV = 5 kΩ full scale**, the spot-check scale. Worst corner is R(n = 1.2, 10 T) ≈ 105 Ω (run 5) × ~10 MR (run 6) ≈ 1 kΩ ≈ 0.2 FS.

**Price.** Measured, not inherited. Per point = fast_delay + 0.10 s of reads (run 5: 1.10 s at fast_delay 1.0). Per row: +3 s magnet settle (run 6), +3 s slow_delay, +1.6 s flyback.
- Grid: 3913 pts × 3.1 s = 3h22m.
- Row overhead: 91 × 7.6 s = 12 min.
- Ramp 1 → 10 T: 66 min. Positioning 0 → 1 T: 7 min.
- **Total ≈ 4h50m**, ending at 10 T with the gates parked at 0.

**Coverage trade.** Electron side and D = 0 only. The hole side is excluded because it is validator-limited to the exception regime. The low-n light partner (< 3 T for n < 2) is not resolvable in any window this rig reaches; the claim rides on the heavy tone and the F_L-tone trajectory.

**Checkpoints.**
1. **First rows** (B = 1.00–1.02 T, ~15 min in, after the 7 min positioning). Check: sr1 fs < 0.5, R(n) near the run-5 anchors (55 → 105 Ω plus 1 T MR), drain ≈ 9.9 nA, no leak beyond the known flyback transient, T at base. Rail or dead channel means abort.
2. **Row ~30** (B ≈ 1.4 T, ~1h45m in). Look for oscillations emerging across n.
3. **Row ~60** (B ≈ 2.5 T, ~3h15m in). Interim per-column FFT on the landed 1.0–2.5 T record (δF ≈ 1.7 T): heavy tone vs F_L across n. Continue, or abandon if nothing has appeared.

Guards trip on gate leak > 1 nA and on T > 2.5 K for 3 consecutive points.
