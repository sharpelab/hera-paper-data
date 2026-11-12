# Post-hoc extraction audit — vti-02 fan-design matrix

Exploratory, dated 2026-09-30, after the registered analysis (`analysis.md` beside this file) was read. The registered result is the result of record and is unchanged; the grader, extraction prompt and `analysis.py` stay at the frozen commit `58d02e64`. This file records where the saved extractions misdescribe the landed cells, what the frozen grader makes of the corrected descriptions, and what the next campaign's grader should do differently. Numbers come from `audit.py` beside this file (`audit.json` is its output); the fan-level defects were found by a GPT-6 Astra read (`astra-notes.md`) and an Opus 5.5 read, and each was checked against the landed cell before it was accepted.

## Eleven fans whose extraction misdescribes the landed cell

**Field grids (6).** The extraction prompt requires the full `B_values` vector for a nonuniform grid. Six extractions instead recorded a stitched or recursive grid as one uniform grid over its endpoints, or dropped a B = 0 anchor row. All six are in the no-corpus arm. The corrected rows use the vector transcribed from the appended cell.

**Hook dwell (5).** Five GPT-6 Astra fans call the sweep with `fast_delay=0.0` and put a 3.0 s `interruptible_sleep` in the registered before-point hook. The extraction records the call's `fast_delay_s 0.0`, and the grader's time and acquisition models read only that field, so these fans are under-priced and carry an acquisition penalty they did not earn. The corrected rows set the effective dwell to 3.0 s.

| Fan (`vti02-fan-request-0822-…`) | Defect | Hours | P(call) | v (8 h) | Span | Rows/F_L |
|---|---|---|---|---|---|---|
| gpt6sol-none/…e9946u/00 | 0.2 T steps plus a final 0.1 T step, read as uniform B | 4.24 → 4.24 | 0.000 → 0.000 | 0.000 → 0.000 | 0.00 → 0.00 | 0.44 → 0.43 |
| gpt6sol-none/…e9946u/14 | 50 mT steps to 3 T then 0.2 T, read as uniform B | 4.45 → 4.45 | 0.052 → **0.590** | 0.052 → **0.590** | 0.22 → **1.72** | 0.38 → 0.72 |
| opus55-none/…e2rujz/06 | 64 rows in 1/B to 4 T then 0.2 T steps, read as uniform 1/B | 6.59 → 6.59 | 0.997 → 0.997 | 0.997 → 0.997 | 4.52 → 4.52 | 3.33 → 2.81 |
| opus55-none/…e2rujz/11 | three 1/B and B segments, read as uniform 1/B | 5.57 → 5.57 | 0.874 → **0.993** | 0.874 → **0.993** | 3.09 → **4.43** | 2.15 → **3.39** |
| opus-none/…7hk80x/02 | B = 0 anchor row dropped | 4.82 → 4.97 | 0.949 → 0.949 | 0.949 → 0.949 | 4.55 → 4.55 | 4.04 → 4.04 |
| opus-none/…4kxt1o/14 | 1/B recursion with a 0.4 T step cap, read as uniform 1/B | 5.50 → 5.50 | 0.997 → 0.997 | 0.997 → 0.997 | 4.48 → 4.52 | 3.32 → 3.19 |
| astra-corpus/…qy46wv/03 | 3 s dwell in a hook | 1.39 → 3.38 | 0.262 → 0.381 | 0.262 → 0.381 | 1.54 | 9.76 |
| astra-corpus/…d9dmed/15 | 3 s dwell in a hook | 0.98 → 2.02 | 0.456 → 0.658 | 0.456 → 0.658 | 1.54 | 4.61 |
| astra-corpus/…xmv9jb/04 | 3 s dwell in a hook | 0.83 → 1.46 | 0.000 | 0.000 | 0.00 | 0.00 |
| astra-none/…7x4jav/03 | 3 s dwell in a hook | 1.92 → **10.58** | 0.000 | 0.000 | 0.00 | 0.20 |
| astra-none/…7x4jav/09 | 3 s dwell in a hook | 2.08 → **10.96** | 0.750 → 0.918 | 0.750 → **0.000** | 2.96 | 0.38 |

