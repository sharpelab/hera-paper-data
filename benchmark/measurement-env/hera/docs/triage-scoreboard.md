# Triage scoreboard — is the loop helping?

Self-measurement for the HERA feedback loop (see
`hera/docs/triage-workflow.md` §self-measurement). One row per
triaged session, appended by Chiron at the end of each run. Metric
definitions:

- **items** — triage-queue size (both note streams + transcript-mined).
- **latency** — note timestamp → landed commit, median (max).
- **acc. unmod.** — accepted-unmodified rate: rulings that matched the
  recommended disposition with the diff landing as drafted. The
  graduation metric (per-class breakdown in the run's notes section
  when a class approaches graduation).
- **recur.** — burn-logged failure classes that fired again this
  session. The loop's true effectiveness metric; target 0.
- **corpus Δ** — net lines added−removed across recipes/STYLE/prompts.
- **misses** — items the human surfaced that the queue didn't (Chiron's
  own burn log).

| session | triaged | by | items | latency | acc. unmod. | recur. | corpus Δ | misses |
|---|---|---|---|---|---|---|---|---|
| 2026-06-10 QC0426 (VTI) | 2026-06-11 | interactive prototype | ~30 dispositions (16 numbered rows) | ~24 h (≈48 h) | ~70 % (retrospective est.) | — (first burns recorded) | +≈400 (STYLE created +192) | n/a (human-driven) |
| same session — **blind dry run** | 2026-06-12 | chiron v0 (calibration) | 47-row queue; coverage 27/29 GT dispositions | n/a (drafts only, nothing landed) | **52 % strict / 79 % lenient** vs actual rulings | 0 (vacuous — baseline session) | n/a (proposals: ~+250 if all landed) | 2 + 1 partial (scratch-nb retirement; estimate-bias rule; Examples setpoint scrub) |
| 2026-06-14 QC0426 (VTI) | 2026-06-16 | **chiron R3 (first real crank)** | ~34 items → 28 resolution rows | ~2 d (notes 06-14 → land 06-16) | **~64 %** (9/14 substantive accepted unmodified; modified: B-1, R-1, R-3, P-2, T-8) | **2** landed-fix regressions (`blinded-r2-set` round-N leak; `landau-fan-cost-nyquist`/burn #2 n_max) + 2 backlog triggers fired (BL-1, BL-2) | **+227** corpus (recipes/STYLE/prompts/cards/blinding); +244 tooling; +315 docs | **1** (burns-to-bottom STYLE convention — inlined a burn instead of bottom+pointer) |
| 2026-06-16 QC0426 (VTI) — first autonomous E1 | 2026-06-17 | chiron R4 | ~28 resolution rows | ~1 d (notes 06-16 → land 06-17) | **low (~20 %)** — nearly every L2/L3 item modified: heavy prose trims (chiron over-editorialized, corrected ~5×), DC-3/DC-4 dropped, all 4 recipe edits pulled to Aaron's pass | **3** (`nbcollab-watch-mode` re-fired, `hera-watch-longrun`, `nb-collab-wait-loud`) + K-1 adherence miss (not a fix regression) | **+19** (prompt +7, device-card findings +12; recipes/STYLE 0 — deferred; excl. device-card R3 rebase) | 0 coverage misses (queue complete); chiron's own burns = editorializing + recipe-domain over-reach |
| 2026-06-17 QC0426 (VTI) — 2nd autonomous E1; first `fs-count` run | 2026-06-18 | chiron R5 | ~24 items → resolution rows | ~1 d (notes 06-17 → land 06-18) | **low (~25 %)** — disposition agreement high but routing/diffs reworked: R-1/A-5/A-6/A-7 broadened to /subtask, T-1 prompt-note→tooling, P-4 split, R-3 to rig `.env`; **editorializing recurred** (3 edits reverted, halted mid-run → Corpus Style rule landed) | **3** (`si-gate-inter-delay` regressed via template re-fork; `lakeshore-single-poller` fired 3rd — run-0 kill; `brief-slack-slot`/`hera-notify` no-recipient 3rd) | **+~9** corpus (prompts +8, recipe/card ~0/−1; STYLE 0); **+~100** tooling (`append --execute`); +large docs (Corpus Style, changelog, aaron-handoff) | **operator-log stream**: Aaron's support log lived on the wiki, not the repo — not pulled until Zack surfaced it; ~6 qualitative items (over-range, density, bias-current, closeout, K2400, E0-after-run) missed on first pass |
| 2026-06-23 zf1 (toploader) — SC characterization; first toploader crank | 2026-06-24 | chiron zf1-0623 | ~17 items → 16 rows | ~1 d (notes 06-23 → land 06-24) | **~75 %** — drafts landed as drafted except **I** (heater asymmetry over-claimed → cut by Aaron live); routing narrowed F/H/D to backlog; recipe-science A/B/C/K drafted + routed to aaron-handoff | **3** landed-fix recurrences (`zf1 T2`/coherence, `zf1 T3`/field-kill+Fraunhofer, `zf1 T4`-recast/gate-range — all live on the rig, all refired) + slot-autofill trigger fired | **+31** corpus (recipes/card/prompt/template); +74 docs (backlog/handoff); +~155 changelog | 0 coverage misses; chiron burn = over-claimed heater asymmetry from an invalid up-ladder (caught by Aaron) |
| 2026-06-24 zf1 (toploader) — SC-char marathon; first full autonomous E1 toploader run | 2026-06-25 | chiron tl_crank | ~25 (9 fixes + 4→Aaron + record-only; 6 hera-session set aside) | <1 d (notes 06-24 eve → land 06-25) | **~60 %** — dispositions agreed; Zack re-routed most fixes to /subtask (not agent+review), set aside S1/S2/S4/S6 (S6 un-set) + all hera-session items; trip_color landed as drafted on his call | **3** landed-fix recurrences (`plot-all-live` 2T omission, `thermo-staleness` deploy-path miss, `newclaude-transcript-loss` 2nd) + slot-autofill 3rd | **+~25** corpus (prompt/brief/recipe); **+~170** tooling (nb_collab/hera-watch/gates); +large docs | **1** (chiron inverted the hera-session "filter" — kept the set it should've dropped; Zack corrected) |

## Notes

**2026-06-24 zf1 (toploader) — SC-characterization marathon; tl_crank.** Landed
on `hera` via `subtask/tl_crank` (ff-merge, no push). 9 fixes, one per subtask,
fanned out and folded.
- **Wins**: `gate-current-sanity-rewrite` passed its first real toploader test
  (4 legs clean to card limits); both of nb-collab's documented QC0426 footguns
  (570s-timeout-as-completion, inline backticks) got *enforced-in-tool* fixes
  after recurring — README prose alone hadn't stopped them; the I_bias ×25 fix
  was verified against the session's real `data/9` metadata.
- **Recurrences (3)**: `plot-all-live` (2T `fp`'d but unplotted on the survey
  map → fixed in the brief); `thermo-staleness` (the landed guard had never
  reached the *deploy* template → ported); `newclaude-transcript-loss` (2nd
  consecutive marathon-transcript loss — the backup hook silently no-op'd → rig
  maintenance flag). `slot-autofill` fired a 3rd time (placeholder B-cap 5.0 T vs
  0.1 T, caught by hera-session).
- **Routing**: Zack drove tightly — nearly every fix became a `/subtask` rather
  than agent+review; recipe-science (S1/S2/S4 + the calc idiom) deferred to
  `aaron-handoff`; `trip_color` landed on his call over the crank's trim rec.
- **Chiron's own burn**: inverted the hera-session "filter" instruction — kept
  the hera-session/init items when Zack wanted them dropped for the actual-session
  findings; corrected on his steer.
- **Transcript reality**: the tactical marathon ran as a `newclaude`-spawned
  session whose jsonl was never persisted (only `.claude/file-history` survived).
  Reconstructed from `session_notes` + both notebooks + 12 scratch scripts + data
  mtimes; the init transcript witnessed the session-init phase.

**2026-06-17 R5 — 2nd autonomous E1; first `fs-count` run.** Landed on `hera`
via `subtask/triage-20260617-QC0426` (ff-merge, no push).
- **Wins**: the reworked `trilayer-stacking-fs-count` produced a strong,
  well-hedged ABA call on its first run; the watch-mode cluster held (7 h fan
  monitored, no stall/silent-timeout — R4 streak broken); `no-hand-roll-analysis`
  held (helpers + `open_run`, 0 FFT re-rolls); peak context ~390k (vs R4 ~907k).
- **Recurrences (3)**: `si-gate-inter-delay` regressed because the round-4
  template was re-forked fresh and dropped the fix (→ template-dedup /subtask);
  `lakeshore-single-poller` fired a 3rd time (hardcoded `fp(temperature)` in
  gate-current-sanity-check killed run 0 → R-2); `hera-notify` had no recipient
  a 3rd time (Aaron's Slack unset → maintenance `.env`).
- **Chiron's own burns this session (two)**: (1) **editorializing recurred** —
  restated hazards, a backlog cross-ref in the rig card, and an edit to a
  *completed* brief; Zack halted the run and reverted 3 edits. Fixed structurally
  by landing the **Corpus Style + Editing** rules into `hera/CLAUDE.md` (so
  subtasks + delegated agents inherit it) and a `chiron.md` "No editorializing"
  rule. The first delegated nb-collab agent (spawned *before* the rule) also
  editorialized two doc files — reverted, rewritten terse. (2) **Coverage miss** —
  declared the support-log stream absent when Aaron had kept it on the **wiki**;
  pulled it only after Zack pointed at it, then folded ~6 operator-only items.
- **Routing**: Zack broadened most crank recommendations — R-1/A-5/A-6/A-7 to
  /subtask (propose-first), T-1 from a prompt-note to a tooling affordance
  (`append --execute`), P-4 split (driver backlog + aliasing subtask), R-3 to a
  rig `.env` write. The gate kept doing design work.
- **Subtask landings**: A-7 progress-bar (`fcef889`) + R-1/P-4.2 template-dedup
  (`19ef0c0`) landed; A-5 closeout → backlog; A-6 `k2400_ramp_behavior` held open
  (not this cut); P-4.1 DC205 driver → follow-up subtask.


- **Wins**: the `fan-nyquist`/burn-#2 recurrence streak **broke** (HERA went
  finer in B, didn't coarsen); blinding exemplary (deferred the card write-back
  mid-session); temp ban honored (no LS335 two-masters recurrence).
- **Top lever (A-1)**: HERA hand-rolled the entire analysis stack (50× json.load,
  40× detrend, 17× rfft) instead of the recipe-cited `hera.analysis` helpers —
  the root of "coding mode" + ~907k peak context. Fixed with a prompt bullet.
- **Regressions (3)**: the watch-mode cluster (`--next` stall on 2nd+ runs,
  block-buffered `--follow`, silent `wait` timeout) re-fired → /subtask.
- **Low acceptance (~20%) is mostly chiron's own fault**, two patterns to fix in
  the crank: (1) **over-editorializing** — verbose, reason-padded prose corrected
  ~5× before terse versions landed; (2) **recipe-domain over-reach** — drafted 4
  recipe/model edits that belong to Aaron's science pass; all pulled and deferred
  to `aaron-handoff.md`. Route recipe-science items to Aaron by default; keep
  prompt/card/tooling for the crank.
- **K-1** was *not-sent*, not a delivery regression (other notifies landed) —
  HERA didn't fire the grant-ack/re-grant notify the prompt already lists.

 Landed on `hera` via
`subtask/triage-r3-integration` (ff-merge, no push). Highlights:
- **Two snapshot corrections drove the headline finding**: the support log's
  "hera-watch 0 adoption" and "no hera_scratch" were file_id-17 snapshots — the
  full transcript shows 31 `hera-watch` calls and 17 scratch scripts. Both
  fixes **held**; the log captured the session before the agent switched media.
  Lesson for the queue build: reconcile support-log snapshots against the whole
  transcript before scoring a regression.
- **Acceptance ~64 %** — no class graduates (the gate still does design work):
  Zack changed routing on B-1 (doc-near-brief, not template edits), R-1 (omit
  fp-LS335, rig card owns it), R-3 (Aaron softening + burns-to-bottom), P-2
  (remove scratch-notebook reference entirely), T-8 (do the cheap fix now).
- **Recurrences (2)**: `blinded-r2-set` (round-N framing in the very templates
  built to fix the Si=+50 leak) and `landau-fan-cost-nyquist`/burn #2 (ΔB reused
  at n_max=10). Plus two backlog triggers fired (lakeshore two-masters killed
  data/19; hera-watch re-arm tax).
- **Process lessons (for the self-crank)**: (1) the Agent-tool `isolation:
  worktree` subtasks branched off a *re-committed divergent copy* of `hera`
  (`2907907`), forcing a cherry-pick-onto-current-`hera` landing instead of an
  ff-merge — the worktree/launch handling is a chiron fix. (2) "subtask" means
  `/subtask` (Zack-in-the-loop proposal), not an autonomous Agent — the
  hera-watch Agent-tool attempt stalled in a test-rerun loop and was killed;
  re-run as `/subtask` it landed cleanly. (3) One Agent-tool subagent edited a
  CRLF notebook and a measure-template warm-read ballooned the diff via
  `nbformat.write` round-trip — raw-JSON edits preserve formatting.

**2026-06-12 blind dry run** — chiron v0 re-triaged the same session in a
clean room (corpus snapshot at `4162879`, resolution log withheld, no
git; outputs preserved at `$HERA_DATA/triage-dryruns/2026-06-10-QC0426/`,
summarized here).
Strict agreement = recommendation matched the ruling outright; lenient
adds right-disposition-class-wrong-routing (e.g. backlog vs
spawn-subtask, recipe vs prompt surface). The two hard disagreements
(cell-index prompt-anchor; permissions mined-allowlist) both reproduce
the round-1 support-session recommendations that Zack overrode —
Chiron replicates the recommender, not the ruler, which is the
graduation premise observed empirically. 9 queue items had no GT row;
standouts: resolving the log's own model-pin scoring caveat (bare
`claude-fable-5` confirmed from transcript metadata), a transcript-only
find (`nb-collab wait` exit-2 timeout UX), and a self-applied growth
control (its drafts breached the trilayer line budget; it queued the
obligated compression against itself). Blinding verified clean from
both agent transcripts. Misses fed back into `chiron.md` (usage audit,
estimates-vs-actuals roll-up, Examples-setpoint sweep) same-day.

