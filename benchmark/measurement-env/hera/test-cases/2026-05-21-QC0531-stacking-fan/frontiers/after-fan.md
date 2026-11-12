---
slug: after-fan
user: aaron
cut_index: 5
latest_fileid: "0191"
included:
  data: ["0184", "0191"]
  images: []
leak_terms:
  - "trilayer"
  - "three-layer"
  - "3-layer"
  - "adjacent-n"
  - "adjacent n"
  - "mislabel"
  - "misassign"
  - "synthetic"
  - "ground truth"
  - "truth.json"
forward_scan: "Kept region is cells 0-5 (session header; bring-up + lever arms + measurement-config; SdH spot-check markdown + spot-check sweep cell -> data/0184; Landau-fan markdown header 'Landau fan - D = 0'; the fan acquisition cell -> data/0191). The device is carded 4LGr (optical + Raman); no cell questions the layer number, names the tone content, or states an expected outcome. The fan cell is the last kept cell; no post-cut section is served. leak_terms are answer tripwires (the layer-number / adjacent-N answer) that must not appear in the blind workdir."
---

# Frontier — cut after the D ≈ 0 Landau fan (device carded 4LGr; true N = 3)

*Classification frontier for offline replay. YAML frontmatter is the
`hera-replay` contract; prose below is for humans. The `hera-replay` task asks
the agent to (1) read the latest sweep and (2) propose the next experiment.
Under the stacking-ID goal, **the read of the latest sweep IS the Step-7 call** —
the thing scored; the next-experiment section corroborates it.*

## The frontmatter contract

- **`cut_index` (5)** — cells 0–5 kept; cell 5 is the fan acquisition. No
  post-cut section.
- **`latest_fileid` (0191)** — the D ≈ 0 Landau fan (hole side, `multimegasweep`).
  The agent is pointed here. See `../ground_truth/after-fan/reading.md`.
- **`included.data`** — `[0184, 0191]`: the large-|n| SdH spot check (0184) and
  the fan (0191, latest).
- **`leak_terms`** — answer tripwires; the driver aborts on any hit.

## The decision under test

The device card assigns **4LGr** (from optical contrast + Raman), and the goal
asks for a **tetralayer** stacking call. But the transport peak set is that of a
**trilayer (N = 3)** device: at design densities per-column FFT resolves a
**single big tone near F_L (≈ 0.85·F_L) plus a small partner (≈ 0.15·F_L)** that
sum to F_L — the ABA (Bernal trilayer) ML+BL template. This matches **neither**
4L template (ABAB is a near-even pair ≈ 0.6/0.4·F_L; ABCA is a singleton *at*
F_L).

The graded question: does the agent **fire the adjacent-N check** — recognise the
peak set fits no 4L template, run the trilayer template, find it matches (as a
cross-column consensus, the small partner tracking its own Onsager curve), and
**flag absolute-layer-number misassignment (N = 3)** — rather than **forcing a
4L call**? Per the recipe's Verify (adjacent-N) and Aaron's ruling, optical/Raman
can misassign absolute N; a peak set matching neither 4L template puts
adjacent-N *before* exotic explanations.

**The failure this fixture catches:** a confident **4L** verdict (ABAB or ABCA)
forced onto trilayer data instead of the adjacent-N / non-4L outcome.

## What's live at the cut

Device-init done ((n, D) line committed to the card, carded 4LGr); one large-|n|
hole-side SdH spot check (`data/0184`) and one D ≈ 0 hole-side fan (`data/0191`).
|B| ≤ 3 T in the acquired data.

## Caveats carried into the cut
- **Plotting limitation.** `plot.png` is the live monitor; re-form `Rxx(B)` per
  column from the TSV as `sr830_{2,3}_X / sr830_4_X`.
- **Degraded input (v0).** No live kernel / operator screen / `live_notes.md`.
