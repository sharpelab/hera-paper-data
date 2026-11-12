# Run report — zf1-r3 (2026-06-22)

*Generated 2026-07-18T00:36:47+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E0 |
| archive | `measurement-env/hera/docs/notes/2026-06-22-zf1-session` |
| transcript | full (1 file(s)) |
| variability set | False |

## Time

| metric | value |
|---|---|
| transcript span | 2026-06-22T23:43:46+00:00 → 2026-06-23T06:16:45+00:00 = **6.55 h** |
| session_h | **6.55 h** (closeout counts) |
| t_final_decision | 2026-06-23T06:12:06.140204+00:00 (heuristic:ana-nb) |
| decision_h | **6.47 h** |
| sweep span | 6.34 h |
| measuring | **3.96 h** (8 sweeps) |
| longest sweep | 2.24 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| gatemap | 2 | 2.30 |
| temperature-dependence | 1 | 1.15 |
| cnp-and-dline-calibration | 2 | 0.24 |
| bias-spectroscopy | 1 | 0.14 |
| field-sweep-1d | 1 | 0.09 |
| gate-current-sanity-check | 1 | 0.03 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 62.3% | 3.96 |
| HERA court (thinking) | 28.4% | 1.80 |
| human court | 9.3% | 0.59 |

raw = **62.3%** · HIL-adjusted = **68.7%** · 17 cell lands · per-gap table in the run JSON

## Messages & tokens

| class | n |
|---|---|
| human messages | **0** |
| loop ticks | 0 |
| task notifications | 10 |
| admin | 1 |
| interrupts | 0 |

191 API requests (418 assistant entries) · 194 tool calls

Write 55 · Bash 48 · Bash[nb-collab] 27 · Read 24 · Bash[hera-watch] 11 · Edit 10 · Bash[nb] 9 · Bash[hera-notify] 9 · AskUserQuestion 1

| model | in | out | cache read | cache write (5m/1h) |
|---|---|---|---|---|
| claude-opus-4-8 | 7,985 | 272,916 | 44,207,112 | 0 / 901,063 |

**cost ≈ $37.98** (API list-price equivalent; sessions ran on subscription)

## Notebook & scratch

measure nb: 48 cells — 17 HERA-landed (8 executed, 0 never-executed), 3 slot, 28 human
ana nb: 34 cells, 9 figures
hera_scratch: 63 files, 1031 LOC, 8 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E0 |
| human messages | 0 |
| interrupts | 0 |
| longest unattended (sweeps running) | **6.55 h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-23T06:10:17.179742+00:00` [ana-nb] '**Read:** **The supercurrent melts at a finite Tc** — the fifth hallmark. Ic(T) saturates at ~24 nA at base (39 mK), falls monotonically, and reaches 0 at **Tc'
- `2026-06-23T06:12:06.140204+00:00` [ana-nb] '# ★ Per-candidate SC verdict — zf1 (bottom device), 2026-06-22\n\n**Candidate R1 — `superconductor (DECISIVE)`** at **n ≈ −4.65×10¹¹ cm⁻², D ≈ −0.65 V/nm** (V_tg='

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
