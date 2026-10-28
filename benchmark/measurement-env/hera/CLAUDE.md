# HERA — agent stack for live measurement sessions

`hera/` holds the agents that run a measurement session at a Sharpe Lab
cryostat, the recipe corpus and rig/device cards they work from, the notebook
templates they bootstrap from, and the docs plus post-session triage that
update the corpus. The Python env and launcher GUI live in the rest of
`measurement-env`.

## Agents

| Agent | File | Runs on | Role |
|---|---|---|---|
| **hera-session** | `tools/hera-session.md` (repo root) | rig PC | Session-init: resolves the device card, bootstraps the notebook, preflights JupyterLab, writes the session brief, hands off to tactical. |
| **hera-tactical** | `hera/hera_tactical.md` | rig PC | Drives the session: decides the next measurement, reads every sweep, commits to an arc. The human executes cells. |
| **iris** | `hera/iris.md` | rig PC | Chat-first collaborator with the same tools as tactical, inverted: the human drives, IRIS supports and types cells on request. |
| **chiron** | `hera/chiron.md` | dev machine | Post-session triage (hera-triage): archives the session and works its notes back into the recipe/card/prompt corpus. |

## Layer model

Each fact has one home (full table in [`rig-cards/README.md`](rig-cards/README.md)):

| Layer | Artifact | Carries |
|---|---|---|
| Protocol | agent prompt | how to behave: gates, handshakes, tools, working style |
| Machine | rig card (`rig-cards/<rig>.md`) | the fridge: magnet, thermometry, envelope, equipment |
| Sample | device card (`device-cards/` schema) | what's bonded: wiring, gates, validators, calibrated values |
| Campaign | session brief (`session_template.md`) | the goal, recipes in play, references, blocklist |
| Method | recipes (`recipes/`) | how to measure a thing, rig- and device-agnostic |

The agent prompt is protocol only; machine/sample/campaign facts belong in the
cards and brief, not the prompt.

## Directory map

