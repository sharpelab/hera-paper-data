# Chiron memory

Triage-process notes for the post-session self-improvement loop. **Scope rule
(same as every agent-visible surface):** never write anything here that would
mis-steer a rig agent if this file leaked into a rig context — these are
dev-machine / triage-process notes only, no operating setpoints, no campaign
frame.

## Queue-build

- **Reconcile support-log snapshots against the WHOLE transcript before scoring
  a regression.** Support-session logs are often written *mid-session* — they
  are a snapshot at some file_id, not the final state. R3's two headline
  "regressions" were both snapshot artifacts: "hera-watch 0 adoption" (actually
  31 calls) and "no `hera_scratch`" (actually 17 scripts) — the agent switched
  media *after* the log's snapshot. Mine tool-usage counts and adoption from the
  full transcript, then diff against the support log; a support-log claim of
  non-adoption/regression is a hypothesis to verify, not a finding.
- The estimates-vs-actuals roll-up and changelog audit catch what no single note
  carries (R3: estimate-discipline held with no optimism bias; burn #2 partially
  refired on a ΔB the agent reused without re-checking Nyquist at higher n_max).

## Delegation — delegate by default; route by the border

- **Delegate by default.** Keep your context on orchestration (queue, routing,
  review, landing), not on typing every diff — serializing the work out of the
  thread keeps you focused and parallelizes the crank (Zack's R3 steer: the
  fanning was good; even the 1–2 inline changes I did could've been agents).
- **The border** (who types the diff):
  - **Agent + post-review** when the *what* is decided and correctness is
    **locally verifiable** (diff + passing test), contained, no protocol
    coupling — most tooling fixes and post-ruling corpus edits. R3's nbtools /
    archive / anakit chunks worked well this way. Fan out.
  - **`/subtask`** when there's **design ambiguity** (several viable approaches,
    choosing is the work), **protocol coupling** (reshapes agent behavior every
    session inherits), expensive review, or high blast radius — Zack in the
    proposal loop. hera-watch's long-run redesign was the case; Zack knew up
    front it needed him. (One Agent-tool attempt at it stalled in a
    `pkill`/test-rerun loop and was killed; `/subtask` landed it cleanly.)
  - **inline** only for the trivial or tightly-coupled-to-an-edit-in-hand.
- **Landing tax (minor, usually absent):** Agent-tool `isolation: worktree`
  subagents can branch off a re-committed *divergent* copy of `hera`, costing a
  cherry-pick to land instead of an ff-merge. Negligible for small disjoint
  diffs; it only showed up in R3 because Zack was advancing `hera` in parallel.
  Don't let it push you off agents. Read-only subagents (mining, audits) never
  commit, so they never pay it.

## Landing mechanics

- **`hera` moves during a session.** It advanced several times in R3 (other
  subtasks landing). Always re-check `hera`'s tip and rebase the integration
  branch onto it immediately before the ff-merge, or it won't be a fast-forward.
- **Edit only inside the worktree.** Early in R3 I edited the main checkout
  (which sits on `hera`) by reflex; had to migrate the diffs into the worktree.
  Resolve every edit path under `.worktrees/<name>/...`.
- A clean landing of N divergent branches = cut an integration branch off
  current `hera`, cherry-pick each branch's range, resolve (conflicts cluster on
  append-only docs + same-rule STYLE edits + test import lists), run tests
  against the **worktree** src (`PYTHONPATH=$PWD/src`, since `menv` pins the main
  project dir), then ff-merge.

## Drafting conventions that survived review

- **Burns go at the BOTTOM of STYLE**; rules stay tight with a `(burn log #N)`
  pointer inline. Don't inline the war-story (Zack corrected this in R3).
- **Soften strength claims an expert would bend.** A correctness floor stated as
  an absolute ("corrupts every point, never") is too strong; "derive-by-default,
  bend knowingly (clean signal), what's not OK is the *unexamined* shortcut" is
  the calibrated form (Aaron, on the τ-settling rule).
- **Variants don't restate card hazards** (STYLE rule 13). The landau-fan-vti
  delta omits "don't fp the LS335" because the rig card already owns the
  two-masters warning — Zack's ruling.
- **Recipe Examples for a blinded device stay device-name- and round-free.**
  QC0426 is a blinded campaign; a recipe Example naming it by round would leak
  next time. Cite by file_id / "a VTI trilayer fan", provenance-tagged.
