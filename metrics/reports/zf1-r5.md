# Run report — zf1-r5 (2026-06-24)

*Generated 2026-10-27T02:34:55+00:00 by hera-metrics (measurement-env).*

## Identity

| field | value |
|---|---|
| device / rig | zf1 / toploader |
| mode | E1 |
| archive | `measurement-env/hera/docs/notes/2026-06-24-zf1-session` |
| transcript | export-only (0 file(s); 1 other-agent file(s) ignored) |
| variability set | False |
| caveats | transcript-export-only, setup-agent-transcripts-only, tokens-null, harness-record-recovered |

## Time

| metric | value |
|---|---|
| transcript span | no session transcript; session start 2026-06-24T22:50:40+00:00 from the manifest override |
| session_h | **4.56 h** (closeout counts) |
| t_final_decision | 2026-06-25T03:20:01.572549+00:00 (heuristic:measure-nb) |
| decision_h | **4.49 h** |
| sweep span | 4.43 h |
| measuring | **2.44 h** (13 sweeps) |
| longest sweep | 1.51 h |

Sweeps by recipe:

| recipe | n | hours |
|---|---|---|
| gatemap | 1 | 1.51 |
| gate-current-sanity-check | 4 | 0.58 |
| bias-spectroscopy | 2 | 0.12 |
| cnp-and-dline-calibration | 4 | 0.12 |
| field-sweep-1d | 2 | 0.11 |

## Utilization

| component | fraction | hours |
|---|---|---|
| measuring (active ops) | 55.0% | 2.44 |
| HERA court (thinking) | 37.7% | 1.67 |
| human court | 7.3% | 0.32 |

raw = **55.0%** · HIL-adjusted = **59.3%** · 27 cell lands · per-gap table in the run JSON

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

Harness record (`claude-project-entry.json`, session `9ceaffa3-25ed-42b6-a395-3ef979018bb2`, Claude Code 2.1.191): window open 6.47 h · harness cost $30.74 · claude-opus-4-8[1m]: in 11,857 / out 252,293 / cache read 40,115,287 / cache write 431,528

The harness total covers every API call of the session window as the harness priced it, so it is not the per-response list-price figure above and is not entered in runs.csv.

## Notebook & scratch

measure nb: 49 cells — 27 HERA-landed (13 executed, 0 never-executed), 3 slot, 19 human
ana nb: 23 cells, 4 figures
hera_scratch: 27 files, 619 LOC, 6 figures, 0 notebooks

## Autonomy

| metric | value |
|---|---|
| mode | E1 |
| human messages | 0 |
| interrupts | 0 |
| longest unattended (sweeps running) | **— h** |
| n_interventions | ⟦pending label review⟧ |

## Decision candidates (heuristic)

- `2026-06-25T01:55:22.922785+00:00` [ana-nb] '**Read:** A sharp, localized 4T Rxx dip to **~6 Ω at n=−0.55×10¹² cm⁻², D=−0.6 V/nm** — absent at D=−0.5/−0.7, and the opposite D sign (+0.5) shows a **peak** a'
- `2026-06-25T02:03:44.485379+00:00` [ana-nb] '**Read:** A critical-current signature — dV/dI dips to ~7.5 Ω at zero bias and rises through **sharp switching peaks at ±Ic ≈ 15 nA** to the ~45 Ω normal state;'
- `2026-06-25T03:19:29.558016+00:00` [ana-nb] '# SESSION VERDICT — zf1 bottom device (2026-06-24)\n\n**Campaign question: does this device superconduct?**\n\n## Candidate C1 — n = −0.55×10¹² cm⁻² (−5.5×10¹¹), D'
- `2026-06-25T03:20:01.572549+00:00` [measure-nb] '## HERA — session pause: device parked, verdict delivered\n\nBase-T + field characterization complete. Candidate C1 (n=−0.55×10¹², D=−0.60 V/nm) = **consistent-wi'

## Expert evaluation — reserved

quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧
