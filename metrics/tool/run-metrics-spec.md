# Per-run metrics spec — v0.2

What we compute for each HERA run on QC0426 (VTI) and zf1/b1c2 (toploader),
feeding Fig. 2 and the expert-evaluation dossiers.

Homes (the freeze split):

- **Definitions + tool** live here in `measurement-env`, inside the corpus
  freeze tag: this spec, the extractor (`src/tools/run_metrics.py`, tool
  `hera-metrics`), and the utilization tool it consumes
  (`hera-utilization`, `hera/docs/hera-utilization-design.md` — this spec
  consumes its output, it does not respec it).
- **Accumulating data** lives with the paper in `hera-paper/analysis/`: the
  run manifest (`runs.yaml`), the headline table (`runs.csv`), and the
  per-run outputs. `hera-metrics` reads the manifest and writes there
  (`--paper-root`, default the `hera-paper` sibling under `~/sharpelab`).

Scope: the 2026-06 campaigns, **"real" QC0426 and zf1 runs only**. Excluded:
May b1c2 sessions (pre-stamps, different social contract), IRIS-mode
sessions (incl. `20260623-QC0426`), the qswitch investigation. The last
three QC0426 runs are a **variability set** — identical config run 3×;
flagged in the manifest, analyzed together. The capstone rerun and the
blinded series (which pin a corpus freeze tag) extend the same manifest.

## Sources, per run

| Source | Gives |
|---|---|
| `data/<id>/metadata.json` | sweep start/end (epoch), recipe slug (`comments[0]`), instrument config |
| `corpus_provenance.json` | corpus git hash + dirty flag stamped at session creation (06-… runs predate the stamp) |
| `*_measure.ipynb` cell `metadata.hera.appended_at` | HERA cell-landing stamps (06-14 onward) |
| `transcripts/*.jsonl` | timestamps, human vs agent messages, tool calls, token usage, interrupts |
| `hera_session.md` | autonomy mode, campaign goal, caps |
| `session_notes.md` | FEEDBACK / RECIPE FIX / TOOLING / PROTOCOL tagged entries |
| `hera_scratch/` | analysis working set (scripts, scratch notebooks, figures) |
| `hera/docs/triage-scoreboard.md` (+changelog) | between-run loop metrics (already tabulated) |

Archives must be **as complete as possible** before extraction. A couple of
runs are missing transcripts to a since-fixed bug; best effort there, gaps
flagged, never imputed.

## 0. Run manifest (`runs.yaml`, hand-checked)

One entry per run:

```yaml
- run_id: qc0426-r3           # campaign ordinal, stable key
  device: QC0426              # QC0426 | zf1
  rig: vti                    # vti | toploader
  date: 2026-06-16
  mode: E1                    # E0 | E1 (from brief)
  archive: measurement-env/hera/docs/notes/2026-06-16-QC0426-session
  rig_session_dir: zack/20260616-QC0426   # the dir the measurement agent ran in (see below)
  layout: root                # root | artifacts (old whitelist era)
  transcript: full            # full | partial | export-only
  variability_set: false      # true for the final 3 QC0426 runs
  corpus_commit: null         # corpus git hash, from the stamp (see below)
  t_final_decision: null      # ISO ts, located per run (see §1), hand-checked
  n_interventions: null       # confirmed count (see §5), hand-checked
  session_start_override: null  # ISO ts; only when the session transcript is missing (see §1)
  session_end_override: null    # ISO ts; operator-ruled end, or the end of a lost-transcript session (see §1)
  caveats: []
```

The manifest is the single place run-inclusion decisions live; everything
downstream iterates over it.

### `rig_session_dir` — which transcript is the session's

An archive can hold more than one jsonl: the `hera-session` setup agent runs
from the shared `measurement_env` checkout and its transcript is often
archived next to the measurement agent's; neighbouring sessions' files turn
up too. `rig_session_dir` is the directory the measurement agent was launched
into (`newclaude <dir> --agent hera-tactical`; the `cwd` of its transcript
entries). The extractor keeps only the jsonl whose `cwd` basename matches it
and counts the rest as `n_extraneous_transcripts`. When nothing matches, the
session transcript is **absent**: tokens null, message counts zero,
`n_transcript_files: 0`. The extractor never falls back to the other files,
because a setup agent's 20 requests would otherwise stand in for a lost 9-hour
session. Lost-transcript archives may carry the harness's own per-project
record (`transcripts/recovered/claude-project-entry.json`, copied from the
rig's `~/.claude.json`); it is reported as `harness_session_totals` (model,
tokens, harness cost, window open) beside the transcript metrics and is not
entered in `runs.csv`.

