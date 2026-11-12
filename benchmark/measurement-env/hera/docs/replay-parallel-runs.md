# Replay — parallel, multi-submitter runs

Design and build of record for replay jobs (`src/hera/replay/jobs.py`,
`cell.py`), shaped with Zack. Budgets, hard stops, the `--dry-run` forecast
and `requeue_quota` are deferred (§6). Not agent-visible.

## Requirement

Several workstreams (separate Claude sessions, Zack by hand) submit replay
work whenever they want, and each submitter can wait on its own submission.
Work is episodes of any mix of cells (arm, model, runner) or grading of
finished episodes. The host runs items from every live job at once, up to
per-pool slot budgets, and starts new ones as slots free up. No job waits
for another to finish, and exact fairness is not a requirement.

`hera-replay run <case>`, `hera-replay grade <run-dir>` and standalone
`hera-grade` are foreground jobs: the same lease, pools and records as a
submitted job, with the same CLI, output and exit codes. `--parallel` is that
job's cap.

**Terms.**

- **Cell**: one case file (arm × model × runner × cut).
- **Episode**: one container, one agent instance.
- **Extraction**: one grader container over one finished episode.
- **Job**: one submission. It is a list of items, each either episodes of a
  cell or extractions over a run dir. An episode item writes one run dir.

## 1. Shape

- **Submitting.** `hera-replay submit` validates the spec, refuses while
  orphans exist (§4), writes the job record, and starts the job as its own
  process under `systemd-run --user --unit hera-replay-job-<id> --collect`.
  It then prints the id and returns. The environment the job needs
  (`HERA_DATA`, credentials, `XDG_*`, `PATH`) is passed by name
  (`--setenv=NAME`), so no value lands on a command line. Its stdout and
  stderr go to `console.log` in the job dir.
- **Why detached.** The job outlives the submitting session, which matters for
  agents whose sessions end or compact, and for Bash's foreground cap.
- **Code.** The job process loads the harness when it starts. `harness`
  provenance is taken once per job and copied into every run.json. Later
  edits to the tree do not reach a running job.
- **Slots.** Pools are lock files. An item holds an `flock` for each slot it
  needs, for its lifetime. Acquisition is non-blocking and all-or-nothing, so
  it cannot deadlock. A lock is released when its process dies, so a crashed
  job cannot leak a slot.
- **Dispatch.** Each job's dispatcher starts at most one unit per 0.25 s tick,
  rotating across its items. Every live job gets roughly an equal share and
  none starves.

`hera-experiments` is not reused. It is built around `hera.variance` sample
records.

## 2. Where state lives

`$HERA_DATA` is a Syncthing folder. It holds data only: run dirs, episodes,
grades, pooled cells. Scheduling state is machine-local.

| What | Where |
|---|---|
| Pool sizes | `~/.config/hera/replay.toml`: `claude = 8`, `codex = 4`, `host = 12` (these defaults apply when the file is absent) |
| Job records, job logs | `~/.local/state/hera/replay/jobs/<id>/` (`job.json`, `job.log`, `console.log`, `records-<i>.json`) |
| Quota readings | `~/.local/state/hera/replay/quota.jsonl` |
| Slot locks | `$XDG_RUNTIME_DIR/hera-replay/slots/<pool>/<k>.lock` (tmpfs, cleared at boot) |
| Run dirs, grades | `$HERA_DATA/replay/runs/` |
| Pooled cells | `$HERA_DATA/replay/cells/<case>/<key12>/` |

A synced run dir carries its job's id, label and host in `run.json`. The job
record itself never leaves the machine.

## 3. Interface and items