| Path | Contents |
|---|---|
| `hera_tactical.md`, `iris.md`, `chiron.md` | Agent prompts (installed as Claude Code agents). `hera-session.md` is in the repo's `tools/`. |
| `session_template.md` | Session-brief template; filled in as `hera_session.md` in the measurement dir. |
| `recipes/` | Recipe corpus: `device-init/`, `measurements/`, `investigations/`, `utils/`, and `STYLE.md`. |
| `crops/` | Cell-range snippets cropped from prior session notebooks, as worked examples per recipe. |
| `rig-cards/` | Repo-canonical machine cards (`toploader.md`, `VTI.md`), `EXAMPLE.md` schema, and `README.md`. |
| `device-cards/` | `EXAMPLE.md` schema only; real device cards live in the measurement dir. |
| `templates/` | `base/` holds the generic measure + ana notebooks; per-device dirs (`zf1/`, `QC0426/`, …) hold the device card + reference data, with notebook slots filled from the card at session creation; campaign-kit template dirs (`stacking-campaign/`) hold frozen brief + device-card templates instantiated per device via `hera-mkkit` (see the dir's README). |
| `campaigns/` | SCORER/SUPPORT-SIDE campaign records — prereg protocols, shield instructions, per-device locked artifacts. Never agent-visible; outside any freeze tag. |
| `models/` | Physics forward-models backing `investigations/` recipes (e.g. `aba_trilayer/`). |
| `graders/` | Replay-episode graders, one dir each (`BASE.md` + `<name>/prompt.md` + `<name>/grade.py`): an LLM extractor writes a flat output file, `grade.py` scores it deterministically; the physics (`s1.py`, `sc_arc.py`) sits in the grader's dir. Harness in `src/hera/grading/` (`hera-grade`, `submit_output`; docker only). Design: Obsidian *HERA Grader Plan*. |
| `experiments/frontier/` | Nathan's frontier experiment yamls and round log (`experiments.log`); the fake-rig grader they drove (`src/hera/frontier/`) is under review (Obsidian *HERA Fake Rig - design notes*). |
| `test-cases/` | Replay fixtures for the offline measurement-suggestion benchmark; see `test-cases/README.md`. |
| `vti/` | VTI-rig assets (Cernox calibration curves). |
| `nb-collab/` | Design/plan docs for the `nb-collab` tool. |
| `docs/` | `notebook-indexes/`, session `notes/`, `papers/`, `vti/`, `iris/`, and design docs (`extending-the-corpus.md`, `triage-workflow.md`, `session-archiving.md`, `benchmark-plan.md`, `eng-backlog.md`, …). |
| `docker/` | The replay image: `build.sh <harness_sha> [--corpus <sha>] [--corpus-prompt] [condition]` builds `hera-agent:<sha7>-<condition>` from a whitelist-filtered `git archive` of one commit (never the working tree), plus the container's clock shims. `--corpus` overlays `recipes/`, `crops/` and `models/` from a second commit — modern harness, older corpus — tagged `hera-agent:<harness7>.c<corpus7>-<condition>`, with `p` after the corpus sha when `--corpus-prompt` takes the agent prompts from it too. Not agent-visible. |
| `replay/cases/` | `hera-replay run` case files (the episode's origin — source archive + cut uuid, a pre-cut bundle, or a hand-built `session` dir and its `ts` — then the start, `resume` or `fresh` with its brief under `cases/briefs/<frontier>/`, corpus sha + condition, model/effort/N/guards; `runner: codex` runs the OpenAI Codex CLI instead of `claude -p`, per `docs/replay-codex-path.md`). A corpus overlay names the code the corpus runs on in the `corpus` block as `harness: <sha>`, alongside `prompt: harness\|corpus` for which of the two shas the agent prompts come from, and `reads: archived\|corpus` for whether the resumed transcript's own pre-cut reads of recipes, crops and models show the text the session got or the corpus sha's (`hera-replay cut --case <yaml>` makes that cut and logs every substituted and unrewritten read). Runs land in `$HERA_DATA/replay/runs/`. `hera-replay submit` / `wait` / `status` / `cancel` / `reap` run jobs of many cells and grade items on host-wide slot pools, and `cell` pools a case's run dirs (`docs/replay-parallel-runs.md`). |

## Data (`$HERA_DATA`)

Bulky binary artifacts — test-case fixture data (`data/`, `images/`, `runs/`,
`*.ipynb`) and replay/triage run outputs — live outside git at `$HERA_DATA`
(default `/data/sharpelab/hera-data`, a snapshotted btrfs subvol). Fixtures
track only their authored text (`frontiers/`, `ground_truth/`, `*.md`) in git;
`test-cases/link-data.sh` relocates the binary layer there and symlinks it
back.

## Recipes

A recipe describes how to measure something, kept rig- and device-agnostic:
instrument-class conditionals, not rig constants or device numbers; the cards
and brief resolve them. `STYLE.md` is the guide for writing them (validity
domains, provenance flags, evidence-strength vocabulary, burn log) — read it
before editing a recipe. Rig **variants** (`<base>-<rig>.md`) name their base,
list only their deltas and the rig fact forcing each, and state their
obsolescence condition.

Adding a new recipe, investigation, or backing model — and the lit-search /
campaign-readiness workflow that grounds them — is mapped in
[`docs/extending-the-corpus.md`](docs/extending-the-corpus.md), which routes
through the two worked examples (the tMoTe₂ readiness pass and the ABA/ABC
trilayer investigation bundle).

## Corpus Style

The recipes, cards, prompts, and docs here are terse instruments read by
agents under token pressure. New files and edits both follow it:

- Terse. Make the point and stop — no padding with justification,
  cross-references, or "while I'm here" context.
- Don't restate what you point to. A doc that defers to another surface
  (rig card, prompt, another recipe) points at it; it does not re-explain it.
- Snapshots, not diffs. Artifacts record the current state, never the path
  to it — no "no longer X" / "now uses Y", no correction residue, no
  prior-state framing. History lives in git and the session logs; a
  transition that matters gets its own dated record, not residue inline.

## Editing the corpus

Follow the Corpus Style above, and:

- Prefer deleting to adding.
- Don't paper over a tool defect: text that routes around one is a loan —
  name the fix that retires it, and delete the text when the fix lands.
- Don't edit a completed record (a spent brief, a past session log) to fix a
  forward problem — fix the forward surface (template, rig env).
- After you make a change, re-read the diff against this section for
  compliance before you propose it. Propose — show the diff, don't self-land.

## Cards

- **Rig card** — repo-canonical at `rig-cards/<rig>.md`; deployed as a copy
  named `rig_card.md` in the measurement dir. Fixes flow back through triage,
  not in-session edits.
- **Device card** — canonical in the deployed copy, which mutates per cooldown;
  `device-cards/EXAMPLE.md` is schema only.

## A session

```
hera-session ──► writes hera_session.md + deploys rig_card.md, resolves
     │            device_card.md, bootstraps the notebook, preflights JupyterLab
     ▼
hera-tactical (or iris) ──► runs against the live notebook; reads recipes by
     │                       absolute path from ~/measurement_env/hera/recipes/;
     │                       lands cells via nb-collab; writes session_notes.md
     ▼
hera-archive ──► snapshots artifacts + transcripts into
     │            hera/docs/notes/<date>-<device>-session/
     ▼
chiron ──► works the notes into recipe/card/prompt amendments
```

Agents are read-only on the repo during a session; changes flow back only
through Chiron.

## Replay-variance experiments

Frozen-frontier replay studies (corpus-version ladders, matched
single-lesson ablations, de-anchored frontiers) run through
`hera-variance` and the quota-aware `hera-experiments` scheduler with a
headless `claude -p` harness. Manifests and analyses: `hera/experiments/`;
design and scoring conventions: `docs/replay-variance.md`.

## Install

`scripts/install.sh` (idempotent; re-run after every `git pull`) symlinks the
`tools/` shims into `~/.local/bin/` and the agent prompts into
`~/.claude/agents/`, and retires agent names superseded by renames. On rig PCs
(Git Bash) `ln -s` falls back to a copy, so deployed prompts and shims drift
until `install.sh` is re-run.
