# Dev-set designs through vti02_sim (agent, 2026-09-23)

## Headline

The component score tracks simulated detection well enough to freeze: capped tone cells,
k = 3, the 0.75 T clip and Halder tones. Before freezing, **drop the SNR multiplier from the
primary score.** It overstates what extra current or τ buys by about 4×.

## Setup

- **Designs:** 23 fans.
  - 19 dev-set fans at the 08-22 cut: 15 graded plus 4 hand-extracted by prereg, labelled by
    observed model.
  - 4 live fans: 08-21 r8, 08-22 r8, 08-24 r4, 08-25 r8.
- **Excluded:** ramps (none at this cut; 08-23 r6 is out), 08-25 r5, astra's B = 0 row, and
  hole columns (the sim covers the electron side only). The grader credits only 3 hole
  columns, and an electron-only grader gives the same ranks.
- **Sim settings:**
  - Tones: Halder_ABAB with its masses (primary), observed tones, corpus tones.
  - Excess noise: 55 / 87 / 165 nV/√Hz, plus noise-free.
  - 5 seeds.
  - Acquisition: the design's own settings; the reference (50 nA, τ 0.3, 100 µV, delay 7τ);
    own settings without clipping or quantization; own settings at 50 nA.
  - Runtime: 19 s for the whole matrix, using cached noise-free maps.
- **Detection:** the live-check col_fft / q1_eval code, counting columns with light_true AND
  split. Two windows: the design's own and the 0.75 T clip.
- **Sanity check, live vs sim** (observed tones, 55 nV), as light_true / split:

  | fan | live | sim |
  |---|---|---|
  | 08-25 | 56 / 54 | 48 / 54 |
  | 08-22 | 50 / 60 | 47 / 57 |
  | 08-21 | 17 / 3 | 15 / 2 |
  | 08-24 | 9 / 4 | 7 / 2 |

## Correlations (Spearman / Kendall, n = 23, own acquisition)

"a" is detected columns; "b" is capped cells; "c" is b per hour.

| window, noise | a vs band | b vs cells | c vs cells/h |
|---|---|---|---|
| clip, 55 nV | 0.91 / 0.79 | 0.86 / 0.75 | 0.92 / 0.78 |
| **clip, 87 nV** | **0.94 / 0.80** | **0.86 / 0.73** | **0.85 / 0.69** |
| clip, 165 nV | 0.84 / 0.66 | 0.71 / 0.55 | 0.56 / 0.43 |
| own window, 87 nV | 0.75 / 0.62 | 0.65 / 0.56 | 0.80 / 0.64 |
| clip, noise-free | 0.87 / 0.74 | 0.87 / 0.77 | 0.91 / 0.78 |

- Bootstrap 90 % CI on Kendall for c (clip, 87 nV): [0.52, 0.83].
- Seed-to-seed agreement of the sim (Kendall): 0.90.
- Swapping the tone model inside the sim barely matters (0.86–0.92). Geometry drives the ranks.
- Noise level matters most. At 165 nV the 10 nA designs collapse while 08-25 at 50 nA survives.

## Disagreements (clip window, 87 nV)

| episode | grader → sim | cause |
|---|---|---|
| opus-none ou2xbh | rank 3 → 13 (cells 0.80, sim 0.52) | Acquisition: 10 nA, only 81 rows, delay/τ 3.3. At the reference acquisition the sim gives b 0.92. |
| live 08-21 r8 | 22 → 14 (0 vs 0.20) | k: every column has p < 3, yet 6.8 columns are detected, in one cell. Ties plus 1.38 h exaggerate the rank move. |
| sonnet 200401 | 9 → 4 (clip); 9 → 18 (own window) | τ 0.1: 13 columns detected vs 58 at the reference. The own window also includes empty field from 0.5–0.75 T. |
| haiku r3w0gf | b rank 2 → 21.5 in the own window | Analysis window only: from 0.3 T the Hann FFT centres on empty low field. So clip the analysis window. |
| sonnet 192335 / #1 | b 0.60 → 1.00, 0.40 → 0.79 | High line m = 3: 37–42 columns sit at 2.5 rows per period, and the sim detects them 34–71 % of the time. |
| live 08-25 r8 | 10 → 6 | k plus 50 nA: 9 columns with p < 3 are detected, making a 5th cell. |
| sonnet 232408 | b 1.0 → 0.80 | Acquisition: 9 columns lost to noise. |