### `corpus_commit` — the corpus-time-series join key

The corpus git hash each run executed under. Fig. 2's between-run
improvement is a function of corpus version, so `corpus_commit` is the join
key against the triage changelog and the freeze tag.

**Extraction path — stamp at session creation.** `hera-mksession` writes a
neutral `corpus_provenance.json` into the session dir when it deploys the
cards/notebooks:

```json
{"corpus_commit": "742f0d8…", "corpus_dirty": false,
 "created_at": "2026-07-…Z", "rig": "VTI", "device": "QC0426"}
```

`hera-archive` mirrors it wholesale; `hera-metrics` reads it back. The hash
is a mechanical fact with no scientific lean — blinding-safe in the
agent-visible session dir. `corpus_dirty: true` (uncommitted corpus at
deploy) makes the join approximate; flag it as a caveat.

This is exact for the capstone rerun and the blinded series (the runs the
paper axis needs). The **June retrospective runs predate the stamp** →
`corpus_commit: null`, flagged. Reconstructing them from archived-artifact
content is unreliable (device cards mutate per cooldown so don't match a
corpus commit; rig cards change rarely so match ambiguously) — left to
optional hand archaeology, never auto-imputed.

## 1. Time metrics

- `t_transcript_first` / `t_transcript_last`, `transcript_span_h` — raw
  agent-session envelope (min/max over all jsonl files).
