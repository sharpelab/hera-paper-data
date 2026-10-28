# Tranche 1 — vti-02 fan-design matrix

You are running tranche 1 of a pre-registered experiment. Zack approved this batch on
2026-09-29: twelve cells × 5 counted episodes on the frontier `vti02-fan-request-0822`, then
grading and the registered analysis. Anything beyond that batch needs his go.

## Read first

- `hera/campaigns/vti02-fan-design/prereg.md` — the design; it is frozen at commit `58d02e64`
  (pushed to origin/hera).
- `hera/campaigns/vti02-fan-design/analysis.py` — the registered analysis (docstring has the usage).
- `hera/docs/replay-parallel-runs.md` — the jobs layer (`hera-replay submit / wait / status`).
- Memory `project-vti02-fan-prereg-state`.

## Frozen: do not change

- No edit to the grader, extraction prompt, case files, briefs, mask, images or `analysis.py`.
- No `git pull`, `checkout`, `stash` or rebase in this checkout while the tranche runs, and do
  not touch `hera/docs/notes/2026-08-22-vti-02-session`: the state is built from that
  archive's file mtimes.
- No commit and no push without Zack's word.
- A problem with a frozen surface is a deviation: write it up for Zack, do not fix it.

## Billing

Claude episodes and all grading bill the AI for Science award:
`ANTHROPIC_API_KEY=$(hera-key offline)` on every `hera-replay submit`, with
`CLAUDE_CODE_OAUTH_TOKEN` unset. Verified today on a Haiku episode and an extraction
(`run.json` `credential: ANTHROPIC_API_KEY`; transcript `apiKeySource`). Codex episodes use the
harness's ChatGPT login and need nothing set. Never print the key.

## Before launch

1. `git status` clean apart from the two untracked paths of another workstream
   (`hera/campaigns/stacking/read-keys/`, `hera/docs/benchmark-rubrics.md`); HEAD `58d02e64`.
2. `uv run hera-replay status`: pools idle, no orphans.
3. `$HERA_DATA/replay/runs/` holds no `vti02-fan-request-0822-*` dir (the smokes are in
   `runs-smoke/`).
4. Cut digest: `uv run hera-replay cut --case hera/replay/cases/vti02-fan-request-0822-opus-corpus.yaml --dest <scratch>`
   and the same for `-opus-none`; both digests start `f7f808fe749b9bf8`. A different digest
   stops the launch.

## Launch

    ANTHROPIC_API_KEY=$(hera-key offline) uv run hera-replay submit /data/sharpelab/hera-data/vti02-fan-scoring-v2/tranche1/tranche1.yaml

One job, twelve cells, pools claude 8 / codex 4. Expect about 60–90 min and about $250.
Eight concurrent Claude sessions on the award key is untested: watch the first ten minutes.
If episodes end `error` or `quota`, cancel the job (`hera-replay cancel`), report to Zack, and
resubmit the unfinished cells with `--parallel` lowered only on his go. `claude-opus-5` has
not run on Claude Code 2.1.283; the other five model ids have.

## After the episodes

1. Check every `run.json`: `credential` is `ANTHROPIC_API_KEY` for Claude cells, no `override`.
2. Top up: a cell with excluded episodes (harness failures, prereg § 3) gets that many more,
   so each cell has 5 counted episodes. Censored episodes count; they are not replaced.
3. Grade: `ANTHROPIC_API_KEY=$(hera-key offline) uv run hera-replay submit --grade <run dirs>`.
   A fan whose extraction fails or leaves τ or the drive untraced is re-extracted once
   (`--regrade` on that run dir).
4. Analysis: `uv run python hera/campaigns/vti02-fan-design/analysis.py <all run dirs> --out /data/sharpelab/hera-data/vti02-fan-scoring-v2/tranche1/`
   (add `--floor-unscored` only after the one re-extraction).

## Report to Zack

Lead with the four registered results (statistic, models in it, raw p, Holm p), then the
per-cell table, the censored and excluded lists, cost and wall time. Numbers first, no
interpretation beyond what the prereg registers; five per cell detects Δ ≥ 0.23 on metric 1,
so an inconclusive tranche is an expected outcome. `notify "fan tranche 1" "<one line>"` when
the analysis is written.