**Per-column breakdown** (987 columns, clip window, 87 nV):

| outcome | columns |
|---|---|
| grader and sim agree, detected | 430 |
| grader and sim agree, not detected | 557 |
| in band, lost to noise | 65 |
| in band, missed even without noise | 52 (all light tone, n 1.6–2.0, p 3.1–3.7) |
| detected with F_L above the high line | 39 |
| detected with p < k | 37 |

**Detection (light AND split) vs the grader's p**, columns under the high line:

| p | 1.5–2 | 2–2.5 | 2.5–3 | 3–4 | 4–6 | > 6 |
|---|---|---|---|---|---|---|
| noise-free | 0.18 | 0.22 | 0.26 | 0.61 | 1.00 | 1.00 |
| 87 nV | 0.20 | 0.17 | 0.23 | 0.54 | 0.88 | 0.77 |

The 50 % point is p ≈ 3.3, so **k = 3 is about right for the joint outcome**. Live-check's
k50 of 1.7–2.2 is per tone, not joint.

**Ruled out:**
- Clipping: no design clips.
- Cell width 2δF: Kendall drops 0.69 → 0.58.
- Quantization: only haiku 3xn8hn #01 is affected (50 mV sens: the sim detects nothing
  against 27 columns without quantization). The grader already scores it 0, because its linear-B
  worst step kills it.

## Does acquisition matter?

- Per-column light-peak SNR, own over reference (median): **0.41**. The formula predicts
  0.20 at τ 0.3 and 0.12 at τ 0.1.
- Detected columns, own over reference: 0.86 / 0.75 / 0.35 at 55 / 87 / 165 nV.
- Capped cells, own over reference: 0.92 / 0.88 / 0.59.
- The loss acts as a threshold on columns with little margin, not as a multiplier. At
  SNR 0.20 the ratio still ranges 0.47–1.0.
- Multiplying by SNR leaves ranks flat or worse (Kendall 0.69 → 0.66) and wrecks the absolute
  fit (MAE 0.13 → 0.48). It helps only at 165 nV.

## Recommendations before freezing

1. Primary score: capped cells, k 3, cell width 1, 0.75 T clip, Halder tones.
2. Drop cells × SNR from the primary; keep it as a sensitivity. None of the saturating forms
   tried (√SNR, per-column ratio) beats having no acquisition term below 165 nV.
3. Quantization multiplier: 0, not 0.5, when the oscillation is about 1 LSB. No dev-set score
   changes.
4. High line m = 3 at the worst step is conservative: 2.5 rows per period is detectable 34–71 %
   of the time, and the worst step is harsh on linear-B grids. The in-sample best (k 2.5,
   m 2.5, Kendall 0.81) sits inside the CI and was fitted on these 23 designs. Change it only
   as a stated ruling. A local rows-per-period rule would fix linear-B grids.
5. Don't use the simulated outcome as the primary quality score. Its ranks depend on the noise
   level (ρ 0.92 → 0.56 on c across noise levels), on the analysis window, and on known sim
   errors. Use it as validation or a secondary, pinned at the clip window and 87 nV.
6. Pre-register the 0.75 T analysis clip for any check based on detection.

## Flags

- SNR ∝ I√τ overstates the effect by about 4×.
- m = 3 at the worst step is conservative.
- 08-25 is simulated at n_scale 1.0.
- Hole columns are unchecked.

## Files

- Plot: `scatter.png`.
- Data: `sim_episodes.csv`, `sim_columns.csv.gz`, `compare_episodes.csv`, `correlations.csv`,
  `diag_columns.csv`, `acquisition_effect.csv`, `knob_scan.csv`.
- Scripts: `designs.py`, `simcore.py`, `run.py`, `compare.py`, `diag.py`, `q5.py`, `knobs.py`,
  `swaps.py`, `plot.py`, `inv.py`.
- Noise-free map cache: `work/`.
