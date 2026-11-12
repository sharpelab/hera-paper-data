# Triage workflow — the HERA self-improvement loop

Design contract for **Chiron** (`hera/chiron.md`, AKA hera-triage): the
standing post-session agent that closes the feedback loop. HERA measures
autonomously; Chiron makes the stack *improve* autonomously from each
session. This doc owns the contract — trigger, inputs, dispositions, the
autonomy ladder and its graduation rules, growth controls, and
self-measurement. `chiron.md` is the operating procedure; where they
disagree, this doc wins.

Provenance: the loop was proved manually on the 2026-06-10 VTI session —
tagged mid-session notes → interactive triage (`session-notes-resolution`
subtask, 2026-06-11) → ~20 commits in 48 h. The resolution table at the
end of `hera/docs/vti/2026-06-10-live-session-log.md` is the reference
work product, and round 1's review data is the autonomy baseline.

## Trigger

Event-shaped, not scheduled: a session ends → the human launches Chiron
(`chiron --rig vti <user>/<session-dir> [date]`). Chiron invokes
`hera-archive` itself as step 0 — the archive tool is idempotent and
Chiron is the driving agent, not a hook target. No cron, no wakeups;
sessions are discrete events days apart.

A second invocation form, `chiron cleanup`, runs the periodic
consolidation pass (§growth controls).

## Inputs

- The session archive (`hera/docs/notes/<date>-<device>-session/`):
  `session_notes.md`, notebooks, `hera_scratch/`, agent transcripts.
- The support-session log (`hera/docs/vti/<date>-*-session-log.md` or
  toploader equivalent).
- The operator-side wiki note doc (Outline "session notes" collection) —
  ZG/AS live observer notes; a doc may span multiple sessions.
- The corpus it amends: `hera/recipes/` + `STYLE.md`, agent prompts
  (`hera_tactical.md`, `iris.md`), rig cards, templates, device cards,
  runbooks, `hera/docs/eng-backlog.md`, committed agent-memory.
- Prior resolution tables + `triage-scoreboard.md` (history; settled
  items are not re-litigated).

## Dispositions

Unchanged from the interactive prototype:

| Disposition | Meaning |
|---|---|
| apply | concrete diff, committed |
| defer-to-backlog | written `eng-backlog.md` entry |
| spawn-or-continue-subtask | work too big for triage; subtask owns it |
| punt-unresolved | with an explicit re-evaluation trigger |
| record-only | logged, no artifact change |
| drop | with rationale |

Every item carries citations (session/date, cell idx or file_id,
transcript line, run id). The resolution table (`# | Item | Ruling |
Change / commit`) is appended to the session log; rig-side writes go to
an ordered maintenance-window checklist in the same log, never applied
by the agent.

## Autonomy ladder

The design principle, from round-1 data: the human's ruling changed the
outcome on ~⅓ of items (resolution rows 6a, 6c, 8a, 11, 13b, 13f, 14) —
the gate does design work. So autonomy goes where the human adds nothing
(preparation, evidence, drafting, bookkeeping, metrics — ~90 % of the
wall-clock) and landing rights are earned per class, with data.

| Level | May land without per-item ruling | Classes |
|---|---|---|
| **L0** | n/a (always autonomous) | queue build, transcript mining, evidence, draft diffs on the branch, resolution-table + scoreboard bookkeeping |
| **L1** | yes (flagged in review summary, revertable) | append-only low-risk docs: burn-log *entries*, eng-backlog entries, record-only notes, resolution-table rows, scoreboard |
| **L2** | no — propose-only, human rules per item | recipe content, STYLE rules, agent-prompt amendments, tooling code, runbooks, templates |
| **L3** | never (structural) | blinded-campaign templates/cards, rig-side writes, measure-notebook semantics, safety surfaces (validators, SAFETIES, field/temp limits) |

A burn-log entry (L1) and the rule fix it motivates (L2) are separate
commits — the record lands even if the fix is rejected.

L3 is structural, not graduatable: blinding integrity and safety
surfaces stay human-gated regardless of track record, and the recipes
are lab-shared — Aaron's people read them as humans, so recipe-content
graduation (L2→L1) additionally requires Aaron's buy-in, not just a
good scoreboard.

### Graduation

