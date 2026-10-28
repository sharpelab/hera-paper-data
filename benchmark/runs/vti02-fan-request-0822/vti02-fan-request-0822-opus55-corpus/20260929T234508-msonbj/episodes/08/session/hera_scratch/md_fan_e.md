## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`) — n 1.5–3.2×10¹² × B 1–8 T, uniform in 1/B

**Why this fan.** Run 6 (n = +3.2×10¹²) shows a clean tone set at ≈ 7.3 / 14.8 / 22.3 / 29.5 T against F_L = 33.1 T (ana, runs 6–7). At one density that set is ambiguous. It could be:
- an ABAB pair (7.3 + 22.3 ≈ 29.6 = F_L at a global scale of ≈ 0.89) plus a sum tone,
- a 7.3 T harmonic comb, or
- a singleton at F_L from the region-B domain.

The three readings separate only through their **n-dependence**. The ABAB heavy tone follows its own Onsager curve (dF/dn ≈ 0.7 × h/4e), a harmonic tracks k·f₁(n), and an ABCA singleton tracks F_L(n). Across this window they part by ≳ 5 T against δF ≈ 1.1 T. This is investigation Step 4/5: per-column FFT, peak set vs F_L, and tone trajectories in one object.

**Design** (`landau-fan` step 1 checks, numbers in `hera_scratch/fan_design.py`):
- **B axis:** `field_invB(1.0, 8.0, 117)`, Δ(1/B) = 0.00754 T⁻¹. That gives F_Nyq = 66 T, **4 points per period at F_L,max = 33 T**. I used 1/4 rather than the 1/3 minimum so the 2nd harmonic of an F_L-ish tone (≈ 60–66 T) cannot fold back onto F_L.
- **B_lo = 1.0 T.** This is the low edge of run 6's fully sampled record. There the 7.3 T tone is `censored` (still alive), and it sits below every claim-carrying onset (22 T tone at 1.40 T, 29.5 T tone at 1.76 T). It also gives the light partner ≥ 5 periods at the top densities.
- **B_hi = 8 T.** δF = 1.14 T (vs 1.11 T at 10 T). The top 2 T would cost ~30 min of traverse up and back for 2 rows in the deep-QH, Hall-admixture corner.
- **n axis:** 3.2 → 1.5×10¹², 39 points, Δn = 0.045×10¹². That is 2.2 points per LL ray at B_lo (ray spacing 0.097×10¹² at 1 T).
- **Dynamic range:** the worst corner is low n × high B. R₀(n = 1.5, D = 0) ≈ 86 Ω (run 5). With run 6's ×10 MR that is ~0.9 kΩ, so the inherited 50 µV = 5 kΩ full scale leaves ≳ 4× headroom. A clip counter logs any |X| > 90 % FS, and clipped high-B tails get truncated per column in analysis.
- **Settling:** τ = 0.3 s at 24 dB/oct (asserted). fast_delay = 2.1 s = 7τ, the 24 dB floor. slow_delay = 3 s = 10τ after each flyback.
- **Guards:** automatic interrupt on |I_gate| > 1 nA or T_sample > 2.5 K.

**Coverage trades, stated:**
- **Hole side excluded.** Its D = 0 line stops at n ≈ −1.1 to −1.3×10¹² (TG −0.3 V limit), which is the semimetal exception regime (run 7). Full coverage would need a wider TG limit, which is session-banned.
- **n < 1.5×10¹² excluded.** Below that the ABAB heavy tone sits within δF of F_L, so those columns carry no discriminating power. Adding 1.0–1.5 would cost ~+30 %.
- **B < 1 T excluded.** Pinning the light-tone onset lower would add ~2 h of rows and n-points, for partner periods at low n that investigation Step 2 already rates unresolvable.

**Price:** 117 rows × (39 × 2.2 s + ~5 s turnaround) ≈ 2.9 h, plus ~58 min of magnet (run-6 calibration: 373 s/T + 3.7 s per set, including the 0 → 1 T positioning). Rig timing actuals run 5–10 % over.

**Endpoint:** gates are parked at 0 V and the **field stays at 8 T**, so the follow-up (LK mass split, or a firming cut) rides it down.

**Checkpoints:**
1. **First rows (~1 T).** sr1 in range, R(n) near run 5's D = 0 profile (56–86 Ω), no leakage, T at base.
2. **Row ~44 (1.5 T, ~1 h 15 m in).** Landed-row sanity: streaks, rails, drift.
3. **Row ~80 (2.5 T, ~2 h 10 m in).** Interim per-column FFT on the landed 1.0–2.5 T record (δF ≈ 1.7 T). The heavy-tone vs F_L trajectory should already be visible. Abort if the n = 3.2 column fails to reproduce run 6's tones.
4. **Completion.** Full read.
