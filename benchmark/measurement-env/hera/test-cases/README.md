# HERA replay fixtures — authoring spec

How to build a fixture for the offline measurement-suggestion benchmark
(`hera/docs/benchmark-plan.md`). Conventions locked 2026-05-31 during the
design review of the reference fixture, `2026-05-06-b1c2-sc-characterization/`.
**Read that fixture alongside this spec — it is the worked example.**

A fixture freezes a real campaign at one or more **frontiers** (decision
boundaries) and hands the frozen state to a HERA-shaped agent via `hera-replay`,
which judges its next-move proposal against captured ground truth. The whole
game is **no leakage**: the agent must see exactly what a live operator saw up
to the cut, and nothing about what came after.

## Directory layout

```
<date>-<device>-<slug>/            # date = capture date; device + short slug
  device_card.md                   # device physical properties + measurement
                                   #   SETUP THIS RUN (instruments/knobs wired)
  goal.md                          # expert framing; the blockquote is the goal
  <stamp>_measure__cAAA-BBB.ipynb  # cropped source notebook, outputs preserved
  <stamp>_ana__*.ipynb             # OPTIONAL, post-hoc analysis — NEVER served
  data/<file_id>/                  # tsv.gz + metadata.json + plot.png per sweep
  images/cell<srcN>_out<M>.png     # cell PNG outputs, named by SOURCE-cell index
  cell-to-fileid.md                # cell ↔ file_id map (human aid; not served)
  README.md                        # what the fixture is + per-cell modality
  frontiers/<slug>.md              # ONE per cut point — see "Frontier file"
  ground_truth/<slug>/
    next_move.md                   # what the expert actually did next
    reading.md                     # correct read of the latest sweep (layer A)
  runs/<slug>/<config>-<ts>/       # driver output (gitignore-able)
```

One source notebook → one fixture dir → **several frontiers** (one `.md` under
`frontiers/`, one `ground_truth/<slug>/` each). The data/images pool is shared
across frontiers; the allowlist in each frontier file selects its pre-cut slice.

## Frontier file (`frontiers/<slug>.md`)

YAML frontmatter is the machine-readable contract `hera-replay` reads; the prose
below it is for humans. Required frontmatter:

```yaml
---
slug: after-idc-vs-n
cut_index: 32              # fixture-relative, 0-based, INCLUSIVE
latest_fileid: 84          # freshest sweep at the cut (agent is pointed here)
included:
  data: [75, 76, 77, ...]  # ALLOWLIST of pre-cut data dirs — authoritative
  images: [cell254_out2.png, ...]
leak_terms: ["mag.field", "B vs Idc", ...]   # must NOT appear in the workdir
forward_scan: "kept cells greped for forward refs; clean (only section headers)"
---
```

## The five rules (what the review locked)

1. **Cut on a section boundary.** `cut_index` is the last cell of a completed
   section; the next section's header is the first thing the agent must predict.
   This makes truncation leak-safe (every later header drops) and the decision
   crisp ("a section landed — what experiment next?"). Don't cut mid-section
   unless you have a reason, and if you do, re-check rule 3 hard.

2. **Pick boundaries where judgment lives.** A good frontier's next section is a
   genuine branch point (a new measurement axis, a go/no-go), not a mechanical
   retune or a calibration tail. The `# find 90 degrees theta` tail in the b1c2
   notebook is a *bad* frontier target — skip those.

3. **Allowlist, don't denylist.** `included.data` / `included.images` list only
   pre-cut artifacts. The driver hardlinks exactly these — so the leak is
   *adding the wrong id*, which is easy to eyeball, rather than *forgetting to
   exclude* something. Derive the list from the cell↔file_id map for cells
   ≤ cut_index.

4. **Leak terms must be post-cut-only tripwires.** Choose strings that appear in
   the answer-key region but **never** before the cut — verify with
   `nb grep <notebook> -i <term>` and check the cell indices are all > cut_index.
   The best ones are the literal *sweep calls* the future uses and the past
   doesn't (e.g. `mag.field` — the qcodes magnet-sweep call — for an SC campaign
   whose characterization phase never sweeps the magnet). The driver greps the
   assembled workdir and **aborts** (exit 2) on any hit — this is the backstop,
   not the primary control.
   - **Capability vs. call.** A leak term is the *answer's code*, not the
     *existence of the instrument*. The device card may say "an AMI430 magnet is
     wired (perpendicular field, Tesla)" — that's legit setup context (rule 6) —
     while `mag.field(...)` (the actual sweep) stays a tripwire. Word the device
     card to avoid the literal token, so capability context and the leak guard
     coexist.

