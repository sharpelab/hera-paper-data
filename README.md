# HERA I — data and code snapshot

Companion data and code for *HERA I. The tactical layer: self-improving
autonomous measurement of quantum materials* (Sharpe Lab, Stanford). This is a
flat snapshot, without version history, of the measurement harness, the agent
corpus it ran with, every measurement session the paper draws on, the expert
grading, and the sealed Raman evidence. It is built by `tools/build_snapshot.sh`
from the lab's working repositories; `MANIFEST.md` records the source and commit
of every directory and `CHECKSUMS.sha256` covers every file.

## Layout

| directory | what it is |
|---|---|
| `measurement-env/` | The harness and corpus as frozen for the blinded trial: launcher and instrument workers, the `sweep`/`measurebot` libraries (vendored under `lib/`), the HERA agent prompts (`hera/hera_tactical.md`, `hera/chiron.md`, `hera/iris.md`), recipes, rig cards, device-card templates, session templates and briefs, replay fixtures, the fix log the triage loop maintains (`hera/docs/triage-changelog.md`, `triage-scoreboard.md`, `eng-backlog.md`), the operator's live-session logs for the QC0426 sessions (`hera/docs/vti/`), the launcher shims (`tools/`), and the replay and metrics tooling (`src/hera/`, `src/tools/`). `uv.lock` pins the Python environment. |
| `corpus-variants/` | One patch per other corpus commit a session ran on, against the frozen tree, plus `corpus-timeline.md` mapping every session to its commit. Apply from inside `measurement-env/` with `git apply <patch>`. |
| `sessions/` | The session archives, one directory per measurement session, grouped by device (`qc0426/`, `zf1/`, `vti-01/`, `vti-02/`). Each holds the measure and analysis notebooks, the raw sweep data (`data/<run>/data.tsv.gz` + `metadata.json`), the device and rig cards as the agent saw them, `hera_session.md` (the brief), `session_notes.md`, the agent's scratch scripts and figures (`hera_scratch/`), and the full Claude Code transcript (`transcripts/*.jsonl`). |
| `campaigns/stacking/` | The blinded stacking trial: pre-registration (`prereg-protocol.md`, `prereg-offline-stages.md`), the deviations register, and per device the transport call, Raman read, fusion verdict, expert adjudication and comparison. `read-keys/` holds the claim keys used for grading. |
| `grading/` | The expert-grading repository: claim extraction and pooling, Pass A (item-level) and Pass B (session-level) scores, rater materials, agreement analysis, and the pre-registration for both passes. Tags referenced in the paper (`t1-scores-frozen`, `passb-scores-frozen`) correspond to this state. |
| `metrics/` | Run manifest (`runs.yaml`), the headline table (`runs.csv`), and per-run metrics, message logs and reports produced by `hera-metrics` (`measurement-env/src/tools/run_metrics.py`, spec in `measurement-env/hera/docs/run-metrics-spec.md`). |
| `benchmark/` | The offline benchmark, the vti-02 fan-design replay matrix of Fig.~4 and Methods. `measurement-env/` is the lab repository again, at the commit that declared the pre-registration: the replay harness (`src/hera/replay/`, `hera/docker/`), the fan-design grader (`hera/graders/fan-design/`, `hera/docs/fan-design-grader.md`), the pre-registration and its analysis script (`hera/campaigns/vti02-fan-design/`), and the case files, briefs and masks (`hera/replay/cases/`). `runs/vti02-fan-request-0822/` holds the frozen state every episode started from (`cut/`) and the 41 run directories of record, one per `<case>/<stamp>`, each episode with its transcript, the notebook as the agent left it, the appended cells, and the grader's extraction and scores (`INDEX.md` lists them). `vti02-fan-scoring-v2/final/` is the analysis of record (`analysis.md`, `analysis.json`, `episodes.json`, the post-hoc extraction audit and the read-only variance reads); the other directories are the grader-development record the pre-registration discloses. `figures/fig4_benchmark.py` draws Fig.~4 from `final/analysis.json`. |
| `hera-data/` | Sealed Raman evidence (WITec `.wip` files, layouts, micrographs) for QC0426, vti-01 and vti-02; the offline agent stages that read the Raman and fused it with the transport call (`raman-*-read`, `raman-*-fusion`, with their launch payloads); and the synthetic validation of the tetralayer Fermi-surface-count model. |