The agents' own stated run times agree with the corrected hours (the Astra none/09 cell states 12.5 h).

## What the corrections do to the registered statistics

Same fans, same equal model weights, the frozen scorer; no permutation test rerun.

| Statistic | Registered | Six grids corrected | Grids and hook dwell corrected |
|---|---|---|---|
| 1 P(call) within 8 h, Δ | +0.427 | +0.422 | +0.431 |
| 2 Tracked span, Δ | +1.371 | +1.347 | +1.347 |
| 3 Rows per F_L period, Δ | +2.334 | +2.327 | +2.327 |
| 4 Pareto dominance, D | +0.399 | +0.396 | +0.406 |

Per model the largest moves are GPT-6 Astra on metric 1 (+0.460 → +0.514) and dominance (+0.466 → +0.526), GPT-6 Sol on metric 1 (+0.808 → +0.781), and Opus 5.5 on span (+0.325 → +0.258). Individual grades move by up to 0.54 in P(call) and 8.9 h; the pooled statistics move by at most 0.024 and in the corpus's favour on three of four.

## Smaller mismatches, not rescored

- **Autorange is extracted but not modelled.** Opus 5.5 none/…e2rujz/10 registers an `autorange_sr830s` hook from a 10 µV floor; the extraction flags it, the scorer clips at a fixed 10 µV. Fixed alternatives of 20, 50 or 100 µV move its P(call) from 0.046 to 0.050; the fan's field grid is its real limit.
- **A data-dependent sensitivity reads as "don't check clipping".** Fable 5.1 corpus/…paekuu/04 picks the fan's scale from 50/100/200/500 µV after a sizing row and aborts if that row clips. The extraction's `sensitivity_V: null` is honest, but the scorer treats null as no clipping check, and the abort branch is not represented.
- **Bundled cells are graded as fans with the preceding diagnostic outside fan time.** Fable 5.1 corpus/…paekuu/04 lands a measured ride-up, a sizing row and the fan in one cell (its `stated_wall_clock_h` of 6.83 prices the package; the fan alone is 4.7 h, and its notes' "921 ride-up points" is 421 by the cell's own expression); Opus 5.5 corpus/…msonbj/05 lands a 22-minute low-field probe and the fan in two cells. A standalone diagnostic is censored, so "deferral" partly depends on where the agent puts the handoff.
- **Acquisition flags do not reach the analysis table.** `box.acquisition` marks 12 of 120 no-corpus fans (six of them GPT-6 Sol) as quantized at their chosen scale, and 0 of 119 corpus fans; the `flags` column in `analysis.md` carries only the extraction-level flags, so an empty entry is not a clean acquisition bill of health.
- **Three fans read from scratch files.** fable-none/…ktxxq0/11, opus-corpus/…4ky568/08 and opus-none/…4kxt1o/09 appended nothing (`--follow` without `--wait`); the grader extracted the fan from `episode-stop.json` and `hera_scratch/cell_fan.py`, and the analysis counts them with the flag "extraction reads a fan; the harness saw no sweep cell appended". Ruled by Zack on 2026-09-30: an extractable fan is a fan. Scoring the three at 0 instead gives Δ = +0.424 on metric 1.

## For the next campaign's grader

Recorded here, not applied: the surfaces are frozen for this matrix.

1. The time and acquisition models read an effective settling that includes hooks; the extraction gets an `effective_dwell_s` field with the hook named as its source.
2. An extraction validator reconstructs the field vector from the landed code and refuses a `spacing`/`n_B` that disagrees with it, or the prompt requires `B_values` for anything that is not a single `linspace`/`field_invB` call.
3. Autorange and data-dependent sensitivity are modelled or flagged as untraced-with-abort rather than read as "no clipping check".
4. A landed cell is charged for every measurement it contains, and a diagnostic that precedes the fan in the same cell is priced with it.
5. The analysis table carries the acquisition flags beside the extraction flags.
