## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — B 1 → 9 T × n −1.25 … +3.25×10¹²

**Plan step 4** (`hera_scratch/plan.md`), requested by the operator.

**Why this fan.** The spot checks (runs 6/7, ana) lean two-band. The electron side at n = +3.2 has a 7.1 + 30.0 T pair; ABCA predicts a single F_L. But the pair sums to 37 T, not F_L = 33.1 T. One density cannot tell a light + heavy ABAB pair from region-B tones, since the second, parallel CNP ridge is offset by +0.43×10¹². It also cannot tell a region offset from a c_tg-scale error.

The fan resolves this by measuring F(n) for every tone:
- the number of tones on each side;
- whether their slopes sum to dF_L/dn (an absolute density calibration that does not depend on geometry);
- where each tone extrapolates to F = 0: n_A = 0 means region A, n_A = −0.43 means region B;
- e/h symmetry (ABCB flag) and the LL-crossing pattern in the quantum-Hall range.

**Design.**
- **Fast axis:** n along the run-5 D = 0 line, TG and BG co-swept. 181 points at 0.025×10¹², which is ≥ 4 points per LL period at 1 T.
- **Slow axis:** B.
  - Uniform in 1/B from 1 to 4 T: 64 rows, Δ(1/B) = 0.012 T⁻¹, ≥ 2.5 samples per period up to F = 34 T. This feeds the per-n FFT, with δF ≈ 1.1 T over 1–9 T.
  - Then 0.2 T steps from 4.2 to 9 T: 25 rows, for the QH picture.
- **Direction:** ascending, because the magnet sits at 0 T. It ends at **9 T**, where step 5 (the D-dependence at high B) starts, so no re-traverse.
- **Lock-in:** sr1 fixed at 100 µV (10 kΩ full scale); runs 6/7 peaked at 590 Ω. fast_delay 1 s at τ 0.3 s / 24 dB, the same as gatemap run 5; the resulting lag is ~1 point along n, the same in every row.
- **Guard:** trips at |I_gate| > 1 nA or T_sample > 3 K. Gates park at 0 on exit; the field holds.

**Coverage trade.**
- **n:** the TG validator bounds the D = 0 line at both ends, so the hole side reaches only F_L ≤ 12.9 T. There ABCA's heavy band is LK-suppressed at T_e ≈ 8 K, so the hole side is weaker evidence by construction.
- **B from 1 T, not 0.5 T:** tones below ~5 T lose their first periods. The extra 0.5–1 T rows would cost ≈ 2 h and only help the light tones.

**Price** (measured rates): run 5 gives 1.10 s/pt in-row and 5.8 s row turnaround; run 6 gives 3 s magnet settle per set. 89 rows × (181 × 1.10 + ~9.5 s) = 5.2 h, plus 58 min ramping 1 → 9 T and 7.5 min for 0 → 1 T, total 6.25 h. The headline is +7 % on that.

**Checkpoints.**
- **First rows** (~15 min in): sr1 below full scale away from the CNP; no leakage; I_drain ≈ 9.9 nA. R at n = +3.2 / −1.2 near 1 T should match runs 6/7 (13 Ω / 110 Ω); a mismatch means the gate or density state has drifted, so abort.
- **Every ~75 min:** hera-watch digests (rails, leakage, T).
- **At B = 4 T** (row 64, ~4 h in): interim per-n FFT over 1–4 T gives the F(n) tone census. Call there: continue 4 → 9 T (~1.6 h more, QH picture) or stop and go to step 5.
