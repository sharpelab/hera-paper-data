# Run report — zf1-ref (2026-06-25)

*Generated 2026-10-28T01:38:23+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E0 |
| archive | `measurement-env/hera/docs/notes/2026-06-25-zf1-reference-session` |
| transcript | export-only (0 file(s)) |
| variability set | False |
| caveats | transcript-lost, export-only, tokens-null, harness-record-recovered, not-scored |

## Time

| metric | value |
|---|---|
| transcript span | no session transcript; session start 2026-06-25T19:29:00+00:00 from the manifest override |
| session_h | **87.71 h** (closeout counts) |
| t_final_decision | — (none found) |
| decision_h | **— h** |
| sweep span | 87.48 h |
| measuring | **70.33 h** (14 sweeps) |
| longest sweep | 11.86 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| temperature-dependence | 7 | 47.38 |
| bias-spectroscopy | 2 | 8.98 |
| nD-map | 1 | 8.57 |
| fraunhofer | 1 | 5.26 |
| field-sweep-1d | 2 | 0.13 |
| re-entry-baseline | 1 | 0.01 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 80.4% | 70.33 |
| HERA court (thinking) | 9.2% | 8.06 |
| human court | 10.4% | 9.09 |

raw = **80.4%** · HIL-adjusted = **89.7%** · 41 cell lands · per-gap table in the run JSON

## Messages & tokens

| class | n |
|---|---|
| human messages | **0** |
| loop ticks | 0 |
| task notifications | 0 |
| admin | 0 |
| interrupts | 0 |

0 API requests (0 assistant entries) · 0 tool calls



*(no token data — transcript missing/export-only)*

Harness record (`claude-project-entry.json`, session `6cdb1c49-165b-4f0e-8985-c65d9b5e9397`, Claude Code 2.1.191): window open 99.30 h · harness cost $316.02 · claude-opus-4-8[1m]: in 30,195 / out 620,263 / cache read 207,602,146 / cache write 19,656,664

The harness total covers every API call of the session window as the harness priced it, so it is not the per-response list-price figure above and is not entered in runs.csv.

## Notebook & scratch

measure nb: 85 cells — 41 HERA-landed (15 executed, 5 never-executed), 3 slot, 41 human
ana nb: 42 cells, 12 figures
hera_scratch: 95 files, 1956 LOC, 10 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E0 |
| human messages | 0 |
| interrupts | 0 |
| longest unattended (sweeps running) | **— h** |
| n_interventions | ⟦pending label review⟧ |

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
