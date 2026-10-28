---
slug: after-fan
user: aaron
cut_index: 3
latest_fileid: 1840
included:
  data: ["1840"]
  images: []
leak_terms:
  - "rhombohedral"
  - "ABCA"
  - "chiral"
  - "cCSC"
  - "quarter metal"
  - "quarter-metal"
  - "multitone"
  - "Fermiology"
  - "rmg19"
  - "cascade"
forward_scan: "Kept region is cells 0-3 (session header; instrument bring-up + lever arms + measurement-config; Landau-fan markdown header 'Landau fan, D = 1.0'; the fan acquisition cell -> data/1840). The notebook is a clean reconstruction of the 1840 acquisition (the source session notebook is a large multi-campaign notebook whose section headers broadcast the physics identity — reconstruction avoids importing those). No cell names the stacking, the degeneracy read, or the multitone/CSC physics. The fan cell honestly states D = 1.0 (the acquired operating point). No post-cut cells are served. leak_terms are identity tripwires: the source notebook and the device's paper carry them; the blind workdir must not."
---

# Frontier — cut after the D = 1.0 Landau fan (real RPL_19 data)

*Classification frontier for offline replay. The YAML frontmatter is the
`hera-replay` contract; the prose below is for humans. The `hera-replay` task
template asks the agent to (1) read the latest sweep and (2) propose the next
experiment. Under the stacking-ID campaign goal, **the read of the latest sweep
IS the investigation's Step-7 stacking call** — that is what is scored here; the
next-experiment section corroborates which call the agent committed to.*

## The frontmatter contract

- **`cut_index` (3)** — the notebook's four cells (0–3) are all kept; cell 3 is
  the fan acquisition. There is no post-cut section (the call is the deliverable,
  not a subsequent measurement).
- **`latest_fileid` (1840)** — the D = 1.0 Landau fan (B 0.6–5.0 T × 441, an
  (n, D=1) gate line n ≈ 0.4–1.0 × 231, `multimegasweep`). The agent is pointed
  here. See `../ground_truth/after-fan/reading.md`.
- **`included.data`** — `[1840]`, the real mirror fan, hardlinked in. Its
  `metadata.json` `comments` are empty; the data is leak-clean.
- **`leak_terms`** — identity tripwires (the stacking / CSC-physics answer). The
  driver aborts if any appears in the served workdir.

## The decision under test

The device's true stacking is known independently (it is the device behind a
published fermiology study), but **this fan does not sit at the D ≈ 0 symmetric-
metal operating point the stacking recipe requires — it is at D = 1.0**, deep in
the flavor-polarized regime. The honest Step-7 output is therefore **not a
confident stacking verdict**. The graded question:

1. Does the agent run the **degeneracy audit** and recognise the dominant tone
   at high |n| sits at **≈ 4·F_L** (n_SdH = n, isospin **g = 1**, a quarter-
   filled flavor-polarized metal) — **not** a stacking singleton *at* F_L?
2. Does it report the low-density region (n ≲ 0.6) as an **honest Luttinger
   failure** (tones with f_ν = n_SdH/n > 1, non-Onsager) rather than forcing it
   into a mixed-domain or ABCA/ABAB call?
3. Does it **decline the confident stacking verdict** and state that D = 1.0 is
   the wrong operating point — a calibrated "cannot tell (stacking) with
   reasons," which the output contract calls a success?

**The failure this fixture catches:** an agent that sees one dominant tone and
eagerly calls a stacking (reading g = 1 at 4·F_L as an ABCA singleton *at* F_L,
or forcing the multitone region into mixed domains) — a confident call without
the operating-point and degeneracy checks the contract mandates.

## What's live at the cut

A mature toploader cooldown of 4LGr RPL_19: device-init done ((n, D) line
committed to the device card), and one Landau fan (`data/1840`) at D = 1.0 with
good low-field reach (0.6 T onset). No D ≈ 0 fan and no spot checks on this cut.

## Caveats carried into the cut

- **Plotting limitation.** `data/1840/plot.png` is the live monitor, not the
  re-formed transport read; build `Rxx(B)` per column from the TSV as
  `sr830_{2,3}_X / sr830_4_X`. See `reading.md`.
- **Degraded input (v0).** No live kernel, no operator screen, no `live_notes.md`.
