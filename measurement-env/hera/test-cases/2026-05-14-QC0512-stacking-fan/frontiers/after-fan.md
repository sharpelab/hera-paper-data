---
slug: after-fan
user: aaron
cut_index: 5
latest_fileid: "0213"
included:
  data: ["0207", "0213"]
  images: []
leak_terms:
  - "breakdown"
  - "sum-tone"
  - "sum tone"
  - "intermodulation"
  - "synthetic"
  - "ground truth"
  - "truth.json"
  - "trilayer"
forward_scan: "Kept region is cells 0-5 (session header; bring-up + lever arms + measurement-config; SdH spot-check markdown + spot-check sweep cell -> data/0207; Landau-fan markdown header 'Landau fan - D = 0'; the fan acquisition cell -> data/0213). No cell names the stacking, the tone content, the F_L-tone origin, or any expected outcome. The fan cell is the last kept cell; no post-cut section is served. leak_terms are answer/mechanism tripwires that must not appear in the blind workdir."
---

# Frontier — cut after the D ≈ 0 Landau fan (synthetic ABAB w/ breakdown)

*Classification frontier for offline replay. YAML frontmatter is the
`hera-replay` contract; prose below is for humans. The `hera-replay` task asks
the agent to (1) read the latest sweep and (2) propose the next experiment.
Under the stacking-ID goal, **the read of the latest sweep IS the Step-7 stacking
call** — the thing scored; the next-experiment section corroborates the call.*

## The frontmatter contract

- **`cut_index` (5)** — cells 0–5 kept; cell 5 is the fan acquisition. No
  post-cut section (the call is the deliverable).
- **`latest_fileid` (0213)** — the D ≈ 0 Landau fan (hole side, `multimegasweep`,
  field slow × paired-gate n-line fast). The agent is pointed here. See
  `../ground_truth/after-fan/reading.md`.
- **`included.data`** — `[0207, 0213]`: the large-|n| SdH spot check (0207) and
  the fan (0213, latest).
- **`leak_terms`** — answer/mechanism tripwires; the driver aborts on any hit.

## The decision under test

The fan is a **two-pocket ABAB** (Bernal) tetralayer: at design densities two
fundamental SdH tones, both below F_L, **partition F_L** (their frequencies sum
to the Luttinger line and each tracks its own Onsager curve across n). Crucially
there is **also a third tone sitting exactly at F_L that strengthens toward high
B** — a **magnetic-breakdown sum-tone** (inter-block breakdown is symmetry-
allowed for ABAB). That F_L tone **mimics an ABCA singleton**.

The graded question: does the agent **run the F_L-tone-origin discrimination**
(the recipe's mandatory check before any singleton call) — the B-window split
that shows the F_L tone growing with B relative to the fundamentals — and call
**ABAB** off the resolved pair? Or does it eagerly read the tone at F_L as an
**ABCA singleton** and skip the discrimination?

**The failure this fixture catches:** a confident **ABCA** call, taking the F_L
breakdown/sum-tone for the single chiral pocket.

## What's live at the cut

Device-init done ((n, D) line committed to the card); one large-|n| hole-side
SdH spot check (`data/0207`) and one D ≈ 0 hole-side fan (`data/0213`). |B| ≤ 3 T
in the acquired data.

## Caveats carried into the cut
- **Plotting limitation.** `plot.png` is the live monitor; re-form `Rxx(B)` per
  column from the TSV as `sr830_{2,3}_X / sr830_4_X`.
- **Degraded input (v0).** No live kernel / operator screen / `live_notes.md`.
