# Ground truth — read of the latest sweep (`data/0191`, the Landau fan)

Layer-A answer key: the correct read of the fan at the cut. A **floor** (must-see
findings), not an exhaustive key. Truth source: the generator record
(`$HERA_DATA/tetralayer-synth-validation/mislabeled_N/truth.json`) and the
rung-3a mechanical results (`.../RESULTS.md`).

- **What it is.** A D ≈ 0 `multimegasweep`: field slow (uniform in 1/B, to ~3 T),
  a paired-gate n-line fast (hole side, n ≈ −0.8 … −6.0 × 10¹²). Reconstruct
  `Rxx(B)` per column from the TSV as `sr830_{2,3}_X / sr830_4_X`; `plot.png` is
  the live monitor.

- **An asymmetric two-tone peak set summing to F_L (must-see).** At design
  densities (|n| ≳ 2–3 × 10¹²) per-column FFT resolves **two tones whose
  frequencies sum to F_L = (h/4e)·|n|** — a **high-frequency tone just below F_L
  (≈ 0.83–0.86·F_L)** and a **low-frequency partner (≈ 0.14–0.17·F_L)**:
  - n ≈ −3.5: ~31 T + ~5 T ≈ 36 T = F_L.
  - n ≈ −6.0: ~51 T + ~11 T ≈ 62 T = F_L.
  **Classify on frequency, not amplitude:** the near-F_L (heavy, larger-mass)
  tone is **Dingle-weak** (~few % of peak power), while the low-frequency
  (lighter-mass) partner is the **amplitude-dominant** peak — the inverse of the
  frequency ordering. Both clear the noise floor and **track their own Onsager
  curves across n** (a cross-column consensus, not a one-column fit) — genuine
  Fermi surfaces, not a damped-singleton-plus-noise artifact. The Luttinger sum
  (not the amplitudes) is what pins the pair.

- **This matches neither 4L template (the decisive point).** ABAB-4L is a
  **near-even** pair (≈ 0.6/0.4·F_L); ABCA-4L is a **singleton at F_L**. A big
  tone near F_L (below it) with a *small* resolved partner is the **trilayer ABA
  (ML + BL) template** — the ML light pocket + BL heavy pocket of Bernal
  trilayer.

- **Degeneracy.** g = 4 symmetric metal (Σf = |n|).

Limitations to name (don't penalize): the agent need not name "ABA trilayer"
verbatim — the floor is recognising the peak set fits **no 4L template** and that
absolute layer number is the suspect (adjacent-N). Live-monitor PNG (re-form from
TSV).
