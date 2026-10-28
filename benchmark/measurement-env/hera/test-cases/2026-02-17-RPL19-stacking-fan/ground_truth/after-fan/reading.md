# Ground truth — read of the latest sweep (`data/1840`, the Landau fan)

Layer-A answer key: the correct read of the freshest sweep at the cut. Written
as a **floor** (must-see findings), not an exhaustive key — the agent will often
out-detail it. Source of truth: the RPL_19 real-data validation memo
(`$HERA_DATA/tetralayer-rpl19-validation/MEMO.md`, §3, §5) and the device's
published fig-3 analysis.

- **What it is.** A 2D `multimegasweep`: field slow (B 0.6–5.0 T, 441 pts),
  a paired-gate (n, D) line fast (231 columns). Reconstruct `Rxx(B)` per column
  from the TSV as `sr830_{2,3}_X / sr830_4_X`; `plot.png` is the live monitor.
  **Compute (n, D) from the gate columns** via the card's lever arms — this fan
  sits at **D ≈ 1.0 V/nm**, `n ≈ 0.4–1.0 × 10¹²`. This is **not** the D ≈ 0
  symmetric-metal operating point the stacking investigation requires (must-see).

- **High-density region (n ≳ 0.78).** Per-column FFT shows a **single dominant
  SdH tone** whose frequency tracks **≈ 4·F_L**, i.e. `n_SdH = n` to ~1%
  (f_ν ≡ n_SdH/n ≈ 1.0). Examples: n ≈ 0.93 → ~39.6 T; n ≈ 0.82 → ~33.3 T
  (F_L ≈ 9.8, 8.6 T respectively). **The degeneracy audit reads this as isospin
  g = 1 — a quarter-filled, flavor-polarized metal** carrying the full density
  in one pocket. It is **not** a stacking singleton *at* F_L; reading the tone at
  F_L would misassign the density fourfold. (Decisive must-see: g = 1, tone at
  4·F_L, not a supra-F_L pocket and not an F_L singleton.)

- **Low-density region (n ≲ 0.6).** A **multitone** spectrum with tones whose
  `n_SdH > n` (f_ν > 1 — e.g. n ≈ 0.62 → 38 T giving f_ν ≈ 1.48, plus 28 T at
  f_ν ≈ 1.09), impossible for a simply-connected pocket in a g ≥ 1 metal.
  **This is an honest Luttinger failure — non-Onsager — reported as a state, not
  refined or forced into a stacking template.** (~46 columns fire the
  non-Onsager flag.)

- **Contact-robust.** `sr830_2` and `sr830_3` (the two long pairs) give the same
  reads.

Limitations to name (don't penalize): live-monitor PNG (re-form from TSV); the
agent need not reproduce the paper's exact f_ν numbers — the qualitative reads
(g = 1 at high n; non-Onsager below) are the floor. The hole side / other fans
are not on this cut.
