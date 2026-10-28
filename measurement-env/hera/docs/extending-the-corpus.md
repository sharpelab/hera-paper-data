# Extending the HERA corpus — recipes, investigations, tools, and lit search

*For contributors (and their agents) adding to the HERA corpus: new
measurement/investigation recipes, the forward-model tools that back them, and
the literature work that grounds both. This is a **map and a pointer list**, not
a tutorial — it routes you to the two worked examples already in the tree and
names the one law you must read first.*

**Read first:** [`hera/recipes/STYLE.md`](../recipes/STYLE.md) — the epistemics
guide for agent-executed science. Every rule below (provenance flags, strength
vocabulary, confounds-next-to-the-rule, rig/device-agnosticism, burn log) comes
from there. A recipe that violates STYLE will mis-calibrate a live agent; treat
it as the spec, not a style preference. Orientation for the whole stack is
[`hera/CLAUDE.md`](../CLAUDE.md) (agents, the layer model, directory map).

---

## The shape of the work

Two stages, front-end then build. You will most likely start at the front end.

1. **Campaign readiness (gap analysis)** — take a target paper or an incoming
   sample, work out the campaign it implies, audit the corpus against it, and
   emit a prioritized *build list*: which recipes, investigations, tools, and
   replay fixtures are missing. **This is where Nate + Aaron are likely to be
   working.** Worked example below (tMoTe₂, arXiv 2504.06972).

2. **Build the missing pieces.** The richest unit is an **investigation
   bundle**: a lit-search-grounded decision procedure plus the forward-model
   tool that makes its reads falsifiable. The completed worked example is the
   ABA/ABC trilayer stacking-ID bundle below — the prep to learn from and build
   on.

A built recipe then gets exercised in a live session; what the session teaches
flows back into the corpus through triage (Chiron), not in-session edits — see
[`triage-workflow.md`](triage-workflow.md) and the burn log in `STYLE.md`.

---

## Stage 1 — Campaign readiness (the likely starting point)

**Worked example: arXiv 2504.06972** (Xu et al., tMoTe₂ FQAH + unconventional
SC). A paper-like sample was expected on the toploader ~1 month out, and the
question was whether the corpus could advise that campaign. Two docs, read in
this order:

- **The report (governing doc)** —
  [`campaign-readiness-2504.06972.md`](campaign-readiness-2504.06972.md). The
  template for a readiness pass: the campaign's decision chain, recipe/fixture
  **coverage tables**, the **gap list**, a prioritized ~1-month build plan, and
  a **lab-input checklist** (what only Aaron can answer). Assessment only — no
  recipes built in the report itself.
- **The workstream resume doc** —
  [`campaign-readiness-2504.06972-workstream.md`](campaign-readiness-2504.06972-workstream.md).
  State at pause: what's landed, the next steps in priority order, the **seed
  data** found (`tmote2/td48` — the only moiré-TMD campaign in the corpus,
  indexed at
  [`notebook-index-tmote2.md`](notebook-indexes/notebook-index-tmote2.md)), and
  the process notes for resuming (subagent pattern, landing flow, recipe-format
  contract). **Resume from here** by forking a fresh subtask off `hera`.

What a readiness pass produces, concretely: coverage tables (which existing
recipes/fixtures cover which campaign phases), a gap list (e.g. "the
discriminating measurements — Landau fan, T-dependence, bias spectroscopy — are
exactly the deferred recipes; `cap-ratio-calibration` is referenced by three
recipes but doesn't exist as a file"), and a checklist of decisions that need
the PI. The corpus units it points at — new measurement recipes, a units layer,
new fixtures, perception-layer classes — are then built in stage 2.

---

## Stage 2 — The ABA/ABC trilayer investigation (the worked bundle)

The one complete investigation in the corpus, and the reference for building a
new one. It classifies trilayer-graphene stacking (ABA vs ABC) from
magnetotransport. Built from a technique paper, backed by a from-first-principles
forward model, written under STYLE, and hardened by a live VTI campaign (QC0426,
June 2026). The three legs plus the campaign that tested it:

### Leg 1 — the lit-search ingestion

| Artifact | What it is |
|---|---|
| [`docs/papers/ncomms14518/paper.md`](papers/ncomms14518/paper.md) | The **ingested technique paper** (Datta et al. 2017). The format to copy: benchmark device/conditions, fitted band parameters, **discriminators split by evidence axis**, a **resolution ladder** (what limits what), a figure guide, and a "how to use this paper" summary contract. ABC-side claims are flagged as citation-network, not this paper's data (STYLE rule 5). |
| `docs/papers/ncomms14518/fig1–5.png` | Figure crops rendered from the PDF for in-session viewing — cite panels from here, don't re-open the PDF mid-session. |
| [`docs/vti/refs/`](vti/refs/) | Source PDF (`ncomms14518.pdf`), the paper's reference fan, and the annotated QC0426 fan PNGs the model overlay digitizes. |

This is the lit-search deliverable: not a summary, but a **measurement-grounded
reference** an agent cites by panel and scales to its own device.

### Leg 2 — the forward-model tool

[`docs/vti/aba-trilayer-qc0426/`](vti/aba-trilayer-qc0426/) — the tool that makes the
recipe's reads falsifiable (a data-driven detector alone re-traced straight rays
as "chains"; the model template is what makes the arc search well-posed).