**2026-06-10 baseline** — the `session-notes-resolution` interactive
subtask, scored retrospectively from the resolution table in
`hera/docs/vti/2026-06-10-live-session-log.md`. Rulings that changed
the recommended outcome: 6a (prompt-anchor fix rejected → JL extension
built), 6c + 8a (punted as premature), 11 (support-session lean
overridden → hard bypass), 13b (compressed to a stopping rule), 13f
(modified — setpoints-are-calibration-data exception), 14 (scratch nb
retired — human-originated). ≈⅓ of substantive items modified ⇒ no L2
class is near graduation; this is the bar Chiron's recommendations are
measured against.

**2026-07-18 capstone-2 targeted crank** (`capstone2_archive_triage` +
three fanned subtasks) — 14 resolution rows; archive `6b39599`. Headline:
one tool defect (fs_count_b0 solver limits) root-caused as the driver of
three chained design failures in the run (spot density → side → fan
window) *and* of a triage-side recurrence — the crank's own first draft
proposed two new paper-over clauses (Diffs A/B, withdrawn on Zack's
reversal; burn → chiron memory `23d053b`). Acceptance-unmodified on the
substantive L2 items: **low by design and gladly** — the ruling flipped
the entire fix strategy from add-text to fix-tool+delete-text, the
strongest human-gate outcome since round 1 (⅓-modified baseline).
Corpus net delta: **−12 recipe/brief lines** (deletion sweep + no-side-
prior), +model/analysis tooling via `edbd476` and `2258fb0`..`95d2d75`.
Evaluation-log inputs: `hera-watch` gate-current unpunt **fired (2nd)**;
`sdh_onset` backlog item **fired (3rd)** → rewritten this crank. Session
itself: fully autonomous E0→E1 arc, zero overrides, ABA-strong call —
ruled insufficient as capstone (design-quality, not protocol); the
staged deletions are replay-gated (`replay_verify`) before landing.
