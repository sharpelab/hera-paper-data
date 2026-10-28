## HERA — Step 4: Landau fan A at D = 0 (`landau-fan`), n −1.25 → +3.25×10¹², B 1 → 10 T

**Why this step (plan step 4).** Spot runs 6 and 7 show strong SdH at D = 0 on both carrier sides, so a fan is worth running at this T_e. Electron side: run 6 at n = +3.2×10¹², where F_L is 33.1 T on the geometry-prior scale. Its tones are about 30 T, which dominates above 3 T, and about 7.5 T, which persists to 0.3 T. It also has 14–15 T and 22 T tones (harmonic or combination), and Rxx drops to about 0 at 6.0 and 7.2 T. Hole side: run 7 at n = −1.2×10¹² (F_L 12.4 T) has tones at 12.3–12.9, 6.6 and 4.7 T. From one density this can't be read uniquely: 7.5 + 30 = 1.13 F_L. That fits three readings:
- an ABAB light/heavy pair, with the absolute lever arm 13 % above the 9.5 nm prior;
- an ABCA singleton, plus a pocket, harmonic or region-B tone;
- a mixed structure.

What separates them is the n-dependence. The fan gives:
1. per-column FFT **F_i(n)**: how many surfaces there are, the slope of each, whether ratios hold fixed (harmonics do) or not (distinct bands), ΣF_i against F_L, and where a second band sets in;
2. the QH-minimum lines n = ν·eB/h through the CNP, which give an **absolute n calibration** independent of stacking (the brief requires the n-scale to be established in-session);
3. the high-B LL crossing pattern.

**Grid.**
- **Fast axis:** (V_tg, V_bg) co-swept along D = 0 with the run-5 calibration (same CAL as runs 6/7). This covers the **whole D = 0 window** inside the validators: n = −1.25 … +3.25×10¹², TG-limited at both ends (V_tg −0.291 / +0.998 V). 91 points, 0.05×10¹² apart.
- **Slow axis:** B from 1 to 10 T, uniform in 1/B at Δ(1/B) = 1/120 T⁻¹ up to 4.8 T (F_Nyquist 60 T, which covers the fundamentals up to F_L × 1.13 ≈ 38 T), then 0.2 T steps to 10 T for the high-B LL structure. 122 rows. Resolution over 1–10 T is ΔF ≈ 1.1 T.
- **Settings:** `fast_delay` 1.0 s, as in the run-5 calibration (1.10 s/pt). With τ = 0.3 s at 24 dB this lags about one point along n, the same direction every row, so it's corrected afterwards. sr1 fixed at 100 µV (10 kΩ full scale) so the D = 0 CNP has room if it goes insulating at high B; a rail on a few CNP columns is accepted.
- **Guards:** automatic trips on gate leakage (|I| > 1 nA on either gate) and on T_sample > 2.5 K for 3 consecutive points. On any exit the gates return to 0 V. On completion the field stays at 10 T: Fan B, at D ≠ 0 (plan step 5), rides it down so the field is never re-traversed.

**Coverage trade.** No rows below 1 T. The main tones start at 1.4–1.9 T, and below 1 T is mostly background. Adding 0.7–1 T would cost about 40 more rows (+1.3 h) for ΔF 1.1 → 0.75 T, which isn't needed to separate tones 7 T apart. D ≠ 0 is Fan B's job.

**Price.** The 0 → 10 T ramp floor is 73 min. On top of that come 122 rows × (91 × 1.14 s + ≈ 11 s for flyback, settle and slow_delay) ≈ 3.9 h. That sums to 5.1 h; the headline figure, with the session's observed overrun, is **≈ 5.5 h**. Time points along the run:
- B reaches 2 T at about 2.2 h;
- B reaches 4.8 T at about 3.6 h.

**Checkpoints.**
- **First rows** (after the 7 min ramp to 1 T):
  - I_drain ≈ 9.9 nA, no rail;
  - gate currents at their pA offsets, TG at about −100 pA with a flyback transient that's expected;
  - R(n) at 1 T should peak near n ≈ 0 at a few hundred Ω, consistent with the run-5 D = 0 row.
- **Around 2 T** (row 60, ≈ 2.2 h): a partial per-column FFT over 1–2 T. The light tones should already be visible, and I kill the run if nothing oscillates anywhere in n.
- **Around 4.8 T** (row 96, ≈ 3.6 h): full-resolution F_i(n). By this point the stacking read is mostly in hand; the rest of the run adds the high-B LL crossings and the ν-line calibration.
