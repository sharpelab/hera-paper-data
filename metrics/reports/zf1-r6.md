# Run report — zf1-r6 (2026-06-25)

*Generated 2026-07-18T00:36:47+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E1 |
| archive | `measurement-env/hera/docs/notes/2026-06-25-zf1-session` |
| transcript | full (1 file(s)) |
| variability set | False |
| caveats | notebook-named-20260624 |

## Time

| metric | value |
|---|---|
| transcript span | 2026-06-25T05:39:03+00:00 → 2026-06-25T18:13:03+00:00 = **12.57 h** |
| session_h | **12.57 h** (closeout counts) |
| t_final_decision | 2026-06-25T13:33:45.940352+00:00 (heuristic:ana-nb) |
| decision_h | **7.91 h** |
| sweep span | 7.77 h |
| measuring | **5.40 h** (21 sweeps) |
| longest sweep | 3.91 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| gatemap | 1 | 3.91 |
| gate-current-sanity-check | 4 | 0.58 |
| nD-map | 1 | 0.27 |
| cnp-and-dline-calibration | 3 | 0.18 |
| temperature-dependence | 8 | 0.16 |
| field-sweep-1d | 3 | 0.16 |
| bias-spectroscopy | 1 | 0.14 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 69.6% | 5.40 |
| HERA court (thinking) | 26.6% | 2.06 |
| human court | 3.9% | 0.30 |

raw = **69.6%** · HIL-adjusted = **72.4%** · 20 cell lands · per-gap table in the run JSON

## Messages & tokens

| class | n |
|---|---|
| human messages | **3** |
| loop ticks | 0 |
| task notifications | 21 |
| admin | 2 |
| interrupts | 0 |

164 API requests (388 assistant entries) · 152 tool calls

Bash 51 · Read 36 · Bash[nb-collab] 32 · Bash[hera-watch] 12 · Write 11 · Edit 4 · Bash[nb] 3 · Bash[hera-notify] 3

| model | in | out | cache read | cache write (5m/1h) |
|---|---|---|---|---|
| claude-opus-4-8 | 15,857 | 264,653 | 39,210,418 | 0 / 372,627 |

**cost ≈ $30.03** (API list-price equivalent; sessions ran on subscription)

## Notebook & scratch

measure nb: 43 cells — 20 HERA-landed (10 executed, 0 never-executed), 3 slot, 20 human
ana nb: 32 cells, 7 figures
hera_scratch: 19 files, 519 LOC, 7 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E1 |
| human messages | 3 |
| interrupts | 0 |
| longest unattended (sweeps running) | **11.78 h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-25T13:33:45.940352+00:00` [ana-nb] '# VERDICT — zf1 (Bernal BLG + WSe₂, bottom device): SUPERCONDUCTOR (decisive)\n\n*Per the `sc-characterization` output contract. Campaign question: does this devi'

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