6. **Declare the measurement setup (instruments available).** A fixture cropped
   mid-notebook strips the cells that instantiate instruments, so the agent
   cannot tell what hardware exists — and will wrongly rule out experiments on
   knobs it can't see (observed: an agent deferred a field sweep because the
   magnet wasn't visible in the cropped cells, when it was wired in cell ~1 of
   the source). The fix lives in `device_card.md`: treat the card as **device
   physical properties + the measurement setup for this run** — gates, DC bias
   (+ bias resistor), lock-ins (channel→contact + gains), heater/thermometry,
   **magnet, rotator**. This is cooldown-invariant rig state for the toploader,
   so it's mostly boilerplate per device; fill it in for every fixture. It is
   setup state, not a forward-looking decision — not leakage.

5. **`forward_scan` is a human attestation.** Structural cropping cannot catch a
   markdown/comment cell *inside the kept region* that says "next we'll sweep
   field." Grep the kept cells' markdown + comments for forward references by
   hand, and record the result in `forward_scan`. If you find one, redact it in
   the cropped notebook and say so.

## Ground truth

- `next_move.md` — what the expert actually did in the next section (the sweep
  call + file_id), **why** it's the right move, and the judging buckets for this
  item: {same experiment / same class, diff params / different but reasonable /
  divergent or worse}. It is **one** good path, not the only answer — used to
  route to review, never as an exact-match score.
- `reading.md` — the correct read of `latest_fileid` (perception layer A). Write
  it as a **floor** (the must-see findings) plus explicit "don't penalize the
  agent for X" caveats about plotting/scope limitations — not an exhaustive key.
  The agent will often out-detail it; that's fine.

## `live_notes.md` — when (almost never)

Add a `live_notes.md` (operator observations not on disk) to a frontier **only
when the decision *class* flips without it** — i.e. an expert at the cut would
choose a fundamentally different experiment knowing the live fact. **Never** add
it to patch a parameter-level guess (a range, a step count, a magnet offset). If
the agent picks the right experiment but the wrong numbers because it couldn't
know a live value, that is correct degraded-input behavior — leave it.

## Data layout (where the bytes live)

A fixture is ~99.9% binary / 0.1% authored text. Only the authored layer
(`frontiers/`, `ground_truth/`, `*.md`) is tracked in git. The binary layer
(`*.ipynb`, `data/`, `images/`, `runs/`) lives on the data volume —
`$HERA_DATA` (default `/data/sharpelab/hera-data`), a btrfs subvol off the
snapshotted `/home`, with its own 7-daily snapshots — and is symlinked back into
the fixture dir. The driver reads through the symlinks transparently and new
`runs/` land on the data volume automatically.

After building a fixture's binaries, relocate them with:

```bash
HERA_DATA=/data/sharpelab/hera-data ./link-data.sh <fixture-dir>   # idempotent
```

`.gitignore` keeps `*/data`, `*/images`, `*/runs`, `*/*.ipynb` out of git.

## Running

```bash
uv run hera-replay <fixture> [--frontier <slug>] [--config <name>] [--model M] [--samples N]
uv run hera-replay <fixture> --frontier <slug> --dry-run   # build + leak-check only
```

`--frontier` is optional when the fixture has exactly one. `--dry-run` builds
the workdir, runs the leak-check, and prints the prompt without spending a model
call — **always dry-run a new frontier first** and confirm `leak-check: clean`.
Runs land in `runs/<slug>/<config>-<ts>/` with `output.md`, `result.json`,
`prompt.md`, and a `manifest.json` recording the resolved model + per-sample cost.

**Sampling.** Run-to-run variance is real and can flip the decision *class*
(observed: same config, one sample proposed a field sweep, another a gate-cut).
Take **N = 3–5 samples per frontier** (`--samples`) and judge the distribution,
never a single draw. Samples share one read-only workdir and land in
`sample-<i>/` subdirs. Run the auto-screen + lever sweep on a **cheaper model**
(`--model claude-sonnet-4-6`) to keep cost sane; reserve the expensive model for
the final expert-batch config.
