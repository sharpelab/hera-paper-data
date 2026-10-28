# Run report — zf1-r4 (2026-06-23)

*Generated 2026-10-27T02:34:55+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E0 |
| archive | `measurement-env/hera/docs/notes/2026-06-23-zf1-session-full` |
| transcript | partial (0 file(s); 2 other-agent file(s) ignored) |
| variability set | False |
| caveats | transcript-lost, setup-agent-transcripts-only, tokens-null, harness-record-recovered |

## Time

| metric | value |
|---|---|
| transcript span | no session transcript; session start 2026-06-23T22:17:53+00:00 from the manifest override |
| session_h | **9.11 h** (closeout counts) |
| t_final_decision | 2026-06-24T03:53:13.290095+00:00 (heuristic:ana-nb) |
| decision_h | **5.59 h** |
| sweep span | 7.47 h |
| measuring | **3.67 h** (41 sweeps) |
| longest sweep | 1.07 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| heater-settle-calibration | 7 | 1.36 |
| gatemap | 1 | 1.07 |
| fraunhofer | 2 | 0.37 |
| field-sweep-1d | 1 | 0.25 |
| temperature-dependence | 21 | 0.18 |
| nD-map | 1 | 0.15 |
| gate-current-sanity-check | 4 | 0.12 |
| bias-spectroscopy | 1 | 0.10 |
| cnp-and-dline-calibration | 3 | 0.08 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 49.2% | 3.67 |
| HERA court (thinking) | 36.4% | 2.72 |
| human court | 14.4% | 1.08 |

raw = **49.2%** · HIL-adjusted = **57.5%** · 43 cell lands · per-gap table in the run JSON

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

Harness record (`claude-project-entry.json`, session `6327fc0f-1a59-4102-8a62-fa1677f8b34a`, Claude Code 2.1.187): window open 20.02 h · harness cost $76.75 · claude-opus-4-8[1m]: in 22,466 / out 456,851 / cache read 90,541,209 / cache write 1,994,463

The harness total covers every API call of the session window as the harness priced it, so it is not the per-response list-price figure above and is not entered in runs.csv.

## Notebook & scratch

measure nb: 83 cells — 43 HERA-landed (19 executed, 3 never-executed), 3 slot, 37 human
ana nb: 34 cells, 8 figures
hera_scratch: 102 files, 561 LOC, 12 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E0 |
| human messages | 0 |
| interrupts | 0 |
| longest unattended (sweeps running) | **— h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-24T03:53:13.290095+00:00` [ana-nb] '# ★ THE CALL — zf1 (bottom device): SUPERCONDUCTOR (strong)\n\nGate-tuned proximity superconductivity in Bernal bilayer graphene / WSe₂, located and characterised'

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
