---
slug: after-idc-vs-n
user: isaac
cooldown_drift: true
cut_index: 32
latest_fileid: 84
included:
  data: [75, 76, 77, 79, 80, 81, 82, 83, 84]
  images: [cell254_out2.png, cell255_out45.png, cell260_out38.png, cell261_out18.png, cell269_out38.png, cell270_out18.png, cell274_out53.png]
leak_terms:
  - "mag.field"
  - "B vs Idc"
  - "find 90 degrees"
  - "theta"
forward_scan: "kept region (cells 0-32) greped for forward references (mag.field / B vs Idc / find 90 / theta / fraunhofer / perpendicular); only the three section headers present (nT map at Beff = 0, Idc vs T, Idc vs n). Clean."
---

# Frontier — cut at end of `# Idc vs n`

*Defines the decision boundary at which this fixture freezes the campaign for
offline replay. The YAML frontmatter above is the machine-readable contract the
`hera-replay` driver reads; the prose below is for humans. One source notebook
can carry several frontiers (one file each under `frontiers/`); this is the
first. Added 2026-05-28 (Phase 0), converted to the frontmatter format
2026-05-31.*

## The frontmatter contract

- **`cut_index`** — fixture-relative, 0-based, inclusive. The agent sees cells
  `0..cut_index`; everything after is the answer key.
- **`latest_fileid`** — the freshest sweep at the cut; the agent is pointed here
  as "the most recent result." See `../ground_truth/after-idc-vs-n/reading.md`.
- **`included.data` / `included.images`** — the **allowlist** of pre-cut
  artifacts the driver hardlinks into the working copy. This is authoritative;
  the driver copies *only* these, so adding a post-cut sweep id here would be
  the leak. Derived once, by hand, and reviewed.
- **`leak_terms`** — strings that must not appear anywhere in the assembled
  working copy. The driver greps and **aborts** the run if any hit. Chosen to be
  post-cut-only in this notebook: `mag.field` (the SC-characterization sections
  never touch the magnet — the `# B vs Idc` answer does), plus the post-cut
  header text.
- **`forward_scan`** — the human attestation that the kept markdown/comments
  were checked for forward references (the one leak vector structural cropping
  can't catch).

## Cut

- **Cut index 32** sits exactly on a **section boundary**: index 32 is the last
  cell of `# Idc vs n` (`dc205_1.volt(0)` — parking the bias to zero after the
  sweep). Index 33 is the `# B vs Idc` markdown header — the first cell of the
  *next* experiment, which is the thing HERA is being asked to predict.
- **No mid-section header leak.** Because the cut is on a boundary, simple
  truncation at index 32 keeps the legitimate `# Idc vs n` header (index 29) and
  drops `# B vs Idc`. No lookahead headers survive the cut.

## What's live at the cut

The campaign has, in order, completed three sub-experiments toward Isaac's
stated goal ("characterize the superconducting state"):

1. `# nT map at Beff = 0` (idx 0–19) — (n,D) gate maps vs heater/temperature at
   zero effective field.
2. `# Idc vs T` (idx 20–28) — DC-bias × temperature (heater) sweeps.
3. `# Idc vs n` (idx 29–32) — DC-bias × carrier-density sweep at fixed D.

**Latest landed sweep: `data/84/`** (cell idx 31). State at the cut: gates
parked, bias returned to 0 V, base temperature (~29 mK), no field applied — all
work so far is at Beff = 0.

## Caveats carried into the cut

- **Cooldown drift.** The `device_card.md` describes the *current* cooldown
  (post-2026-05-04); the data in `data/75–84/` is from the *prior* cooldown
  (2026-04-23 → 2026-04-25). A genuine confound, not a fixture bug — note
  whether the agent catches it.
- **Degraded input (v0).** No live kernel, no operator screen observations, and
  deliberately **no `live_notes.md`**: the next decision (run a field sweep)
  does not hinge on an unrecorded live observation — only the *field range* does
  (the magnet's "Beff = 0" sits at a remanent offset ≈ −6.8 mT, which the agent
  cannot know from disk). Per the locked principle, live_notes is added only when
  the decision *class* flips without it, never to patch a parameter-level guess.
