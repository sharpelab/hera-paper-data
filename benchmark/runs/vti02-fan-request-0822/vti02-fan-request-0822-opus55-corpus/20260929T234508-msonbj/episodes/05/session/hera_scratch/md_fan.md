## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`) for the stacking FS count (`tetralayer-stacking-fs-count`)

**Why this fan.** The spot checks (runs 6–7, ana) show strong SdH on both sides, but no single density can decide the call. On the electron side at +3.2×10¹² there are tones at ≈ 7.3 T and ≈ 29.4 T (0.90·F_L). Their ratio is ≈ 4, so they could be a harmonic comb, an ABAB pair (model 7.3 / 25.8 T), or ABCB/ABCA-like main tones plus something else. The fan settles it through **n-dependence**:
- A harmonic stays locked at k·f.
- Real pockets follow their own Onsager curves. At a fixed scale, the ~29 T tone rises by ≈ 11.6 T (ABAB heavy) versus ≈ 16.6 T (ABCA) across the window.
- The fan also pins the lever-arm **scale and n-offset** separately.

**Side, window, coverage trade.**
- **Electron side:** it is the only side that reaches the investigation's design densities (≳ 2–3×10¹²).
- **Hole side excluded:** the validators cap it at −1.27×10¹², inside the near-CNP exception regime. Run 7 already previews it.
- **n = 3.2 → 1.6×10¹² at D = 0 (run-5 calibration):**
  - The top end is the run-6 point, 16 mV under the TG limit. Sharing that density lets the fan be checked against the spot check (acquisition-quality comparison).
  - A factor of 2 in n gives the slope leverage.
  - Below 1.6 the model's ABAB heavy tone crowds F_L (≥ 0.86) and the partner drops under 2.3 T, unresolvable at this onset. The trade: extending to 1.2 costs +45 min and buys no discriminating column.

**Design numbers (recipe step 1).**
- **B_lo = 1.0 T.** `sdh_onset` on run 6 (B ≥ 1 T; its 50 mT steps below 1 T alias a 7 T tone) gives the 7.3 T tone *censored* at 1.0 T. So 1.0 T is a valid lower bound on the onset.
  - The ~29 T tone's onset is 1.76 T. At m* ≈ 0.06 and T_e ≈ 8 K it is LK-bound, so a lower B_lo buys it nothing.
  - B_lo = 0.8 T would cost ×1.6 (both axes).
  - Step A below pins the true onset for the analysis at almost no cost: it rides the 0 → 1 T ramp the fan needs anyway, ~14 min over a bare ramp.
- **B_hi = 10 T** (session cap). The binding case is the ABAB partner at the low-n end.
- **Sampling:**
  - **B axis:** uniform in 1/B with Δ(1/B) = 0.9/101 T⁻¹, i.e. Nyquist 56 T = 3 pts/period on the fastest observed fundamental (~37 T). **N_B = 102 rows.**
  - **n axis:** Δn = 0.047×10¹² ≤ ½ LL period at B_lo. **N_n = 35.**
  - **Resolution:** δF ≈ 1.1 T for tones alive from 1 T, ≈ 2.1 T for the ~29 T tone. Both are below the 3.7–5 T separations the claim needs.
- **Sensitivity:** fixed at **100 µV (10 kΩ FS)**. The worst corner (n = 1.6, 10 T) is estimated at 1.3–2.1 kΩ (R₀ = 84 Ω × low-n MR/QH), i.e. ≤ 21 % FS. Run 4's lesson: headroom before resolution.
- **Dwell:** fast_delay 1.8 s = 6τ at 0.3 s / 24 dB (per-column SdH fan). slow_delay 3 s = 10τ after each flyback.
- **Guards:** interrupt on gate leak > 1 nA and on T_sample > 1.7 K, with gates parked.
- **Endpoint:** the fan ends at **10 T** with gates at 0. The next step (LK mass split / firming) rides the field down.

**Price.** Timing calibrated on run 5 (1.10 s/pt at a 1 s dwell) and run 6 (3.1 s/pt at a blocking-magnet step).
- **Step A:** 261 pts × 3.1 s + 0 → 1 T ramp 7.3 min ≈ **22 min**.
- **Step B:** 3570 pts × 1.95 s = 116 min, + 9 T bare traverse 66 min, + 102 rows × ~8.5 s ≈ 14 min, = 196 min. Quoted **≈ 3 h 30 m**, which includes the session's ~7 % overrun margin.
- **Total ≈ 3 h 55 m.**

**Step A → B handoff.** Step B runs as soon as step A completes cleanly: no rail, no leak, oscillations consistent with run 6 above 0.8 T. Step A feeds the analysis (the onset, and a seamless 0.3–10 T uniform-1/B record at n = 3.2 joined with the fan's top column), not the design.

**Checkpoints.**
1. **First 3 fan rows** (~4 min in): R within FS, I_drain ≈ 9.9 nA, gate currents at pA, T at base.
2. **Row ~50** (B ≈ 1.8 T, ~1 h 10 m in): raw ΔR(n, B), with the n = 3.2 column checked against run 6 and step A.
3. **Row ~80** (B ≈ 3.5 T, ~2 h 05 m in): interim per-column FFT over 1–3.5 T to see whether the ~7 T tone tracks its own curve or ¼ of the main tone.

Abort on a rail, leak, or a featureless map.
