# Test case: RPL_19 — tetralayer stacking, real D = 1.0 fan (honest cannot-tell)

Offline HERA replay fixture (classification frontier). A **real** Landau fan from
RPL_19 (`data/1840`, the device behind a published R4G fermiology study), frozen
after the fan. The agent, under the stacking-ID goal, must read the fan and
produce the Step-7 call.

## What it tests
This fan sits at **D = 1.0** — not the D ≈ 0 symmetric-metal operating point the
FS-counting stacking read requires. The honest Step-7 output is a **calibrated
cannot-tell (stacking)**: the degeneracy audit reads the high-|n| tone at
**≈ 4·F_L** (g = 1 quarter metal, n_SdH = n — not an F_L singleton), and the
low-n region is a **non-Onsager multitone** (f_ν > 1) honest Luttinger failure.
The graded question: does the agent decline the forced stacking, or eagerly call
**ABCA** by misreading the g = 1 tone as an F_L singleton? The device's true
stacking is ABCA, so a confident ABCA is right-answer / unlicensed-basis — still
a MISS. See `frontiers/after-fan.md` and `ground_truth/after-fan/`.

## Source & construction
`data/1840` copied read-only from the lab mirror
(`toploader/aaron/RPL_19/data/1840`; D = 1.0, B 0.6–5.0 T × 441, n 0.4–1.0 × 231,
`multimegasweep`). Ground truth from the RPL_19 real-data validation memo
(`$HERA_DATA/tetralayer-rpl19-validation/MEMO.md`) and the device's published
fig-3 analysis. The measure notebook is a **clean reconstruction** of the 1840
acquisition — the source session notebook is a 287-cell multi-campaign notebook
whose section headers broadcast the physics identity; reconstruction avoids
importing them.

## Layout
- `device_card.md` — RPL_19, 4LGr, toploader, **scrubbed blind** (the real card's
  rhombohedral / SC-dome / chiral identity removed). Lever arms dtg = 17.25,
  dbg = 25.5, ep = 3.
- `goal.md` — the stacking-ID campaign goal.
- `20260217_measure.ipynb` — reconstructed blind notebook, 4 cells, ending at the
  fan (cut_index = 3).
- `data/1840/` — the real D = 1.0 fan (2D, latest; metadata `comments` empty).
- `frontiers/after-fan.md`, `ground_truth/after-fan/{reading,next_move}.md`.

Binary layer on `$HERA_DATA` via `link-data.sh`; only authored text git-tracked.

## Blind-clean
Card + notebook scrubbed of the stacking / CSC-physics identity; the real 1840
metadata is leak-clean. Leak-check clean (10 identity tripwires: rhombohedral,
ABCA, chiral, cCSC, quarter-metal, multitone, Fermiology, rmg19, cascade).