| File | What it does |
|---|---|
| `ll_spectrum.py` | 6-site SWMcC LL Hamiltonian with the paper's fitted parameters; `selftest()` validates the 2 meV / 14 meV band splittings — the **validation gate**. |
| `crossing_model.py` | Predicted ML×BL crossing loci / DOS on the (n,B) plane. |
| `compare_qc0426.py` | Worked overlay on real data (run-80 Rxx(n,B)), single global density rescale. |
| `validate.py` | Reproduces the paper's Fig 2b/3a from first principles. |
| [`README.md`](vti/aba-trilayer-qc0426/README.md) | What was built, how it was validated, the QC0426 comparison and verdict. |
| [`FUTURE_WORK.md`](vti/aba-trilayer-qc0426/FUTURE_WORK.md) | **Read this for how a tool earns its keep**: a prioritized roadmap written after the model's first live deployment, each item tied to a concrete session pain point. The model's highest-value acts were *rejections* — a forward model that places falsifiable loci lets a wrong candidate be argued down. |

Pattern to copy: build the spectrum the paper computed → gate it on the paper's
own published numbers → overlay on your data with a *single* global scale
(a per-feature fit is not a test) → write down what it can and can't resolve.

### Leg 3 — the recipe

[`recipes/investigations/trilayer-stacking-id.md`](../recipes/investigations/trilayer-stacking-id.md)
— a decision procedure spanning multiple measurements (it orchestrates
`measurements/gatemap.md` and `landau-fan.md`), not a single sweep. Note how it
embodies STYLE: discriminators carry their confounds inline, evidence is split
presence/pattern/magnitude, absence claims cite resolvability, and it ends with a
mandatory **output contract** (per-region verdict on the strength scale, evidence
list with coordinates + paper panels, hedges, what-would-firm-it) where a
reasoned "cannot tell" is a success and a confident unevidenced call is a
protocol violation.

### The campaign that produced and tested it

The recipe's burn log entries are real — they came from this campaign:

- Session briefs, live-session log, preflight, and the **retrospective** —
  [`docs/vti/`](vti/) (`qc0426-*-session-brief.md`, `2026-06-10-live-session-log.md`,
  `qc0426-hera-retrospective-2026-06.md`).
- Session archive + transcripts —
  [`docs/notes/2026-06-10-QC0426-session/`](notes/2026-06-10-QC0426-session/).
- Notebook index —
  [`notebook-index-QC0426-3LGr.md`](notebook-indexes/notebook-index-QC0426-3LGr.md).
- Replay fixture distilled from the campaign —
  [`test-cases/2026-06-01-QC0426-fan-mapping/`](../test-cases/2026-06-01-QC0426-fan-mapping/)
  (fixture-authoring spec: [`test-cases/README.md`](../test-cases/README.md)).

---

## Anatomy — building a new investigation bundle

The ABA/ABC bundle, distilled into the process that made it:

1. **Lit search → ingest the technique paper** into `docs/papers/<id>/paper.md`
   in the format above (benchmarks, parameters, axis-split discriminators,
   resolution ladder, figure crops, usage contract). Flag every claim's
   provenance (STYLE rule 5).
2. **Build + validate a forward-model tool** in `models/<name>/` if the reads
   need a model to be well-posed. Gate it on the paper's published numbers
   before trusting it on data; one worked overlay; a `FUTURE_WORK.md` written
   from real use.
3. **Write the recipe** in `recipes/investigations/` using the house skeleton
   (`What / When / Why / Recipe / Verify / Examples / Next`), rig- and
   device-agnostic (STYLE rule 11 — instrument-class conditionals, never rig
   constants or device numbers; those live in the rig/device cards and brief).
   End with the output contract (rule 9).
4. **Exercise it live**, then **fold the burns back** through triage — fixes to
   recipes/cards/prompts flow through Chiron, not in-session edits.

Measurement recipes (single modalities) are the same minus the paper/model
legs; see `recipes/measurements/` for the form.

---

## Mechanics (from the workstream process notes)

- **Branch is `hera`, not `master`** (master is abandoned). Subtask flow:
  commit on `subtask/<slug>` → `git rebase hera` → `git -C ../.. merge
  --ff-only`. **Agents never push** — Zack pushes manually.
- **Subagent pattern**: indexing → opus/sonnet agent; recipe drafting → fable
  agent; the main session reviews everything — verify Examples cell-claims and
  any `hera.analysis` API usage against real files before landing. Never invent
  an API; verify cell ranges with `nb cells` and file_ids via `metadata.json`.
- **`nb` tool** runs from the main checkout (worktree submodules are
  uninitialized): `cd ~/sharpelab/measurement-env && uv run nb
  sections|summary|cells|grep <ipynb>`.
- Durable gotchas: `.claude/agent-memory/subtask_agent/MEMORY.md`.

## Start here

1. Read `recipes/STYLE.md` end to end — it is the law.
2. Skim one completed example of each thing you're building: the readiness
   report (`campaign-readiness-2504.06972.md`) for a gap analysis; the
   trilayer bundle (recipe + `paper.md` + `docs/vti/aba-trilayer-qc0426/README.md` +
   `FUTURE_WORK.md`) for an investigation+tool.
3. If resuming the tMoTe₂ readiness work, the workstream doc's "next steps" is
   the queue; fork a subtask off `hera`.
