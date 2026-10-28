## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, per `tetralayer-stacking-fs-count` Step 4)

**What it decides.** Spot check run 6 (n = +3.2) returned {7.3, 22.3, 29.6 T}, with 7.3 + 22.3 = 29.6 ≈ 0.90·F_L. From one density that set fits two readings (ana, runs 6 + 7):
- an ABAB pair plus a breakdown sum tone;
- a singleton plus comb/intermodulation products.

The fan measures the **n-dependence** of each tone across n = +1.80 … +3.25×10¹². A harmonic tracks k·f exactly. An ABAB pair drifts in ratio (model heavy/F_L 0.78 → 0.84) and sums to F_L at every column. The same object pins the global scale, and gives the B-window split for the F_L-tone origin.

**Side and coverage.** Electron side only. It is the only side whose D = 0 line reaches the design densities |n| ≳ 2–3×10¹² inside the validators (top point n = 3.25 → V_tg = 0.998 V against the 1.0 V limit). The hole side is cleaner by onset (0.71 T vs ~1.2 T), but its D = 0 reach ends at −1.27, inside the exception regime. **Excluded:** a hole fan (−1.27…−0.6, ≈ 2 h), deferred. **Low edge n = 1.8:** below it the heavy tone and F_L converge within δF. At the low-n end ν = 8 / 12 / 16 fall inside 10 T, which gives the Step-6 layer-number check.

**Design (landau-fan step 1, checks computed):**
- **B_lo = 1.0 T.** This is `sdh_onset` on run 6's well-sampled record. It is censored at the record edge by the weak 7.3 T tone; the fast tones die out at ~1.15–1.2 T. The partner at ≥ 5 periods holds for n ≳ 2.7 at scale 1.
- **B_hi = 10 T.** The B-window split needs the high-field half, and ν = 8 at the low-n end needs it too. The fan ends where the next step (LK ladder / firming fan riding down) starts.
- **B grid — deliberately not `field_invB`.** Uniform 1/B at 0.0099 T⁻¹ (⅓-Nyquist on F_L(3.25) = 33.6 T) up to 1.62 T, then geometric at ΔB/B = 1.6 %, so the local Nyquist is 31·B. Run 6's harmonic comb reaches ~23·B (130 T at 5.6 T). A uniform 1/B grid at the F_L rule would alias 81–130 T onto 20–29 T, exactly the tones under test. Resolution: δF ≈ 1.1 T on the record above 1 T.
- **n axis:** 32 pts, Δn = 0.047 ≤ 0.048, the ray-Nyquist floor (2 pts/ray at 1.0 T).
- **Dwell:** fast_delay 2.1 s = 7τ (τ = 0.3 s, 24 dB; the per-column read carries the signal).
- **Sensitivity:** sr1 fixed at 50 µV = 5 kΩ FS. The worst corner (n = 1.8, 10 T) is estimated at ~1.5 kΩ ≈ 30 % FS; a per-row RAIL WARN prints if |X| > 0.9 FS.
- **Price:** 155 rows × (32 × 2.25 s + 7 s turnaround) ≈ 3 h 25 m, plus 10 T of blocking ramp ≈ 1 h 13 m. About 4 h 40 m, headline 4 h 55 m with the session's ~5 % over-run.

**Guards and checkpoints.** Preconditions: base T, B ≈ 0, Si 0, heaters off, drive / τ unchanged. Leak trip at 1 nA on either gate interrupts. Checkpoints:
- **First rows (~10 min):** signal level vs run 6 at 1 T (≈ 13 Ω at n = 3.2), gate currents, T.
- **~2.5 T (~1 h 45 m):** SdH present across columns.
- **~4.5 T (~3 h):** partial per-column FFT on 1–4.5 T. Do the 22 / 30 T tones disperse with n, and do they track k·f or the Onsager curves? If there is no tone content, abandon.
- **~7 T:** rail check at the low-n corner.

**End state:** B = 10 T, gates on the D = 0 line at n = 3.25.
