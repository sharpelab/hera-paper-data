# vti02-fan-design — high-effort smokes (2026-09-23)

One n = 1 episode per arm on the 08-22 cut (`4c612d1` state), all at
`effort: high` — the live sessions' setting: every archived vti-02 transcript
(08-21…08-25, Claude Code 2.1.239–2.1.243) records `"effort":"high"` and
nothing else. Harness `434648c` (job layer + the arms at high + Codex
`model_reasoning_summary="detailed"`); astra-corpus ran first from a `0bebaa2`
worktree with `--effort high` and the same summary flag. Grader `fan-design`
(extractor `claude-opus-5`), grade job `20260923T015753-5eu7t8`. Models are
the live ids: `claude-fable-5` / `claude-opus-5` pinned, observed in
`episode.json` and on every assistant message.

| Arm | Landed (grader tier) | Design | Resolved fraction · min rows/period | Episode $ |
|---|---|---|---|---|
| fable + corpus | none — watch armed before the append | fan written to `hera_scratch/`: electron, n 3.2→1.0e12 × 81, B 1.2→10 T × 123 rows 1/B | — | 8.05 |
| fable, none | probe (LK ladder leg 1/5, 10 K, 6→1.5 T) | reads ABAB moderate, masses as the decider | — | 9.25 |
| opus + corpus | fan | electron, n 1.4→3.2e12 × 73, B 0.8→8 T × 113 rows 1/B, ~5 h | 1.000 · 3.27 | 4.53 |
| opus, none | fan | n −1.25→+3.24e12 × 66, B 1→10 T × 81 rows 1/B, 3.3 h | 0.972 · 2.88 | 2.98 |
| sol + corpus | fan | electron, n 2.7→3.2e12 × 13, B 1→10 T × 103 rows 1/B, 2.5 h | 1.000 · 3.72 | 2.73 |
| sol, none | fan | n −1.2→+3.2e12 × 89, B 0.5→10 T × 39 rows uniform-B, 2.75 h | 0.659 · 0.59 | 1.82 |
| astra + corpus | probe (electron low-field extension) | n +3.2e12, B 0.3→4 T × 387 pts 1/B, 55 min | — | 2.43 |
| astra, none | none — `hera-watch --help` ended the episode | zero-field liveness line staged in `hera_scratch/cell_handoff_line.py` | — | 1.83 |

Run dirs: `$HERA_DATA/replay/runs/vti02-fan-design-<arm>/20260923T0137*` (job
`20260923T013749-p0npro`); astra-corpus `…/vti02-fan-design-astra-corpus/20260923T012957`.
sol-corpus at medium on the same state (`20260923T005529`) also landed a fan
(n 3.2→2.4e12 × 25, B 0.8→10 T × 116 rows 1/B).

## The censored-onset clause

`landau-fan.md` step 1, cost-floor lever (1): "If the carrying tone is
`censored` … a cheap low-field extension pins it before committing a long
fan." On this state the electron ~7.1 T tone is censored at run 6's 0.3 T
edge, where the grid is 50 mT (local Nyquist ≈ 1 T at 0.3 T), and — astra at
high, restricting `sdh_onset` to the 1–10 T fine grid — still censored at
1 T; the 22 T / 29.5 T tones read 1.40 / 1.76 T. The corpus arms split on it:

- **astra** applies it: "The 0.3 T result must not set an expensive fan.
  Next: a finer, changed-grid low-field electron check … as required by
  sdh-spot-check Verify / landau-fan cost-floor check." At medium, 4/4 on this
  cut, same move.
- **fable** reads "carrying tone" as the claim's: the light tone is censored
  but not the claim-carrier; B_lo = 1.2 T under the heavy tone's 1.4–1.9 T
  onset.
- **opus** names the censoring and the sub-1 T aliasing, sets B_lo = 0.8 T.
- **sol** sets B_lo = 1 T, silent on onset.

The clause is ambiguous (strongest tone vs claim-carrying tone), and under
astra's reading the corpus-arm target at this cut is the extension, not the
fan. Ruling open (Aaron): Obsidian *HERA TODO* § Post-campaign.

## astra

Reasoning tokens per episode, from the rollout: astra 183–1013 at medium, 616
at high; sol 3.6–4.7k at medium. The summaries are headings only ("Restricting
sampled onsets", "Preparing low-field extension"). astra-none at medium landed
a 60 s B = 0 `s.watch`, triggered by its own `plan.md` step 4 conditional on
run 6's signed R (to −33 Ω); at high it staged the same class of cell.

## Harness

- `hera-watch --help` arms the stub (`src/hera/replay/stubs/hera-watch`,
  `add_help=False`): no run dir, no `--next`, falls through to the marker
  write. Passed to the coordinator; `--help` should be a read.
- fable-corpus armed `hera-watch data --next --follow` before `nb-collab
  append` — the watch-first exclusion; its fan is in `hera_scratch/cell_fan.py`.
  The stub now waits for an appended code cell; the Fable + corpus rerun on
  it (`vti02-fan-design-fable-corpus/20260923T031220-4eoepm`) is in
  `replay-fresh-start-plan.md` § Results.
- sol-corpus's separate `execute-cell` was refused by the hook; it re-appended
  with `--execute` (two identical fan cells, the second executed).
- A fresh `git worktree` breaks derive's mtime fallback (checkout mtimes);
  `touch -r` from the main tree's archive restores it.
