# analysis/ — per-run HERA metrics

The metric **definitions and the extractor** live in `measurement-env`, inside
the corpus freeze tag (paper claims must be under the tag):

- Spec: `measurement-env/hera/docs/run-metrics-spec.md`
- Tool: `hera-metrics` (`measurement-env/src/tools/run_metrics.py`)

The **accumulating data** lives here. `hera-metrics` reads the manifest and
writes these outputs (`--paper-root` / `HERA_PAPER`, default this repo as the
`measurement-env` sibling under `~/sharpelab`):

- `runs.yaml` — hand-checked run manifest (spec §0). Single source of run
  inclusion + hand-checked fields (`t_final_decision`, `n_interventions`,
  `corpus_commit`, `caveats`).
- `runs.csv` — one headline row per run.
- `metrics/<run_id>.json`, `messages/<run_id>.csv`, `reports/<run_id>.md`.
- `drafts/` — capture-at-close output (`hera-metrics --archive`), pending
  hand-check before promotion into `runs.yaml`.

## Regenerate

```bash
hera-metrics --all                     # every non-excluded manifest run
hera-metrics qc0426-r3                  # one run
hera-metrics --archive <fresh-archive>  # capture-at-close: draft a new run
```

Run from the `measurement-env` checkout (or with the installed `hera-metrics`
shim); pass `--paper-root <this repo>` when the tool can't find it as a
sibling (e.g. running from a git worktree).
