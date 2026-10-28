# Run report — zf1-r1 (2026-06-20)

*Generated 2026-07-18T00:36:47+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E0 |
| archive | `measurement-env/hera/docs/notes/2026-06-20-zf1-session` |
| transcript | full (1 file(s)) |
| variability set | False |

## Time

| metric | value |
|---|---|
| transcript span | 2026-06-20T20:55:19+00:00 → 2026-06-21T19:38:27+00:00 = **22.72 h** |
| session_h | **22.72 h** (closeout counts) |
| t_final_decision | 2026-06-21T14:52:10.849528+00:00 (heuristic:ana-nb) |
| decision_h | **17.95 h** |
| sweep span | 17.76 h |
| measuring | **10.90 h** (8 sweeps) |
| longest sweep | 7.73 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| nD-map | 1 | 7.73 |
| gatemap | 2 | 3.02 |
| gate-current-sanity-check | 2 | 0.09 |
| perp-density-at-Bzero | 3 | 0.06 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 61.4% | 10.90 |
| HERA court (thinking) | 10.2% | 1.82 |
| human court | 28.4% | 5.04 |

raw = **61.4%** · HIL-adjusted = **85.7%** · 31 cell lands · per-gap table in the run JSON

## Messages & tokens

| class | n |
|---|---|
| human messages | **11** |
| loop ticks | 0 |
| task notifications | 18 |
| admin | 1 |
| interrupts | 0 |

239 API requests (529 assistant entries) · 238 tool calls

Write 65 · Bash 52 · Read 37 · Bash[nb-collab] 34 · Bash[hera-watch] 19 · Edit 14 · Bash[nb] 10 · Bash[hera-notify] 7

| model | in | out | cache read | cache write (5m/1h) |
|---|---|---|---|---|
| claude-opus-4-8 | 9,455 | 454,152 | 77,811,268 | 0 / 3,442,896 |

**cost ≈ $84.74** (API list-price equivalent; sessions ran on subscription)

## Notebook & scratch

measure nb: 69 cells — 31 HERA-landed (9 executed, 6 never-executed), 3 slot, 35 human
ana nb: 28 cells, 7 figures
hera_scratch: 79 files, 1248 LOC, 12 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E0 |
| human messages | 11 |
| interrupts | 0 |
| longest unattended (sweeps running) | **11.07 h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-21T01:39:02.834257+00:00` [ana-nb] '## CORRECTION (2026-06-20) — 4T Rxx is `sr830_2`, not sr3 — Step-1 map & verdict redone\n\nOperator: the 4-terminal Rxx is **`sr830_2`** (the `sr2="5-4"` config l'
- `2026-06-21T01:39:02.834257+00:00` [ana-nb] '**Read (corrected, sr2 = 4T Rxx) — NO superconducting candidate; cleaner than the sr3 view.**\n\n- **4T Rxx is kΩ-scale everywhere:** 3.1–44 kΩ, metallic backgrou'
- `2026-06-21T05:25:47.589187+00:00` [ana-nb] '**Read — no SC candidate in the large-D quadrant, even at 2× resolution.**\n\n- 4T Rxx (sr2) spans 3.4–44 kΩ (metal + CNP ridge); **zero points below 3 kΩ** anywh'
- `2026-06-21T14:52:10.849528+00:00` [ana-nb] "## Run 8 — 8 h rasterized nD-map: the candidate's extent, and a verdict on it\n\n20,572-pt `nD-map` (sweep.raster, 240×100 ≈ 0.0025 e12 × 0.0025 V/nm) over n ∈ [−"

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
