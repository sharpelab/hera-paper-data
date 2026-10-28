# Extract brief — RPL_10 / RPL_19 fixture batch (2026-06-01)

You are building **one HERA replay fixture** from one source notebook. Follow the
authoring spec exactly and use the existing b1c2 fixture as your concrete template.

## Read first (do not skip)
1. `hera/test-cases/README.md` — the authoring spec (layout, frontmatter
   contract, the rules, ground-truth-as-floor, the depth/instrument conventions).
2. The reference fixture `hera/test-cases/2026-05-06-b1c2-sc-characterization/` —
   open `frontiers/after-idc-vs-n.md`, `ground_truth/after-idc-vs-n/*`,
   `briefs/after-idc-vs-n/*`, `device_card.md`. **Copy these shapes.**
3. `hera/docs/tactical-brief.md` — the brief variants (2×2 autonomy×length; depth
   probe quick/deep/paper) and what each field means.
4. The relevant entry in `hera/docs/notebook-indexes/notebook-index-<DEVICE>.md`
   for your notebook's section structure + synopsis (your starting map).

## Source data
- Source notebooks: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_<N>/`.
- Sweep data: `…/RPL_<N>/data/<file_id>/` — each has `metadata.json`
  (`function`, `slow_params`/`fast_params`, `slow_setpoints`, `start_time`,
  `comments`), `data.tsv(.gz)`, `plot.png`. ~2100 dirs spanning the device's whole
  life, roughly chronological by `file_id` and by `start_time`.
- `nb` handles the giant notebooks fine (it skips outputs):
  `uv run nb sections|summary|cells|grep <notebook>`. Use it; don't load the raw
  ipynb.

## Build steps (per frontier)
1. **Confirm the cut.** `nb sections` + `nb summary <range>` on the source
   notebook. The cut sits on a **section boundary**: `cut_index` = last cell of
   the completed section; the next section header is what the agent must predict.
   The slate gives approximate indices — confirm them.
2. **Crop the notebook into the fixture.** Write cells `0..(max cut among this
   fixture's frontiers + that section's next section, for ground-truth)` to
   `<fixture>/<stamp>_measure__c0-<N>.ipynb` (parse JSON, slice `cells`, dump).
   Cropping from 0 means **fixture indices == source indices** — keep it that way.
3. **Map data file_ids.** Identify this notebook's file_id range: its first sweep
   ≈ the notebook date / earliest `start_time`; many notebooks have an explicit
   "file number" annotation cell — use it. For each frontier, `latest_fileid` =
   the last real sweep at/just before the cut (match the sweep cell's
   `add_comment`/function/params against `data/<id>/metadata.json`). The
   **allowlist** = all data dirs in `[notebook_first_id, latest_fileid]` (the
   start_time-cutoff method the b1c2 fixture used). Copy those dirs into
   `<fixture>/data/<id>/` (real dirs — do NOT symlink to $HERA_DATA; the batch is
   partitioned later). Write `cell-to-fileid.md` (cell ↔ file_id, like b1c2's).
4. **Images (light).** The agent reads `data/<id>/plot.png` directly, so a
   separate `images/` is optional. If a frontier's latest sweep has a useful
   cell plot, you may `nb extract` it; otherwise rely on `plot.png`.
5. **`frontiers/<slug>.md`** — YAML frontmatter (`slug, cut_index, latest_fileid,
   included:{data,images}, leak_terms, forward_scan`) + prose. **leak_terms must
   be post-cut-only** — verify each with `nb grep <notebook> -i <term>` and check
   ALL matching cells are `> cut_index`. Good tripwires: section headers of
   post-cut sections, and instrument/function names the future uses but the past
   doesn't. **forward_scan**: grep the kept markdown/comments (cells 0..cut) for
   forward references; record "clean" or redact.
6. **`ground_truth/<slug>/next_move.md`** — what the operator actually did in the
   next section (the sweep call + file_id), why it's a good move, and the judging
   buckets (same / same-class / different-reasonable / divergent). It is ONE good
   path. **`reading.md`** — read the latest sweep's `plot.png` + `metadata.json`
   and describe it as a floor + "don't penalize for X" caveats. **Flag any physics
   you're unsure of** — better an honest "candidate feature, needs expert check"
   than a confident wrong claim.
7. **`device_card.md`** — from the notebook's Init/Configs cells + the index
   synopsis. MUST include a **"Measurement setup (instruments wired this
   cooldown)"** section: gates + validators, DC bias source + bias resistor,
   lock-ins (channel→contact + gains), heater/thermometry, **magnet (AMI430 /
   Yoko as present), rotator** — described as *capability* (do NOT write the
   literal sweep-call token that's a leak_term). Note cooldown/material identity.
8. **`briefs/<slug>/`** — adapt the b1c2 briefs to this frontier's physics:
   - **contested** frontier → the 2×2: `open-short`, `open-long`,
     `directive-short`, `directive-long` (depth held = deep investigation).
   - **depth** frontier → `quick`, `deep`, `paper` on a single directive anchor.
   Keep the `<!-- variant: … -->` comment headers. The directive briefs encode
   the operator's actual next move (that's the revealed strategic decision).
9. **Self-verify (required).** For EACH frontier:
   `uv run hera-replay <fixture> --frontier <slug> --dry-run`
   It must print **`leak-check: clean`** and the expected data/images allowlist.
   If it reports a LEAK, fix the allowlist or leak_terms and re-run until clean.
   Do NOT do live (non-dry-run) runs — no model spend during the build.

## Rules / reminders
- Cut on a section boundary; never include post-cut cells in the served notebook
  (the driver crops to cut_index, but your stored notebook + allowlist must not
  smuggle the answer).
- Allowlist, don't denylist. Capability (instrument exists) is legit context; the
  literal post-cut sweep *call* is a leak term.
- This is **coding mode**: write files, run `nb`/`hera-replay --dry-run`. Do NOT
  commit, do NOT push, do NOT run `link-data.sh`.

## Report back
Return: the fixture dir path, each frontier slug + confirmed cut_index +
latest_fileid + #data dirs in allowlist, the leak-check result per frontier, and
a short list of anything uncertain (especially physics in `reading.md`) for human
review.
