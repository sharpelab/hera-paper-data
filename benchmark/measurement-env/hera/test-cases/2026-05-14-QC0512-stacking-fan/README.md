# Test case: QC0512 — tetralayer stacking, ABAB with a breakdown sum-tone

Offline HERA replay fixture (classification frontier). A **synthetic** D ≈ 0
Landau fan on a dual-gated 4LGr device, frozen after the fan acquisition. The
agent, under the stacking-ID goal, must read the fan and produce the
investigation's Step-7 call (`investigations/tetralayer-stacking-fs-count.md`).

## What it tests
The fan is a two-pocket **ABAB** tetralayer: two fundamentals partition F_L,
**plus** a magnetic-breakdown sum-tone sitting *at* F_L that grows with B and
mimics an ABCA singleton. The graded question: does the agent run the
**F_L-tone-origin discrimination** (B-window split) and call ABAB, or eagerly
call **ABCA** off the F_L tone? See `frontiers/after-fan.md` and
`ground_truth/after-fan/`.

## Source & construction
Generated from the rung-3a validated fan
`$HERA_DATA/tetralayer-synth-validation/abab_breakdown/fan.npz` (generator
`hera/models/tetralayer_fs_count/synth_fan.py`) via
`hera/models/tetralayer_fs_count/synth_to_house.py`, which encodes `Rxx(n, B)`
into the house sweep format (`Rxx = sr830_{2,3}_X / sr830_4_X`; gate columns set
to (n, D = 0) via the device-card lever arms). Tone recovery verified to < 1.5 %,
(n, D) round-trip to machine precision.

## Layout
- `device_card.md` — QC0512, 4LGr, toploader, dual-gated, blind (stacking not
  assigned). Lever arms dtg = 18.0, dbg = 24.0, ep = 3.
- `goal.md` — the stacking-ID campaign goal (blockquote handed to the agent).
- `20260514_measure.ipynb` — blind measure notebook, 6 cells, ending at the fan
  acquisition (cut_index = 5).
- `data/0207/` — large-|n| hole-side SdH spot check (1D). `data/0213/` — the
  D ≈ 0 hole-side Landau fan (2D, latest).
- `frontiers/after-fan.md`, `ground_truth/after-fan/{reading,next_move}.md`.

Binary layer (`data/`, `*.ipynb`) lives on `$HERA_DATA` via `link-data.sh`; only
authored text is git-tracked.

## Blind-clean
Notebook cells, metadata, and plots carry no "synthetic / test / ABAB / ABCA /
breakdown / trilayer" framing; the device card reads as an ordinary 4LGr device.
Leak-check clean (8 terms).
