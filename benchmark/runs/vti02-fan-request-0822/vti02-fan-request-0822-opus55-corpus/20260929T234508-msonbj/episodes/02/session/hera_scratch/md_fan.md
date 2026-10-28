## HERA — Step 4: Landau fan for the stacking call (`landau-fan-vti`, `tetralayer-stacking-fs-count` Step 4)

**Why this fan.** Spot check run 6 (electron side, n = +3.2×10¹², ana cells 14–15) shows strong SdH with onset ≤ 1.0 T and tones at 7.4, 22.2 and 29.5 T; F_L is 33.1 T. The 7.4 T tone sits on the ABAB light branch at scale ≈ 1. On one trace, though, {22.2, 29.5} can't be told apart between two readings: 3×/4× harmonics of 7.4 T, or an ABAB heavy tone plus its sum/breakdown tone. The investigation names this trap (the ABAB ratio drifts through 3×). The **fan's per-column F(n)** is what discriminates:
- a harmonic tracks k·f₁(n);
- the ABAB heavy branch tracks its own Onsager curve (≈ 7.2 T per 10¹²);
- an F_L singleton tracks 10.3 T per 10¹²;
- the partition f₁ + f₂ = F_L(n) either holds across density or it doesn't.

The fan goes on the electron side because the hole side of the D = 0 line stops at −1.27×10¹² (TG limit). That is the near-CNP exception regime, where run 7's pair is not separable.

**Design (floored per `landau-fan` step 1).** Fast axis: a paired n-line at D = 0 (run-5 cal), **n = +1.75 → +3.24×10¹², 37 points**. It ends at n_hi, 5 mV under the TG limit, and includes the spot-check density.

- *B axis:* **1.0 → 10.0 T, uniform in 1/B, 91 rows**. Δ(1/B) = 0.01 T⁻¹ is inherited from run 6, giving Nyquist 50 T against F_L(n_hi) = 33.5 T (1.5× margin, 3 samples per F_L period).
- *B_lo:* **1.0 T** = `sdh_onset().onset_b` on run 6's 10 mT segment. It is censored there, so it is a lower bound. The heavy tone's onset is 1.4 T and the 29.5 T tone's is 1.8 T.
- *n axis:* ray period at 1 T is 0.097×10¹², so Δn = 0.041 gives 2.3 points per period. That stays ≥ 2 even with a +15% lever-arm scale error.
- *Lock-in:* sensitivity **50 µV** (5 kΩ FS), inherited. Worst corner is n = 1.75 at 10 T, estimated 0.8–1.2 kΩ (R₀ = 80 Ω from run 5, times run 6's ×10 MR), i.e. ≤ 25% FS. τ = 0.3 s / 24 dB, read and asserted, not set. fast_delay 2.1 s = 7τ (rig-card settling floor for 24 dB).
- *Resolution:* δF = 1.1 T. Heavy vs F_L separation runs from 2.8 T at n = 1.75 to 7.4 T at n = 3.24.

**Coverage trade, stated.**
- **Excluded:** the hole side (unreachable at discriminating |n|); n < 1.75 (light tone under 2.5 periods, heavy within ~2 T of F_L, nothing to discriminate); n > 3.25 (TG limit).
- **Light tone:** it gets ≥ 5 periods only for n ≳ 2.65, and 2.5–5 periods over 1.75–2.65. There the fan reads mainly the heavy/F_L trajectories, and the partition sum is claimed for n ≳ 2.3.
- **Not bought:** buying 5 light periods at n = 2.0 would need B_lo ≈ 0.66 T. That costs +56 rows and +11 columns, about +80% (+2h45m), and the light tone's onset below 1 T is unmeasured (run 6 below 1 T was undersampled).

**Price.**
- grid: 3367 pts × 2.22 s = 125 min
- magnet traverse 1 → 10 T: 66 min
- positioning 0 → 1 T: 7 min
- row overhead: 91 × ~8 s = 12 min
- total: **≈ 3.5 h modeled**; ETA priced 5–10% over.

Endpoint: **field stays at 10 T** so the next step (the LK mass split) rides down from there. Gates stay at n = +3.24, D = 0.

**Guards (E1, auto-abort):** gate current > 1 nA; T_sample > 2.0 K; thermometry logfile stale at any row start; more than 10 points with sr1 above 90% FS. Preconditions asserted: T at base, B ≈ 0, V_si = 0, PS/output on, nplci 1, τ/slope/drive as priced.

**Checkpoints (via `hera-watch`):**
1. **First rows** (+9–12 min, B = 1.00–1.02 T): Rxx scale ~60–100 Ω, sr1 fs, drain current ≈ 9.9 nA, gate currents at their pA offsets, T.
2. **Row ~30** (+55 min, B ≈ 1.4 T): re-form the partial fan and look for rays. Abandon if there is no oscillatory structure, which would contradict run 6.
3. **Row 50** (+1h30m, B = 2 T): partial per-column FFT over 1–2 T. Does the light tone track across n?
4. **Completion:** full per-column FFT, model overlay and Luttinger check in ana.
