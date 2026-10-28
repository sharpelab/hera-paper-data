# Round-lesson detail (gists in MEMORY.md)

## Round 4 (2026-06-16) — Zack steered hard on these

- **Terse, no editorializing.** Corpus edits state the rule/fact in minimum
  words — no reason-padding clauses, no "because/this is important". Zack
  corrected ~5× this round (re-entry clause, the step parenthetical, a
  redundant "brief wins" line, a bad Si-sign physics claim + duplication in the
  device card, a rig-card timing line). When a tool fix already covers a gap,
  do NOT add prompt text (P-1 kernel probe was dropped — tool fix `2cd0442`
  already covered it). Propose, then wait — don't direct-edit L2/L3 surfaces.
- **Spawn /subtasks at the START of triage.** Subtasks are chiron's to spawn
  (Zack never spawns them); do it first so they run in parallel with the queue
  work instead of serially at the end. The watch-mode cluster is the proven
  /subtask case (autonomous-Agent attempt stalled in R3).
- **Recipe-science → Aaron by default.** Don't draft recipe/investigation/
  model/STYLE-physics edits — Aaron does a science pass on those. Record them
  in `hera/docs/aaron-handoff.md` (drafted text preserved) and defer. Chiron
  owns prompt / cards / tooling / bookkeeping. (Pulled 4 recipe edits this
  round.)
- **NotebookEdit balloons ipynb diffs** — it re-encodes unicode (em-dashes →
  literal) across every cell via the nbformat round-trip. For a one-line
  notebook change, do a surgical raw-JSON string edit: `nb grep` to find the
  line, replace the exact JSON string (keep `\n` escapes), `json.load` to
  validate. Confirms the R3 round-trip lesson.
- **Use `nb`, don't hand-roll** — `nb grep <ipynb> <regex>` gives cell + line
  numbers; don't `json.load` a notebook to search it (chiron's own A-1
  anti-pattern).
- **Device/measure templates were stale** (round-1 framing) — rebased the
  device card on the blinding-scrubbed R3 card. The measure template is also
  stale (Si `[0,+100]`, Qingrui/run-79 framing); flagged, not rebased — same
  R3-rebase decision likely applies.
- **Chiron-spawned subtasks branch off the triage branch and land back to it
  — never `hera`/`master`.** Holds for ALL chiron subtasks, including deferred
  follow-ups (R5 wrongly branched its 4 off `hera` as "separate work" — Zack:
  branch off the triage branch, land here, so the whole crank lands as one
  reviewed unit). Concretely: base the subtask worktree on the triage-branch
  tip, set its land target to the triage branch (ff-merge back, no push), and
  do NOT ff-merge the triage branch to `hera` until the subtasks are folded in.
  `subtask-launch`'s default (`--repo` main, base HEAD, land→master+push) does
  the wrong thing — override the base and land target.
- **Operator log may be on the wiki, not the repo.** R5 had no committed
  support log; chiron declared the stream absent. Aaron kept it on the wiki
  (`outline.py get <id>`). Before scoring "no support log," check the wiki — it
  carries qualitative observations the transcript doesn't (recipe-adherence
  annoyance, design asks).
- **Editorializing is structural, not willpower.** R5 recurred it (restated a
  hazard, a backlog cross-ref in a card, edited a completed brief) — Zack halted
  the run. Fixed by landing Corpus Style + Editing into `hera/CLAUDE.md` + a
  `chiron.md` rule. **Delegated agents don't inherit it**: the first nb-collab
  agent (spawned before the rule) editorialized two doc files. Always put the
  Corpus Style rule in the brief/prompt you hand a subtask or Agent.

## tl_crank (zf1 2026-06-24)

- **"Filter your list of X issues" can mean filter X OUT.** Zack said "filter your
  list of hera-session/session-init issues" — I produced a hera-session-only list;
  he meant *drop* hera-session and work the actual measurement session. When an
  instruction names a category to "filter," confirm direction (keep vs drop)
  before spending a pass on it. My one coverage burn this round.
- **`newclaude` transcript loss is now 2nd-consecutive, and the backup hook fails
  SILENTLY.** The tactical marathon ran as a `newclaude`-spawned session whose
  jsonl was never persisted; the `hera-transcript-hook` is registered + launched
  with `HERA_SESSION_DIR` set correctly, yet wrote nothing (fails below the env
  gate — likely `command -v uv` PATH, swallowed exit 0). Don't trust hook-exists =
  hook-works. Mine the marathon from durable artifacts (session_notes + both
  notebooks + `hera_scratch/*` + `data/<n>` mtimes) + the init transcript.
- **Toploader has TWO measure templates.** Deploy source = `hera/templates/base/
  toploader_measure.ipynb` (hera-session fills + ships this); repo-root
  `templates/toploader_measure.ipynb` = the launcher copy. A fix landed in the
  wrong one never reaches a session (the thermo-staleness guard regression). Target
  the base template; flag the launcher-copy divergence.
- **Tell subtasks to commit-and-STOP, never ff the triage branch.** One subtask
  ff'd `subtask/tl_crank` itself (clean only because linear). The crank folds via
  cherry-pick; a subtask self-ff can desync the crank worktree. Base each subtask
  on the *current* crank tip so its file already carries prior folds (no conflict),
  and fold in launch order.
