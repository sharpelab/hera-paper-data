# Run report — zf1-r2 (2026-06-21)

*Generated 2026-07-18T00:36:47+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E0 |
| archive | `measurement-env/hera/docs/notes/2026-06-21-zf1-session` |
| transcript | full (1 file(s)) |
| variability set | False |

## Time

| metric | value |
|---|---|
| transcript span | 2026-06-21T21:07:33+00:00 → 2026-06-22T03:27:01+00:00 = **6.32 h** |
| session_h | **6.32 h** (closeout counts) |
| t_final_decision | 2026-06-22T03:23:35.347372+00:00 (heuristic:measure-nb) |
| decision_h | **6.27 h** |
| sweep span | 6.08 h |
| measuring | **3.42 h** (24 sweeps) |
| longest sweep | 1.52 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| gatemap | 3 | 2.15 |
| nD-map | 6 | 0.43 |
| fraunhofer | 2 | 0.41 |
| temperature-dependence | 8 | 0.15 |
| contact-survey-2t | 2 | 0.13 |
| field-sweep-1d | 2 | 0.10 |
| bias-spectroscopy | 1 | 0.05 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 56.3% | 3.42 |
| HERA court (thinking) | 33.7% | 2.05 |
| human court | 10.0% | 0.61 |

raw = **56.3%** · HIL-adjusted = **62.5%** · 27 cell lands · per-gap table in the run JSON

## Messages & tokens

| class | n |
|---|---|
| human messages | **1** |
| loop ticks | 0 |
| task notifications | 17 |
| admin | 1 |
| interrupts | 0 |

219 API requests (474 assistant entries) · 214 tool calls

Bash 51 · Bash[nb-collab] 41 · Read 34 · Write 28 · Bash[hera-watch] 20 · Bash[hera-notify] 15 · Edit 12 · Bash[nb] 9 · AskUserQuestion 2 · ToolSearch 1 · TaskStop 1

| model | in | out | cache read | cache write (5m/1h) |
|---|---|---|---|---|
| claude-opus-4-8 | 10,054 | 333,575 | 59,814,846 | 0 / 639,423 |

**cost ≈ $44.69** (API list-price equivalent; sessions ran on subscription)

## Notebook & scratch

measure nb: 63 cells — 27 HERA-landed (13 executed, 0 never-executed), 3 slot, 33 human
ana nb: 47 cells, 14 figures
hera_scratch: 100 files, 1364 LOC, 16 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E0 |
| human messages | 1 |
| interrupts | 0 |
| longest unattended (sweeps running) | **3.30 h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-21T23:36:31.687670+00:00` [ana-nb] '**Read:** Both linecuts show the **same structure and no superconducting\nsignature**: a resistive plateau (>50 Ω, clipped) from the CNP/gap out to\nn≈−3.5×10¹¹,'
- `2026-06-21T23:56:57.458926+00:00` [ana-nb] '# ★ SESSION CALL — does zf1 (bottom device) superconduct?\n\n*Per `investigations/sc-characterization.md` Step 6, five-part output contract.\nBase T 33 mK, B ≈ 0 ('
- `2026-06-22T00:08:05.415879+00:00` [ana-nb] '**Read:** At 0.2 nA the hole-side Rxx(n) is **identical to the 1 nA trace** —\ncandidate-band median 31 Ω, global min ~15 Ω, no dip toward zero. No fragile-SC\nsu'
- `2026-06-22T03:22:21.685543+00:00` [ana-nb] '# ★★ SESSION CALL (FINAL) — zf1 (bottom device) IS a superconductor\n\n*Supersedes the retracted "not-SC" call above. Per `investigations/sc-characterization.md`'
- `2026-06-22T03:23:35.347372+00:00` [measure-nb] '## HERA — session close / park (optional)\n\n**Result: zf1 (bottom device) is a superconductor** at n≈−5.0×10¹¹, D≈−0.67 V/nm — full call in the ana notebook. Thi'

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
