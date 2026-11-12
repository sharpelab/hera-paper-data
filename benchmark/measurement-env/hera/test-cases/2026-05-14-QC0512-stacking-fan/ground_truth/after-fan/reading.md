# Ground truth — read of the latest sweep (`data/0213`, the Landau fan)

Layer-A answer key: the correct read of the fan at the cut. A **floor** (must-see
findings), not an exhaustive key. Truth source: the generator record
(`$HERA_DATA/tetralayer-synth-validation/abab_breakdown/truth.json`) and the
rung-3a mechanical results (`.../RESULTS.md`).

- **What it is.** A D ≈ 0 `multimegasweep`: field slow (uniform in 1/B, to ~3 T),
  a paired-gate n-line fast (hole side, n ≈ −0.8 … −6.0 × 10¹²). Reconstruct
  `Rxx(B)` per column from the TSV as `sr830_{2,3}_X / sr830_4_X`; `plot.png` is
  the live monitor. Both signs of D ≈ 0 (this fan is the hole side).

- **Two fundamental Fermi surfaces partitioning F_L (must-see).** At design
  densities (|n| ≳ 2–3 × 10¹²) per-column FFT resolves **two tones, both below
  F_L**, whose frequencies **sum to the Luttinger line** F_L = (h/4e)·|n|:
  - n ≈ −3.5: ~14 T (light) + ~22 T (heavy) ≈ 36 T = F_L.
  - n ≈ −5.1: ~19 T + ~33 T ≈ 52 T = F_L.
  - n ≈ −6.0: ~22 T + ~40 T ≈ 62 T = F_L.
  Heavy/light ratio ≈ 1.6–1.8 (not the bare 0.72/0.28 decomposition-limit ratio —
  read the sum, not a fixed ratio). Each tone tracks its own Onsager curve across
  n (the partition sum holds algebraically column-to-column). This is the
  **ABAB two-pocket signature**.

- **A third tone at F_L that grows with B (the discriminator, must-see).** A tone
  sitting **at F_L** (= light + heavy) is also present; on a low-B vs high-B
  window split its power **strengthens toward high B relative to the
  fundamentals**. This is a **magnetic-breakdown sum-tone** (ABAB inter-block
  breakdown is symmetry-allowed), **not** a genuine chiral pocket at F_L. Reading
  it as an ABCA singleton is the trap.

- **Degeneracy.** g = 4 symmetric metal (tones sit at their g = 4 F_L positions;
  Σf = |n|).

Limitations to name (don't penalize): the breakdown tone is a high-B / short-
record feature — an agent that resolves the two fundamentals and flags the F_L
tone as origin-ambiguous (rather than fully nailing "breakdown") still has the
floor. Live-monitor PNG (re-form from TSV). The heavy (larger-mass) tone is
Dingle-weak — keyed off the noise floor, not a fraction of the peak.
