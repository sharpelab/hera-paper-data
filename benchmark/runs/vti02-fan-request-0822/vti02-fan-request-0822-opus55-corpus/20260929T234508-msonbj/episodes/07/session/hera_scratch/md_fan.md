## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`) — per-column SdH FFT for the stacking call

The spot checks (runs 6 / 7, ana cells 14–15) favour the **electron side**. It is the only side that reaches the design density at D = 0. At n_cal = +3.2 its record carries 7.3 / 22.3 / ≈30 T tones, with F_L,true = 30.0 T from the QH-minimum scale (S = 0.906). One density cannot say whether 22.3 T is a real heavy pocket, as in an ABAB pair (7.3 + 22.3 ≈ F_L,true), or 3 × 7.3 T, or whether the 30 T tone is a singleton. **The fan answers that from each tone's n-dependence** (investigation Step 4/5).

**Design, lever by lever (landau-fan step 1):**
- **B_lo = 1.0 T.** This is the `sdh_onset` value on run 6's 10 mT record. It is censored, so the true onset is ≤ 1 T.
- **n window: n_cal +1.50 → +3.20×10¹².**
  - The top column **repeats the run-6 spot on a different grid** (uniform-1/B vs uniform-B). That is the free grid-change / alias check.
  - Over the window the model ABAB heavy/F_L runs 0.885 → 0.79, while ABCA stays at 1.0. The model also puts 3 × light at 4.9 → 19 T, well apart from heavy at 12.4 → 23.6 T.
  - Below 1.5 the ABAB heavy tone approaches F_L (the exception regime), so it cannot discriminate.
- **N_n = 35 (δn = 0.05).** The LL ray spacing at 1 T is 0.107×10¹² in cal units, so this gives ≥ 2 samples per ray period.
- **B_hi = 6 T.** δF = 1/(1/B_lo − 1/B_hi) = 1.2 T. At n_hi the heavy tone is ~6 T from F_L,true (≫ 2δF). Going to 10 T only adds QH-regime rows and 29 min of traverse (δF 1.11 T).
- **B axis: uniform in 1/B, 85 rows, Δ(1/B) = 0.0099 = 1/(3·F_L,cal(n_hi)).** At the low edge that is the spot check's 10 mT. With 3 samples per period, the 2nd-harmonic alias of the ≈30 T tone lands at ≈41 T, outside the band. Any in-band harmonic alias shows up by its reversed n-slope.
- **Dwell: fast_delay 2.4 s = 8τ** (τ = 0.3 s at 24 dB/oct; the rig floor is 7–10τ). slow_delay is 3 s = 10τ after the flyback.
- **Sensitivity: sr1 50 µV (5 kΩ FS).** R(B = 0) along the line is 58–84 Ω (run 5) and run 6 reaches ≤ 125 Ω for B ≤ 6 T, so the low-n × 6 T corner has > 10× headroom. Auto-guards: leak > 1 nA, T > 2 K, or ≥ 10 railed points interrupts the cell.

**Coverage trade, stated:**
- **Hole side excluded.** At D = 0 it is TG-capped at −1.27×10¹², inside the near-CNP exception regime, and run 7 is a preview only.
- **Light partner, ≥ 5 periods:** resolvable only for n_cal ≳ 3.0 (f ≳ 6 T in [1, 6] T).
- **Below 1.5:** the n-range down there carries mainly the heavy-tone position, the partition via F_L, and the per-column QH ladder (scale pin).
- **Price of more light-tone reach:** extending B_lo to 0.8 T is +25 rows (≈ +55 min), and it needs a measured sub-1 T onset first.
- **Carried confound:** region B (+0.43×10¹², series) may add tones at ×1.13.

**Checkpoints:**
- **First row** (1.0 T, ~9 min in): R 50–90 Ω, no rail, I_drain ≈ 9.9 nA, gate currents at the pA floor, T at base. Abort there on any failure.
- **Row ≈ 50** (B ≈ 2.0 T, ~1h35m): partial per-column FFT on [1, 2] T. The question is whether the ~22 T tone tracks its own Onsager curve or 3 × light across n. Continue unless the columns are flat or railed.
- **Row ≈ 70** (≈ 3.1 T, ~2h20m): same read, sharper.

**End state:** gates parked at 0 and the **field left at 6 T**. The LK mass-split series (Verify, `temperature-dependence-vti`) rides down from there; no re-traverse.