```
hera-replay submit <spec.yaml> [--label L] [--parallel P] → job id; returns at once
hera-replay submit <case.yaml> --n 3 [--model M --effort E] → one episode item
hera-replay submit --grade <run-dir>... [--grader X] [--regrade] → one grade item per run dir
hera-replay wait <id>      → streams job.log, then per-item summary; exit 0 done / 1 failed or died / 130 interrupted
hera-replay status [<id>]  → pools in use, live + recent jobs (launched/done/queued, slots), orphans
hera-replay cancel <id>    → SIGTERM to that job: in-flight interrupted, queued cancelled
hera-replay reap           → stop + remove orphan containers; record dead jobs as `died`
hera-replay cell <case>    → pool the case's run dirs (§5)
hera-replay quota          → latest plan-window readings, burn rate (§6)
hera-replay run <case> ... → a foreground job, one episode item (CLI unchanged)
hera-replay grade <run-dir> [--regrade] → a foreground job, one grade item
```

An agent runs `wait` with `run_in_background` and is notified when it exits.
Ctrl-C on `wait` stops waiting only; the job goes on.

```yaml
# spec
label: G-topup                  # who/what, shown in status
parallel: 6                     # optional job cap; default: the pools alone
items:
  - {case: hera/replay/cases/vti02-fan-design-fable-corpus.yaml, n: 3}
  - {case: hera/replay/cases/vti02-fan-design-sol-none.yaml, n: 3, parallel: 2}
  - {case: ..., n: 3, model: claude-sonnet-5}        # the overrides `run` takes (model, effort)
  - {grade: $HERA_DATA/replay/runs/<case>/<ts>, grader: fan-design, n: 1, regrade: false}
```

Relative paths resolve against the submitter's cwd; `$VARS` and `~` expand.
Unknown keys, an item that names both or neither of `case`/`grade`, a
non-positive `n`/`parallel`, or a bad effort fail the submit.

**Slots per item:**

| Item | Pools |
|---|---|
| Claude episode | `claude` + `host` |
| Codex episode | `codex` + `host`; the whole `codex` pool while the harness login's access token expires within a day, so its refresh runs alone |
| Extraction | `claude` + `host` |

`run_episode` and `grade_once` are the units; records and dirs are
unchanged. An extraction sees the job's stop event and ends `interrupted`.

**What a grade item covers.**

- It takes the run dir's finished episodes that have no grade from that
  grader yet. It chooses them when the item is first dispatched.
- An episode counts as graded if it has an extraction dir from that grader
  that is still in flight (no `run.json`), or whose exit is not an
  infrastructure ending (`quota`, `interrupted`, `harness_error`).
- `--regrade` takes every finished episode.
- Episodes still in flight are left for a later grade item, so grading can
  follow a cell as its episodes complete.
- Grading is always an explicit step: a job never grades its own episodes
  unless its spec lists a grade item.
- `grades.csv` gets one row per extraction that ran, appended under an
  `flock`.

## 4. Scheduling, records, leases

- **Per-job loop.** The job prepares every episode item first: the case is
  validated, the image resolved and the cut materialized, and `run.json` is
  written. A bad cut fails the job before anything is spent, and the run
  dirs it prepared are removed. Then, while units are queued, the dispatcher
  rotates across items, acquires slots, and starts units in threads.
- **The job record** (`jobs/<id>/job.json`, schema `hera-replay-job/1`):
  - spec (normalized, plus its sha256), label, mode (`detached` |
    `foreground`), submitter cwd, unit and `systemd-run` argv;
  - lease: pid, `/proc` start time, `boot_id`, host, unit;
  - `harness` provenance, pools, job cap;
  - every container started, listed before its `docker run`;
  - per item: kind, run dir, state (`queued | running | done | interrupted |
    failed`), queued/running/done counts, statuses, slots held.
- `job.log` interleaves the per-run `harness.log` lines with the extraction
  lines.
- **Liveness.** A lease is live while its host and `boot_id` match and
  `/proc/<pid>` has the recorded start time. A reboot or a reused pid kills
  it.
