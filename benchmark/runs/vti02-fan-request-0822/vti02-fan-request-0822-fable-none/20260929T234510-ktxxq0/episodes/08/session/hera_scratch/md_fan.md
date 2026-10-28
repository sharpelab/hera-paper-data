## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.25 → +3.20×10¹², B 0.5 → 10 T

**Plan step 4** (operator-requested; `hera_scratch/plan.md`). Runs 6/7 (ana cell 15) show multi-band SdH on both carrier signs — e-side F ≈ 7.1 + ~30 T (sum 37 vs F_L 33.1), h-side tones 4.7–12.9 T — but a single-n FFT can't separate fundamentals from harmonics/breakdown or give the degeneracy partition. The fan's per-column F(n) slopes and the ν-gap wedges are the ABAB/ABCA/ABCB discriminant.

**Geometry.** Fast axis: n = −1.25 → +3.20×10¹² cm⁻² through the CNP, 131 pts (Δn = 0.034), co-swept (V_tg, V_bg) along the run-5-calibrated D = 0 line — V_tg −0.291→+0.984 V, V_bg −0.484→+1.166 V, all inside the committed validators. Slow axis: B ascending 0.5 → 10 T (magnet reads ~0, state0), **two-segment uniform-1/B grid, 133 rows**: Δ(1/B) = 0.0199 below 1.3 T (Nyquist 25 T — only tones ≤ 13 T are alive there, margin against harmonic aliasing) and 0.0096 above (Nyquist 52 T — covers the 30 T family + harmonics). Per-column ΔF = 1/(1/0.5 − 1/10) = 0.53 T.

**Coverage trade:** the hole side ends at n = −1.25×10¹² (TG −0.3 V validator) — the fan is e-side-rich by construction; full hole coverage does not exist inside the committed box. D ≠ 0 is not covered here (step 6 candidate, riding 10 T down).

**Sensitivity trade (stated):** sr1 at 100 µV (10 kΩ FS at 10 nA). The gapped CNP columns at high B may soft-clip (>10.9 kΩ) — accepted: a ν = 0 rail is itself a read, and the SdH evidence lives in the metallic columns, where 100 µV keeps the readback resolution the oscillations need (session-notes rail lesson, run 4).

**Dwell (bent knowingly):** fast_delay 0.7 s ≈ 2.3τ (τ = 0.3 s, 24 dB/oct) — a uniform ~1-pt lag along n, shifts all columns equally, F(n) slopes untouched (same argument as run 5's 3.3τ). Reads ≈ 0.1 s/pt async (measured, run 5: 1.098 s/pt at fast_delay 1.0).

**Price (honest):** 133 rows × (131 × 0.8 s + 6.5 s turnaround) ≈ 4.1 h + field 9.5 T @ 0.137 T/min = 69 min + 133 × 3 s settle + first ramp ≈ 1.3 h → 5.4 h; +7 % session-measured overrun → **≈ 5 h 50 m**, ending at **10 T, gates at the n = +3.2×10¹² end** (next step rides the field down — never re-traverse).

**Checkpoints** (hera-watch armed on `data --next --follow`): first 2 rows — signal level, no rail across the metallic range, gate currents at pA floor, T stable; then hourly digests; interim analysis at row ~63 (B = 1.3 T: apex + hole-side wedges visible?) and row ~101 (B ≈ 2.5 T: partial per-column FFT — two dispersing branches?). Abort (`nb-collab interrupt`) on: sustained gate current > 1 nA (in-cell guard also trips), wide-range railing, T_sample excursion > 1.6 K, or a featureless map by 2.5 T. Partial data keeps.
