## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`) → per-column FFT for the stacking read

**Why this fan.** Run 6 (n = +3.2×10¹²) shows tones at 7.5 / 14.9 / 22.3 / 29.9 T against F_L = 33.1 T. Three readings fit that one density: a harmonic comb of 7.5 T; an ABAB pair (7.5 + 22.3 = 29.8) plus a sum/breakdown tone at a lever-arm scale of ≈ 0.90; or an ABCA singleton at 29.9 T plus a 7.5 T comb. The density dependence separates them (Steps 4–5 of the investigation). A harmonic tracks k·f₁ exactly. The ABAB heavy/light ratio drifts from 3.5 (n = 3.2) to 4.8 (n = 2.0) (model). An ABCA singleton has F ∝ n with no partner, and a sum tone equals f₁ + f₂ in every column. The electron side is the only side that reaches design density: the hole side of D = 0 stops at −1.27×10¹², and run 7 there sits in the near-CNP exception regime.

**Design (floored, per recipe step 1).**
- **n window:** [2.0, 3.2]. The top is 16 mV under the TG limit. Below 2.0 the ABAB partner (< 3.2 T) can't be resolved and the heavy tone mimics a singleton (investigation Step 2).
- **B_lo = 0.70 T.** `sdh_onset` on run 6's 10 mT record finds the light tone censored, still above threshold at 1.0 T. Scaling from the 22.3 T tone's measured SNR-vs-B, which follows LK-thermal damping at T_e ≈ 8 K, gives SNR ≈ 15 for m* ≈ 0.027 at 0.7 T. B_lo = 0.7 gives the partner ≥ 5 periods down to n ≈ 2.2; B_lo = 1.0 would stop that at 2.8.
- **Two uniform-1/B segments.** Below 1.25 T, Δ(1/B) = 0.030: only the light tone is alive there (run 6 heavy-tone onsets are 1.40 and 1.76 T), and it gets 3.9 points per period. Above 1.25 T, Δ(1/B) = 0.010, which gives 3.0 points per period at F_L(3.2) and 2.7 at region B's F_L (n + 0.43). This matches the spot check's Δ(1/B).
- **δF:** 1.6 T for the heavy tone and 0.75 T for the light tone. The heavy-vs-F_L gap is 3.2–7.3 T across the window.
- **n-axis sampling:** Δn = 0.050, sized to each tone's own period along n (B / (dF/dn)) at that tone's onset. That gives 3.4 points per period for F_L-slope components at 1.76 T, 3.8 for the heavy tone and 4.5 for the light tone. The recipe's total-ray check at B_lo would call for Δn 0.034 (+12 columns, +40 min), but it guards components that are dead below 1.25 T.
- **B_max = 10 T** buys three things: the ν-ray (Středa) ladder, a scale-free lever-arm pin and 4L-vs-3L check that is independent of the FFT read; the high-B half for the F_L-tone-origin split; and a start point for the LK series to ride down.
- **Acquisition,** inherited from runs 6/7: sr1 at 50 µV, a 5 kΩ full scale. The worst corner (n = 2.0, 10 T) is estimated at ≤ 1.5 kΩ. The state0 replay left sr1 at the 2 µV bring-up value; the cell sets 50 µV. τ is 0.3 s at 24 dB/oct, with fast_delay 2.4 s (8τ, 4 % step residual).

**Coverage trade.** Excluded: the hole side (validator-limited) and n < 2.0 (unresolvable by design). Extending down to n = 1.5 would cost about +40 min for heavy-tone curvature only.

**Checkpoints.**
1. **First rows (0.70 T):** R range vs full scale, drain current ≈ 9.9 nA, gate currents ≪ 1 nA, T_sample.
2. **B ≈ 1.25 T (+35 min):** check the n = 3.2 column against run 6 at the same (n, D). This is a free grid-change reproduction.
3. **B ≈ 2.5 T (~+1 h 30 m):** interim per-column FFT of the light tone, giving f₁(n) (comb vs pair).
4. **B ≈ 5 T (~+2 h 15 m):** FFT over the full claim window.

**Abort** on any of: sustained rail, leak trip, T_sample > 1.6 K, lost drain current, or an n = 3.2 column that disagrees with run 6. The field is left at 10 T.