- **Orphans.** An orphan is a `hera-replay-*` or `hera-grade-*` container
  that no live job lists: its harness was killed, and an agent inside may
  still be spending quota.
  - `submit`, `run` and the job process refuse to start while an orphan
    exists.
  - Grade-only foreground jobs (`grade`, `hera-grade`) do not refuse.
  - `reap` stops and removes orphans, and records dead jobs as `died`.
  - Containers from a harness older than jobs are orphans by this rule.
- **Signals.** SIGINT/SIGTERM set the job's stop event. Queued units are
  `cancelled` (not launched); in-flight episodes end `interrupted` with their
  containers stopped and removed; every run is recorded.
- **Stamps.** Run dirs, job ids and grade stamps are `20260922T201530-k3f9qz`:
  the UTC second plus a random 6-character tag. Same-second names sort by tag.
  Old unsuffixed dirs coexist. No code parses these names.
- **Byte-identical:** every `episode.json` run block field, the grade records,
  the `docker run`/`exec` argv apart from the names, the faketime computation,
  `summary.csv` and `grades.csv`. What changes: new stamps carry the tag, and
  `run.json` gains `job: {id, label, host}`. A submitted item without
  `parallel` records `parallel: null`.

Unchanged by the job layer: JupyterLab ports (each container has its own
network namespace), faketime (computed per episode at container start, so
queue delay is absorbed), per-episode `stall_s`/`timeout_s`.

## 5. Top-ups and pooling

- More episodes for a cell come from a new episode item, with its own run
  dir. Episodes are never appended to an existing run dir. `summarize` and
  `grade` work per run dir.
- A cell's sample is the union of its run dirs. `hera-replay cell <case>`
  (a yaml or a case name) groups the case's run dirs by pool key, newest pool
  first. For each pool it writes `summary.csv` and `grades.csv` (with a `run`
  column) and `key.json` to `$HERA_DATA/replay/cells/<case>/<key12>/`. The key:
  - the case as run: sha256 of run.json's parsed case block (path aside) plus
    its `override`. This works for every existing run dir, and YAML comment
    edits don't split a cell;
  - image id;
  - first-message sha256;
  - cut digest: the materialized episode dir, less what each materialization
    mints (`created_at`, and a resume cut's synthetic close-line uuid, which is
    normalized in the staged transcript too).
- A differing `harness.code_hash` inside a pool is reported, not enforced.
  Otherwise run dirs on either side of a harness change would never pool.

## 6. Quota

**Readings.**

- Claude streams carry a `rate_limit_event` at session start and again when
  utilization moves. Each has `five_hour`/`seven_day` utilization (0–1, whole
  percent), the reset times, a `status`, and `isUsingOverage`.
- Every Codex response in the rollout carries `rate_limits`: weekly
  `used_percent`, `resets_at`, the credit balance, `plan_type` and
  `rate_limit_reached_type`.
- The readings cover the whole account, interactive use included.

**Record and report** (`hera.replay.quota`).

- `quota.jsonl` gets one `reading` line per changed reading, holding time,
  runner, status, overage or plan, the windows, and the source (run dir +
  sample, or grade dir) and job.
  - Claude episode readings are logged live through `on_event`.
  - Extraction readings come from the transcript and Codex readings from the
    rollout, when the item ends.
- Each item also gets one `item` line: its first and last windows, model and
  notional cost.
- `hera-replay quota` shows the latest reading per runner with its reset
  times. It also shows the burn rate per (runner, window, model): percentage
  points of the window per notional dollar, one sample per item (first-to-last
  change within one reset), with its median, IQR and n.

**Quota status.**

- An `error`, `stall` or `timeout` with usage-limit evidence is recorded as
  status `quota`, with the evidence as the record's `quota` block. That covers
  episodes of both runners and extractions (`claude.exit`).
- It is an infrastructure failure, excluded like `error` but counted apart.
- Evidence comes only from the harness-facing channels:
  - a rate-limit event with `status: rejected`;
  - a usage-limit message in the error result, `turn.failed`, or an error
    event;
  - the CLI's stderr;
  - the Codex rollout's `rate_limit_reached_type`.

