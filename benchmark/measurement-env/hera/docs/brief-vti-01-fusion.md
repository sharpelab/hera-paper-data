# vti-01 — Raman×transport fusion brief

*You are a fresh instance producing the fused stacking verdict for vti-01.
This brief names the goal, inputs, and isolation rules; the method lives in
the recipe.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
execute the fusion recipe, and write one output file plus its artifacts.
Analysis only.

## Goal

**Produce the fused, region-resolved stacking verdict for vti-01** — execute
`~/sharpelab/measurement-env/hera/recipes/investigations/stacking-raman-transport-fusion.md`
and deliver its Step 5 output contract. A fused "cannot tell" or a
well-evidenced disagreement is a successful outcome; forcing concordance is
a protocol violation.

## Inputs — the complete set

All under `/data/sharpelab/hera-data/raman-vti-01-fusion/inputs/`:

- **Transport contract** (locked stacking call): `transport-call.md`
- **Raman contract** (locked, stage-stamped): `raman-contract.md`, with its
  Step 0 `raman-provenance.md` and region-label raster `regions.npz` /
  `regions.png`
- **Raw Raman data**: `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip`
  (WITec project; the stage-registered video images inside it are the only
  frame bridge)
- **Frame bridges** beyond the in-file video (optical images, GDS,
  build-step list): none supplied.
- **Ana notebook + session notes** backing the transport call:
  `20260818_ana.ipynb`, `session_notes.md`
- **Device card**: `device_card.md`

If a listed input is missing, or a contract fails admissibility (recipe
Step 1), stop and report — don't reconstruct it.

## Data isolation — strict

Your only inputs are the files above plus the corpus:
`~/sharpelab/measurement-env/hera/recipes/`,
`~/sharpelab/measurement-env/hera/models/`, and the papers and docs they
cite (`hera/docs/papers/`, `hera/docs/raman-public-data.md`).

- **Never read**: any prior fusion attempt, draft, or verdict for this
  device; any human's read, lean, or reaction to either modality's call;
  any document not in your input list — no other directories under
  `hera/`, no session archives, no email, chat, or wiki.
- If forbidden material reaches you anyway, stop and report the
  exposure — a contaminated fusion is not repaired by ignoring what you saw.
- Your output carries a **provenance line**: what you received, and that
  you saw no prior fusion attempt and no third-party views.

## Arc

1. **Admissibility + independence** (recipe Step 1 and the independence
   audit) — these gate everything downstream.
2. **Recipe Steps 2–5** as written. The registration artifact (Step 2) is
   binding — produce it from the frame bridges you actually have (in-file
   video images, the device card's contact map, the ana notebook's
   geometry), and state the registration uncertainty against the domain
   scale. Where coverage cannot be established, the row is uncovered — no
   interpolation.
3. **Verify** — all four audits.

Archive figures, intermediates, and the scripts that regenerate them under
`/data/sharpelab/hera-data/raman-vti-01-fusion/` and cite them by path.

## Output

One file, `/data/sharpelab/hera-data/raman-vti-01-fusion/fusion-verdict.md`:
the Step 5 output contract (the Step 4 table over every named channel —
sr1, sr2, sr3 — per-region verdicts on the strength scale, the
registration-artifact pointer, named hedges, what-would-settle for every
unreconciled row) plus the provenance line.