A class moves L2 → L1 when its **accepted-unmodified rate** (Zack's
ruling == Chiron's recommendation, diff landed as drafted) clears
**~90 % over 2–3 consecutive sessions**, per the scoreboard. Zack rules
on the graduation itself; the scoreboard is the evidence, not the
trigger. Demotion is symmetric: a landed-then-reverted L1 change, or a
class whose acceptance rate drops, goes back to L2.

Round-1 baseline (interactive prototype, 16 rows): ~60–70 % accepted
unmodified — i.e., no class graduates on day one, which is the point.

## Inclusion thresholds

What evidence earns what artifact:

- **One fully-cited burn** (a rule misled a live agent; session/cell/run
  cited) → burn-log entry + a fix to the specific rule. Burns 1–3 are
  all single-incident; burns are expensive, one is enough.
- **Hypothesis-grade observation** (a lean, an anomaly, no burn) →
  record-only or eng-backlog. Never recipe text.
- **Behavioral norms** (working-style bullets in agent prompts) require
  recurrence across sessions or a measurement — precedent: the
  idle-time-pricing norm, punted 2026-06-11 as "right direction, too
  strong for now" pending `hera-utilization` data.
- **Tool candidates** need the hand-rolled-twice test (an operation the
  agent improvised ≥2 times in transcripts) before a build is proposed.

## Ruling principles

Disposition heuristics — they calibrate *where an item goes and when*, the
way STYLE's burn log calibrates recipes. A principle earns its place here
only if it guides routing and isn't already captured as a concrete artifact
rule (the same anti-accretion bar as the corpus it triages).

**Tooling beats process.** When friction can be fixed by a tool/affordance
instead of prompt text, prefer the tool even at higher build cost — it
costs the agent zero tokens and zero cognitive load, and it can't be
misread or forgotten. Prompt text is the fallback, not the default. Build
the pit of success. Two riders (ruled 2026-07-16 — doc fixes land same-day
while code fixes backlog, so paper-overs accrete by default):
- **Promote, don't backlog**: a tool defect that is generating corpus text
  is priced by the text's standing per-session cost, not the build cost.
- **The fix deletes the text**: paper-over text names the tool fix that
  retires it, and that fix's definition of done includes the deletion
  (read-path: `9442cb5`→`e77941f`, one crank; backtick guard: `fd3fcd4`,
  note outlived it three weeks to `a23b3fd`).

**Route by generality, gate by recurrence.** Whether a lesson exists is
gated by evidence — one cited burn is enough. Where it lives is set by how
general the failure mode is, not how often it fires: a lesson that doesn't
name the method is epistemics and goes to STYLE; a method-specific one goes
to the recipe. A single incident can still earn a STYLE rule.

**Front-load the cheap, perishable, iterable.** When something is cheap to
stand up, captures something you'd otherwise lose, and can be refined
later, build it now rather than backlog it. Timing you don't record this
session is gone forever.

## Growth controls — the corpus must not accrete

- **Dedup-before-add** (every run): an addition first checks whether an
  existing rule/caveat/backlog item covers it; cite or strengthen in
  place instead of duplicating.
- **Size budgets**: any single recipe or `STYLE.md` crossing **~250
  lines** obligates a compression proposal in the same run that grew it.
  (Reference points, 2026-06: largest recipe 286 lines —
  `trilayer-stacking-id` is already over; STYLE 192.)
- **Net-line accounting**: every commit reports its net line delta; the
  scoreboard tracks the corpus trend per session.
- **Cleanup mode** (`chiron cleanup`, every ~3–4 sessions or on a rising
  scoreboard trend): a separate invocation whose deliverable is
  **removals and merges only** — overlapping caveats merged, rules
  deduped, over-budget files compressed, never-fired amendments proposed
  for sunset. Separated from per-session triage deliberately: an agent
  graded on landing fixes has the wrong incentive to prune the same day.
- **Sunset (deferred-honest)**: "this amendment never fired again" needs
  rule-fired telemetry that doesn't exist. Until it does, cleanup mode
  uses a proxy — grep session transcripts/notes for rule citations — and
  sunset proposals are L2 regardless. Real telemetry is a future
  instrumentation item, not something to fake.

## Self-measurement

`hera/docs/triage-scoreboard.md`, one row per session, updated by Chiron
at the end of each run:

- **Loop latency** — note timestamp → landed commit, median + max
  (derivable from session-notes timestamps vs git dates).
- **Acceptance-unmodified rate, per class** — the graduation metric.
- **Recurrence count** — landed fixes whose `watch` was violated this
  session (a superset of burn-logged classes refiring; the loop's true
  effectiveness metric; target is zero). The per-fix ledger is
  `hera/docs/triage-changelog.md` (changelog + evaluation log) — Chiron
  audits it at step 1 and appends at step 7.
- **Corpus net delta** — lines added − removed across recipes, STYLE,
  prompts.
- **Queue coverage** — items found vs items the human later surfaced
  that Chiron missed (misses are Chiron's own burn log).

## Standing audits

Each run, beyond the queue:

- **Scope hygiene** over agent-visible surfaces (committed agent-memory,
  cards, templates, briefs, recipe Examples): dev-machine notes that
  would steer a rig agent (the 2026-06-10 `--no-project` leak), and
  inherited operational defaults (STYLE rule 11; the Si=+50 burn).
- **Recurrence check** against the STYLE burn log.

## Validation — the blind dry run

Before v0 is called done: run Chiron against the 2026-06-10 QC0426
archive with the resolution log withheld, and score against the real
table — queue coverage (all 16+ rows, plus the transcript-only finds),
disposition agreement, diff quality vs what landed. That run seeds the
scoreboard's calibration baseline and its misses feed back into
`chiron.md` — the loop applied to itself.
