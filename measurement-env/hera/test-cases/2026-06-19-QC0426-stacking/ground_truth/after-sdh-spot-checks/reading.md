# Ground truth — read of the latest sweep (`data/3`, electron SdH spot check)

Layer-A answer key: the correct read of the freshest sweep at the cut.

- **What it is.** A fixed-(n = +5e12, D = 0) magnetic-field sweep, B 4→0 T at
  8 mT (501 points), electron side; `sr1`/`sr2` are Rxx, `sr3` Rxy, `sr0` the
  transimpedance current. Rxx must be re-formed from the TSV as `sr{1,2}_X /
  (sr0_X / sr0_gain)`; the `plot.png` is the live monitor.
- **Signal.** Clean Shubnikov–de Haas oscillations, **low onset (~0.4 T)** once
  the smooth MR background is removed (in B, not 1/B). The ΔRxx trace beats — the
  two-tone fingerprint.
- **Tone content (the read that matters).** A **~8 T tone + a cluster near F_L
  (~44–48 T)** on both `sr1` and `sr2`, with `8 + ~44 ≈ 52 = F_L` — a
  Luttinger-consistent ML(~8 T) + BL(~44 T) two-pocket partition. Decisive that
  **≥ 2 Fermi-surface frequencies coexist** (ABA two-pocket signature, or
  ABA+ABC mixed); an ABC-singleton is excluded on these channels. The exact
  partition / a possible tone *at* F_L (mixed-domain test) is for the fan.
- **Why electron.** Cleaner and higher-mobility than the hole side (run 2, which
  clipped at ~2.3 T and partly aliased) — so the fan goes here.
- **R-scale for fan design (load-bearing).** The spot check is metallic
  (low-Ω) at n = +5e12; its `sr1/sr2 = 1e-5` sensitivity was sized for *that*
  R-scale. A fan spans down to n ~ 1e12 at B up to 4 T, where Rxx is far larger —
  the spot-check sensitivity does **not** cover the fan's worst corner. This is
  the fact a correct fan design must act on.
- **Settling.** The spot check used a full ~2.2 s (7·τ) dwell — the amplitude
  reference. SdH amplitude (the FS-count observable's strength) is settling-
  sensitive on a per-point sweep.

Limitations to name: live-monitor PNG (re-form from TSV); VTI base T ≈ 1.2 K.