- **`session_h`** — headline wall clock: transcript span **trimmed** of
  trailing post-run operator discussion (retrospectives, triage chatter,
  "chat a bit about…"). Trim point = end of the last measurement-serving
  activity (last sweep end, last landed cell, or the final call — whichever
  is latest); the final closeout write-up counts (ruling 2026-07-06).
  **Deliverable-complete standby ends the session**: if HERA declares the
  deliverable complete and stands by, and the operator later returns and
  extends the run, the session ends at the standby declaration
  (`session_end_override` in the manifest); the extension is post-session,
  excluded from session_h/utilization/sweep counts, and its operator
  messages count as a **strong intervention** (ruling 2026-07-06, from
  qc0426-r10). A *premature* standby the operator corrects (qc0426-r5) is
  NOT a session end — the idle stays charged to HERA court.
  **Lost transcript**: when the archive has no session transcript, the
  manifest anchors the session with `session_start_override` (the measurement
  agent's launch, from the setup agent's transcript or the rig's file times)
  and `session_end_override` (the latest of the last landed cell, the last
  sweep end and the final call, by the rule above); `session_h` is their
  difference and `longest_unattended_h` is null, since the operator messages
  are unknown. The override's evidence is cited in a manifest comment and in
  the archive's `transcripts/recovered/README.md`.
- **`t_final_decision`** — when HERA delivers the final call (the
  campaign-goal verdict: stacking call / SC determination). Located by
  LLM-assist over transcript + session_notes + ana notebook, hand-checked,
  pinned in the manifest.
- **`decision_h`** = t_final_decision − t_transcript_first. Time-to-result.
- `t_first_sweep`, `t_last_sweep_end`, `sweep_span_h` — the utilization
  denominator (per the utilization design doc).
- `measuring_h` — Σ sweep durations (overlap-merged).
- `n_sweeps`, `sweeps_by_recipe` — count + hours per recipe slug.
- `longest_sweep_h`.

## 2. Utilization (from `hera-utilization`)

Three-way split of sweep_span, mapping to Fig. 2's bar:

- `util_measuring` — fraction actively sweeping ("active ops").
- `util_hera_court` — idle charged to HERA ("thinking").
- `util_human_court` — idle waiting on the operator ("human").
- `raw_utilization` = measuring / span; `hil_utilization` = measuring /
  (span − human_court).
- Per-gap table retained in the run JSON (audit trail).
- qc0426-r1 (06-10): no stamps → raw only; court split = null.

## 3. Message / transcript metrics

User-type entries partitioned into (mutually exclusive):

- `n_loop_ticks` — scheduled autonomous-loop ticks ("# Autonomous loop…").
- `n_task_notifications` — harness `<task-notification>` injections.
- `n_admin_msgs` — session bootstrap (brief injection, install/boot chatter).
- `n_human_msgs` — everything else typed by the operator. **The auditable
  raw count.**
- `n_interrupts` — "[Request interrupted by user]" markers.

Agent side:

- `n_assistant_turns`.
- **Tool-use set**: `n_tool_calls` total + by tool — nb-collab lands (append)
  vs waits, nb reads, Read/Write/Edit, Bash, subagent/Task spawns,
  hera-watch/notify invocations. Broad v0 net; we prune to the interesting
  ones after seeing the numbers.
- **Tokens & cost**: `tokens_in`, `tokens_out`, `tokens_cache_read`,
  `tokens_cache_write` (summed per-turn usage, split by model), plus
  `cost_usd_est` from a pricing table pinned in the extractor (per-model
  in/out/cache rates, priced at time-of-run). Export-only runs: null.
- `transcript_completeness` — full / partial (06-23 zf1: `recovered/`) /
  export-only (06-24 zf1: markdown export; message counts best-effort,
  tokens null).

## 4. Notebook & scratch metrics

Measure notebook:

- `n_cells`; `n_hera_cells` (appended_at); `n_slot_cells` (template
  autofill); `n_human_cells` (remainder).
- `n_hera_executed` / `n_hera_unexecuted` — executed = execution_count or
  outputs present. Unexecuted landed code cell = **veto proxy**.
- `n_superseded` — corrected-cell chains ("cell 35 supersedes cell 33");
  v0: extracted from markdown-cell text + session_notes, LLM-assist +
  human check.

Ana notebook: `n_ana_cells`, `n_ana_figures` (image outputs).

`hera_scratch/` (analysis effort behind the curtain):

- `n_scratch_files` by type (py / ipynb / md / png / other).
- `scratch_loc` — code lines across .py + notebook code cells.
- `n_scratch_figures` — pngs + embedded notebook images.
- `n_scratch_notebooks`.

## 5. Interventions & autonomy (the judged layer)

**A science-judgment metric**: how much operator judgment did the run
consume? Most meaningful for E1 runs; in E0 the signal is steering-vs-mere-
approval. Each of `n_human_msgs` gets a label (draft auto, Zack reviews;
labeled CSV ships with the run for auditability):

| label | meaning | counts as intervention? |
|---|---|---|
| `correction` | overrides/redirects HERA (wrong physics, wrong plan, bad cell) | yes |
| `steering` | scope/priority change not prompted by an error | yes |
| `expert-input` | physics context supplied (asked-for or volunteered) | **yes** (see rule) |
| `handshake` | E0 run-this/ran-it traffic, autonomy grants | no — the E0 contract, counted as `n_handshakes` |
| `logistics` | rig/ops chatter, closeout, social | no |

### Counting rule — the bar is **potentially arc-altering**

An intervention is an operator-authored message (or veto action) that
**could shape the arc** — the direction HERA takes from here. The bar is
*potential*, not realized: important physics context can redirect the run
much later, so it counts when supplied, not only when its effect is visible.
Two people counting the same transcript should agree by this procedure,
message by message:

- **Counts.** A correction (wrong physics / plan / cell); unprompted
  steering (scope or priority change); a **substantial physics or expert
  comment** (asked-for or volunteered — treated as potentially arc-altering);
  a veto (an interrupt, or a landed-but-abandoned HERA cell); an
  edited-then-run cell; an E0 new-directive drop; the r10-style
  post-session-extension (strong).
- **Does not count.** E0 run-this / ran-it handshakes; a "yes / proceed"
  consent to an agent-initiated ask that *confirms* HERA's already-stated
  path; passive acks ("ok", "nice", "thanks"); status pings; logistics,
  closeout, social.
- **Tie-breaker for a consent reply.** A response to an agent-solicited ask
  counts only if the answer changes HERA's course — a "no / do Y instead".
  A bare "yes" confirming the proposed path does not.
- **Substantial vs passing.** A physics comment counts when it carries
  content that could bear on a measurement or interpretation decision; a
  bare acknowledgement or social aside does not. When genuinely torn,
  count it — the bar is *potential* influence.

Aggregates:

- `n_interventions` = correction + steering + expert-input + interrupts +
  vetoes + edited-then-run cells (where detectable). **Fig. 2's
  "Interventions."** Sub-counts always reported so the boundary is
  auditable. Expected ~0 for E1 capstone/series runs — but recorded
  whenever it happens.
- `n_feedback_notes` — FEEDBACK entries in session_notes (cross-check
  against the message labels; discrepancies resolved by hand).
- `longest_unattended_h` — longest stretch with no human-typed message
  during which ≥1 sweep started (work continued without input).
- `mode` (E0/E1) from the brief — **always annotated in Fig. 2** so the
  intervention decline isn't read as apples-to-apples across the E0→E1
  category change; `util_human_court` (§2) is the continuous autonomy
  signal.

## 6. Between-run loop metrics (campaign-level join)

From the triage scoreboard/changelog, keyed by the *gap* between run N and
N+1 — Fig. 2's improvement blurbs; joined on `corpus_commit` (§0):

- `n_triage_items`, `acc_unmodified_rate`, `n_recurrences`, `corpus_delta`.
- Items classified `self-extracted` vs `expert-feedback` (source stream:
  agent's session_notes vs Aaron/operator log).
- Gaps with no triage crank recorded as null, not zero.

## 7. Expert evaluation (reserved)

- `quality_expert` — Aaron's score per run; **rubric and dossier content
  TBD** (separate discussion). Fields reserved: score, rubric version,
  blind status, dossier wiki link.

## Capture-at-close

Retrospective extraction over the June archives was archaeology. For the
capstone rerun and the blinded series, capture fires at session close-out,
right after the archive lands — a standalone one-command step, **not owned by
Chiron** (Chiron runs `hera-archive` as its own step 0; metrics stay
decoupled):

```bash
hera-archive <rig session-dir>          # snapshot artifacts + transcripts
hera-metrics --archive <fresh archive>  # draft manifest entry + csv row
```

`--archive` mode auto-derives the mechanical fields (date, device/rig,
archive path, layout, transcript completeness, `corpus_commit` from the
stamp) and runs the full extraction, then emits a **DRAFT manifest stanza**
plus the per-run JSON / report / draft csv row. Judgment fields —
`t_final_decision`, `n_interventions`, `variability_set`, `caveats` — are
printed as explicit `HAND-CHECK` placeholders, **never auto-filled
silently**. The operator confirms them and pastes the stanza into
`runs.yaml`; a later `hera-metrics <run_id>` re-extracts against the settled
manifest.

## Outputs (in `hera-paper/analysis/`)

- `metrics/<run_id>.json` — full per-run structure (everything above incl.
  per-gap and per-sweep tables).
- `messages/<run_id>.csv` — timestamped labeled human messages.
- `reports/<run_id>.md` — rendered per-run report.
- `runs.csv` — one row per run, headline columns: run_id, device, date,
  mode, corpus_commit, session_h, decision_h, measuring_h, n_sweeps, util
  three-way split, n_interventions (+sub-counts), n_handshakes, n_human_msgs,
  tokens_out, cost_usd_est, longest_unattended_h, quality_expert.

## Known per-run caveats (v0 inventory)

| run | caveat |
|---|---|
| qc0426-r1 (06-10) | no stamps → raw utilization only; data re-pulled 2026-07-06 |
| qc0426-r2 (06-14) | old `artifacts/` layout (extractor handles both) |
| qc0426 06-19.2 / 06-21.2 | archived 2026-07-06 (were rig-only) |
| zf1 06-23 | tactical transcript lost; the archive's two jsonl are the setup agent's; `recovered/` holds file-history, task outputs and the harness record (model `claude-opus-4-8[1m]`, $76.75, 20.0 h window); session 22:17:53Z → 07:24:29Z from the launch command and the last cell stamp |
| zf1 06-24 | tactical transcript lost; terminal export only; the jsonl is the setup agent's; `recovered/` holds task outputs and the harness record (`claude-opus-4-8[1m]`, $30.74, 6.5 h window); session 22:50:40Z → 03:24:08Z |
| zf1 (all) | `rig_session_dir` is the per-session dir under `aaron/` on the toploader, not the device owner's `Isaac/b1c2_toploader` |
| June runs (all) | predate the corpus-provenance stamp → `corpus_commit` null |
| (bug-era runs) | transcript losses from the since-fixed newclaude bug — best effort, gaps flagged |

## Open questions (iterate)

1. **t_final_decision detection rule** — what exactly counts as "the final
   call" when a run ends without one (variability runs may re-confirm an
   existing call; some runs are characterization-only)? Proposal: the last
   campaign-goal-level verdict statement; runs with no verdict get
   decision_h = null, not session_h.
2. **Cost pricing table** — pin per-model rates (opus/sonnet, cache
   read/write) and note assumption that rates at time-of-run apply.

## Changelog

- **v0.3** (2026-10-26) — `rig_session_dir` selects the session transcript
  strictly (no fallback to other agents' files); `session_start_override`;
  `harness_session_totals` from a recovered `claude-project-entry.json`;
  `longest_unattended_h` null without a transcript; `claude-opus-5` priced.
  Prompted by the zf1 06-23 and 06-24 runs, whose metrics had been computed
  from the setup agent's transcripts.
- **v0.2** (2026-07-17) — migrated into `measurement-env` (definitions +
  tool inside the corpus freeze tag; data stays in `hera-paper`). Added
  `corpus_commit` (stamp-at-creation join key) and the concrete
  `n_interventions` counting rule (potentially-arc-altering bar).
- **v0.1** — initial spec, retrospective extraction over the June archives.
</content>
</invoke>
