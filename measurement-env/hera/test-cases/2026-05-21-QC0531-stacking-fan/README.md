# Test case: QC0531 — tetralayer stacking, mislabeled layer number (true N = 3)

Offline HERA replay fixture (classification frontier). A **synthetic** D ≈ 0
Landau fan on a device **carded 4LGr** whose transport is actually **trilayer
(N = 3)**, frozen after the fan acquisition. The agent, under the tetralayer
stacking-ID goal, must read the fan and produce the Step-7 call.

## What it tests
The peak set is the trilayer **ABA** ML+BL template — a high-f tone ≈ 0.85·F_L
plus a low-f partner ≈ 0.15·F_L summing to F_L — matching **neither** 4L template
(ABAB near-even pair; ABCA singleton at F_L). The graded question: does the agent
**fire the adjacent-N check** and report non-4L / N = 3, or **force the carded 4L
call**? (Classify on frequency: the near-F_L tone is Dingle-weak, the low-f
partner amplitude-dominant.) See `frontiers/after-fan.md` and
`ground_truth/after-fan/`.

## Source & construction
Generated from `$HERA_DATA/tetralayer-synth-validation/mislabeled_N/fan.npz`
(generator `synth_fan.py`, case `mislabeled_N` = an ABA trilayer fan labelled
4LGr) via `hera/models/tetralayer_fs_count/synth_to_house.py`. Tone recovery
verified to < 1.5 %, (n, D) round-trip to machine precision.

## Layout
- `device_card.md` — QC0531, **carded 4LGr** (optical + Raman), toploader,
  dual-gated, blind. Lever arms dtg = 19.2, dbg = 22.6, ep = 3.
- `goal.md` — the tetralayer stacking-ID campaign goal.
- `20260521_measure.ipynb` — blind measure notebook, 6 cells, ending at the fan
  (cut_index = 5).
- `data/0184/` — large-|n| hole-side SdH spot check (1D). `data/0191/` — the
  D ≈ 0 hole-side Landau fan (2D, latest).
- `frontiers/after-fan.md`, `ground_truth/after-fan/{reading,next_move}.md`.

Binary layer on `$HERA_DATA` via `link-data.sh`; only authored text git-tracked.

## Blind-clean
The device card asserts 4LGr with no hint of the mislabel; no file carries
"trilayer / N = 3 / adjacent-N / synthetic" framing. Leak-check clean (10 terms).