- **Notebook edits: use raw-JSON splices, not `nbformat.write`.** `nbformat.write`
  re-serializes the whole file (704-line diff for a 3-line change), and CRLF
  notebooks (Windows-edited, e.g. toploader templates) balloon further. A raw
  text/JSON splice preserving the file's existing line endings keeps the diff
  minimal.

## Ruling patterns to pre-empt (Zack)

- **Blinding leaks → a doc near the example brief**, not piecemeal template
  edits (R3 B-1: `hera/blinding.md`).
- **Cheap fix now, expensive one backlogged** — and the cheap fix still gets
  per-instrument consideration (T-8: warm the τ cache, but only the lock-in
  τ/slope, because reads aren't free on every instrument).
- **Scope template edits to where the burn happened** (skip the toploader
  template when the burn is VTI).
- The gate still does design work: R3 acceptance ~64 %, no class graduated.
  Don't push for L2→L1 graduation early.

## Paper-over reflex (burned 2026-07-17/18, QC0426 capstone-2 triage)

A tool defect (`fs_count_b0` grid edge, |n| ≈ 3.5e12 + e-only) had been quoted
as "validity" onto three agent-visible surfaces across prior cranks (brief
arc-reader line, landau-fan lever 2, investigation Verify); the capstone agent
clamped a hole-side fan to it — half the reachable window, on the side where
the overlay couldn't run — and the first triage draft proposed *adding two
more clauses*. Zack reversed to: fix the tool, delete every quote. Standing
check for every queue item: **before drafting any corpus text that mentions a
tool's limitation, route to the tool fix instead** (CLAUDE.md
tooling-beats-process); if the fix can't land this crank, the interim is the
tool failing loudly (raise/NaN), not prose. Deletion sweep is part of the
fix's landing: grep the corpus for every quote of the defect (briefs +
templates included — kit regeneration re-ships old quotes at full salience).

## Replay verification methodology (capstone-2 crank, 2026-07-18)

- **Burn-reproduction controls run the PRODUCTION model.** The capstone density
  burn was fable-5-modal and opus-invisible: text defects amplify with
  instruction-following quality — the stronger model burns *because* it takes
  the corpus seriously. An opus-only screen would have called the control arm
  clean and the pass vacuous.
- **Serve the brief on decision frontiers** (`--brief`): the load-bearing steer
  can live in the brief, not the recipes (the density clamp did).
- **Fixture cards must be at-cut.** An archived post-session device card is an
  answer key (the Luttinger-pin leak tainted the onset acceptance runs). Add
  leak-term tripwires when authoring fixtures.
- A discriminating pass needs the control to reproduce the burn first; a soft
  frontier makes any pass vacuous (cf. the 21/21 lever-sweep).

## Round lessons — gists (detail: [rounds.md](rounds.md))

**R4 (2026-06-16):**
- Terse, no editorializing; a tool fix that covers a gap means NO added prompt
  text; propose-then-wait on L2/L3.
- Spawn /subtasks at the START of triage (parallel with queue work).
- Recipe-science → Aaron by default; drafts to `hera/docs/aaron-handoff.md`.
- Notebook edits: surgical raw-JSON splices; `nb grep`, never NotebookEdit or
  hand-rolled json.load searches.
- Templates can be stale round-1 framing — rebase on the latest scrubbed card.
- Chiron-spawned subtasks branch off the TRIAGE branch and land back to it,
  never `hera`/`master` — override `subtask-launch` defaults (base + land target).
- Operator log may be on the wiki, not the repo — check before scoring "absent".
- Editorializing is structural: delegated agents don't inherit the Corpus Style
  rule — put it in every brief/prompt you hand out.

**tl_crank (zf1 2026-06-24):**
- "Filter your list of X" can mean filter X OUT — confirm keep-vs-drop.
- `newclaude` transcript loss ×2; the backup hook fails SILENTLY — verify a
  transcript exists before mining plans assume it; fall back to durable artifacts.
- Toploader has TWO measure templates — deploy source is `hera/templates/base/`;
  repo-root copy is the launcher's. Target the base.
- Tell subtasks to commit-and-STOP (no self-ff of the triage branch); base each
  on the current crank tip, fold in launch order.