**Deferred.** These share one mechanism, holding a runner's dispatch until a
reset:

- per-job budgets gated on a projected reading;
- hard stops: overage, and an exhausted Codex week;
- the `submit --dry-run` forecast;
- `requeue_quota`.

Until they land, nothing pauses dispatch on quota. Exhaustion mid-job records
`quota` items.

## 7. External limits

Figures below come from the `rate_limit_event`s in 106 Claude episode streams
and the rollout `rate_limits` of 7 Codex episodes under
`$HERA_DATA/replay/runs/`, 2026-09-22. Quota is Zack's to manage. The
numbers are for sizing.

**Claude.** The OAuth token is plan-billed. `cost_usd` is notional. The
replay harness shares the plan with all of Zack's interactive sessions, and
grade extractions (`claude -p`, Opus) draw on it too.

- No `api_retry` events and no rejected status in any of the 106 episodes,
  including 5-way parallel Sonnet runs and four concurrent zf1 cases.
  Concurrency itself has never been the limit.
- Burn rate, other use of the account included (so an upper bound):
  - `five_hour`: roughly 0.3–0.6 % of the window per notional dollar, so one
    5-hour window holds about $170–330 of episodes.
  - `seven_day`: roughly 0.06–0.1 % per dollar, about $1000–1600 a week.

**Codex.** The plan is `prolite`, with a single weekly window. About 0.35 % of
the week per notional dollar, so a week holds about $290.

**Codex credential.** The harness has its own ChatGPT login
(`~/.config/hera/codex-home/auth.json`), read fresh for every episode. A
rotated token is written back before the episode's copy is scrubbed.
`replay-codex-path.md` §5 has the details.

- **Residual risk:** two episodes that start from the same token and both
  refresh it. The second write-back is recorded as `conflict`, and the token
  it was given is dead.
- A refresh is rare: the access token lives about 10 days.
- Mitigation: while it expires within a day, a codex episode takes the whole
  codex pool (§3).

**Host (edhar).** 32 threads, 62 GiB.

- About 33 GiB is free; other workloads hold about 28.
- A live episode container sat at 433 MiB and under 1 % CPU while its agent
  was thinking. Peaks during analysis cells have not been measured.
- Episode containers have no memory limit, since adding one could OOM-kill a
  kernel and change outcomes. Grade containers keep their 3g / 2 CPU limit.
- Contention stretches agent-visible cell times on the faked clock. The host
  cap keeps that confound small.

## 8. Wall time: 8 cells × 3 episodes

Assumed episode walls (fresh fan-design runs on record):

- Fable/Opus/Sonnet: 170–750 s, mean about 9 min, max about 12.5 min.
- sol: about 9 min. astra: 3–5 min.

| How | Wall | Notes |
|---|---|---|
| One job, 6 claude slots | ~40–45 min | 24 × 9 / 6 + tail |
| One job, 8 claude slots | ~30–35 min | Three waves, filled asynchronously |
| One job, 12 slots | ~22–25 min | About two waves; the longest episode sets the floor |
| One job, 24 slots | ~13–15 min | Max of 24 draws; `timeout_s` 1800 bounds it |
| Serial, one case at a time | ~3.6 h | 24 × 9 min |

Grading those 24 episodes shares the 8 claude slots with any episodes still
running. Two Codex cells × 3 run beside them on the codex pool.

## 9. Risks

- **Codex concurrency** on one login has run two luna episodes at once
  (2026-09-23, both `ok`, no 429); four at once and the refresh race (§7) are
  untested.
- **Burn-rate attribution** is noisy: interactive use and concurrent items
  share each reading, and Claude reports whole percent. The report gives the
  spread.
- **Host contention** changes agent-visible cell durations. The host cap
  addresses it.
- **`systemd-run --user` needs a user manager.** It exists on edhar. Rig PCs
  never run replays.
- **A killed job's run dir** keeps episodes without a run block. `summarize`
  refuses it; `cell` counts them as unfinished; a grade item skips them.
