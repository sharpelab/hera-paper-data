# Tetralayer synthetic-fan validation — results

SdH-FFT pipeline (RMG-snapshot conventions) run on synthetic fans from the validated `fs_count_b0` band model. Generator: `hera/models/tetralayer_fs_count/synth_fan.py`; evaluator: `synth_eval.py`. Data + truth under this directory.

Frequency error is over the tones the analysis *claims* on a resolved column (a confident call); noise-limited low-|n| columns make no claim. `resolved` = columns yielding a definite call.

## Per-case verdicts

| case | truth | recovered | s_true | s_fit | freq err (med/max) | resolved | trap |
|---|---|---|---|---|---|---|---|
| abab_hole | ABAB-4L | ABAB (OK) | 1.00 | 0.987 | 0.0% / 0.3% | 30/40 | n/a |
| abab_electron_trap | ABAB-4L | ABAB (OK) | 1.00 | 1.000 | 0.0% / 90.1% | 37/40 | PASS |
| abca_clean | ABCA-4L | ABCA (OK) | 1.00 | 1.000 | 0.3% / 91.4% | 30/40 | n/a |
| abab_breakdown | ABAB-4L | ABAB (OK) | 1.00 | 1.011 | 0.0% / 0.2% | 30/40 | PASS |
| abca_scale | ABCA-4L | ABCA (OK) | 1.12 | 1.120 | 0.4% / 90.0% | 31/40 | PASS |
| mislabeled_N | ABA-3L | ABA_trilayer (OK) | 1.00 | 1.000 | 0.0% / 94.6% | 40/40 | PASS |

## Trap details

### abab_electron_trap
- low_n_ambiguity_flagged: True
- low_n_called_abca: False
- n_low_cols: 10
- n_ambiguous: 3
- pass: True

### abab_breakdown
- n_tested: 23
- n_breakdown_identified: 17
- sample: [(-3.07, {'lowB': 1.18, 'hiB': 1.79}), (-3.2, {'lowB': 1.11, 'hiB': 1.84}), (-3.33, {'lowB': 0.47, 'hiB': 1.82}), (-3.47, {'lowB': 0.98, 'hiB': 1.91})]
- not_called_abca: True
- pass: True

### abca_scale
- s_true: 1.12
- s_fit: 1.12000723274141
- s_recovered: True
- pass: True

### mislabeled_N
- n_good_cols: 31
- n_ABA_trilayer: 31
- n_called_4L: 0
- adjacent_N_fired: True
- pass: True

## Per-column labels (consensus over |n|>=2)

- **abab_hole**: ABAB×30, inconclusive×10
- **abab_electron_trap**: ABAB×37, ambiguous_lown×3
- **abca_clean**: ABAB×2, ABA_trilayer×1, ABCA×27, inconclusive×8, uninformative×2
- **abab_breakdown**: ABAB×30, inconclusive×10
- **abca_scale**: ABAB×2, ABA_trilayer×3, ABCA×26, inconclusive×7, uninformative×2
- **mislabeled_N**: ABA_trilayer×40

## Method notes / findings

- **Verdicts and scale are recovered on all six cases.** The fan-level consensus stacking is correct everywhere, the pinned scale s_fit matches truth to <2% (1.120 exact for the 1.12 lever-arm case), and claimed-tone frequency error is <0.5% median.
- **Adjacent-N false positive on noise-limited ABCA hole columns (genuine method gap).** On the ABCA hole side the flat-band-edge cyclotron mass is large (~1 m_e near the CNP), so at low-to-mid |n| the singleton is heavily Dingle-damped, broad and noisy. A degraded singleton sitting just below F_L plus a spurious low-f noise peak reproduces the ABA-trilayer template (small partner + big tone near F_L). A partner-significance gate (a second FS may only be claimed from a tone clearing the column noise floor) suppresses most, but a few columns per fan still misfit — the max freq error (~90%) is those columns' spurious low-f partner. Consensus and scale are unaffected; the per-column two-FS-vs-singleton call is the fragile part. A cross-column n-tracking requirement on the partner would close it.
- **Breakdown is a narrow-window phenomenon at B<=3 T.** A magnetic-breakdown sum-tone lives only at the high-B (low-1/B) edge, which is both a short effective record and where the Hann window tapers to zero. With B0 in the nominal 4-8 T range it is sub-threshold in this window; it becomes an observable, B-growing confound only for B0 ~ 3 T (just above the fundamentals' Dingle rate ~1.8), where the B-window split correctly flags it (hi-B/lo-B power ratio grows). The case uses B0=3.0 so the trap is actually exercised; higher-B0 breakdown would need a wider field window to test.
- **Generator regime.** T=1.4 K, T_D=1.5 K, ~20% SdH modulation, 0.4% noise — the quantum-mobility regime the recipe scopes to. The ABAB heavy (larger-mass) tone still lands at only ~4% of the light tone's power (Dingle), so its detection keys off the noise floor, not a fraction of the max.
- **Harmonic screen is Luttinger-aware, not ratio-only.** A true 3rd harmonic of a 0.25*F_L tone lands at 0.75*F_L and also closes the Luttinger sum, so per-column ratio screening eats the real ABAB heavy tone wherever its ratio to the light tone passes 3.0 (recipe's 2.6~3 warning). Protecting the Luttinger partner fixes the electron-side scale pin.