## How the pieces map to the paper

- **Blinded prospective trial**: `sessions/vti-01/`, `sessions/vti-02/2026-08-21-*`, `campaigns/stacking/{vti-01,vti-02}/`, `hera-data/raman-vti-0*`.
- **Model × corpus matrix**: `sessions/vti-02/2026-08-22-*` through `2026-08-25-*`, `campaigns/stacking/{vti-02-20260822,vti-02-20260824,vti-02-20260825,ablation-2026-08}/`, `grading/`, `corpus-variants/corpus-039b0f5.patch` (the no-corpus deploy).
- **Domain transfer**: `sessions/zf1/`, recipe under `measurement-env/hera/recipes/investigations/`, rig card `measurement-env/hera/rig-cards/toploader.md`.
- **Offline benchmark** (Fig.~4, Methods, Replay benchmark): `benchmark/`. The corpus arm's image was built from the frozen tree in `measurement-env/`; the no-corpus arm's from `corpus-variants/corpus-039b0f5.patch` applied to it. Reproduce the analysis of record with `uv run python hera/campaigns/vti02-fan-design/analysis.py <run dirs>` from inside `benchmark/measurement-env/`, and Fig.~4 with `uv run --project measurement-env python figures/fig4_benchmark.py`.
- **Measured improvement** (the QC0426 ladder): `sessions/qc0426/`, `metrics/`, and the corpus evolution in `corpus-variants/`.

Session dates, autonomy mode, archive layout and known caveats per run are in
`metrics/runs.yaml`. `sessions/INDEX.md` lists every session with the model it
ran on, taken from the `model` field of its transcript.

## Reproducing the environment

```bash
cd measurement-env
uv sync            # Python >= 3.10; some instrument drivers are Windows-only
```

The rig-specific config files (`toploader.toml`, `vti.toml`, `pink.toml`) are
not included; templates are the `*.toml.example` files. Hardware workers need
the instruments; the analysis code, replay tooling and metrics extractor run
anywhere.

## What is deliberately not here

- Third-party PDFs (papers, instrument manuals) and the public Raman datasets
  used for model validation. The latter are cited by DOI in
  `measurement-env/hera/docs/raman-public-data.md`.
- Sessions on devices outside the paper, and the offline replay runs
  (`hera/test-cases` run directories); the replay fixtures themselves are in
  `measurement-env/hera/test-cases/`.
- The benchmark's development episodes (the free-choice frontiers the grader
  was developed on, which the pre-registration discloses), the exploratory
  medium-effort arm run on 2026-10-03, and the earlier frontier-sampling
  pipeline (`hera/evaluations/`, `hera/experiments/` at the benchmark commit),
  none of which the paper reports.
- Design notes, proposals, dev specs and material for rigs and campaigns
  outside the paper. `MANIFEST.md` lists what was removed from the frozen
  tree.
- The lab's InfluxDB and Slack credentials. Jupyter server tokens that appeared
  in transcripts are replaced with `REDACTED`.

## Provenance

- Frozen corpus commit: `13b07e9` in the lab's `measurement-env` repository
  (tag `arm1-freeze` plus the vti-02 brief and device card). See
  `corpus-variants/corpus-timeline.md` for every other session.
- Benchmark commit: `58d02e64` in the same repository, the commit that adds
  `hera/campaigns/vti02-fan-design/prereg.md`.
- Build: `tools/build_snapshot.sh`; the manifest it writes is `MANIFEST.md`.
- Repository: https://github.com/sharpelab/hera-paper-data
- Verify: `sha256sum -c CHECKSUMS.sha256`.

## License and citation

License: to be set before public release; code and data will carry different
licenses. Two vendored packages keep their own: `measurement-env/lib/measureme`
is GPL-3.0 and is a copy of
[sharpelab/measureme](https://github.com/sharpelab/measureme) at tag
`hera-paper-freeze` (branch `sharpelab`); `measurement-env/lib/measurebot` is
MIT, from [sharpelab/measurebot](https://github.com/sharpelab/measurebot).

Citation: to be added when the paper and the Stanford Digital Repository DOI
are available.
