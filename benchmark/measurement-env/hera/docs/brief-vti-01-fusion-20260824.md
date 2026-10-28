# vti-01 — Raman×transport fusion brief (2026-08-24)

*You are a fresh instance producing the fused stacking verdict for vti-01.
This brief names the goal, the inputs, the output contract, and the isolation
rules; the fusion method is yours to derive from them.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
derive and execute your own fusion analysis, and write one output file plus
its artifacts. Analysis only.

## Goal

**Produce the fused, region-resolved stacking verdict for vti-01** from the
transport contract and the Raman contract below. A fused "cannot tell" or a
well-evidenced disagreement is a successful outcome; forcing concordance is
a protocol violation.

## Inputs — the complete set

All under `/data/sharpelab/hera-data/raman-vti-01-fusion-20260824/inputs/`:

- **Transport contract** (locked stacking call): `transport-call.md`
- **Raman contract** (locked, stage-stamped): `raman-contract.md`, with its
  `raman-provenance.md` and region-label raster `regions.npz` /
  `regions.png`
- **Raw Raman data**: `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip`
  (WITec project; the stage-registered video images inside it are the only
  frame bridge)
- **Frame bridges** beyond the in-file video (optical images, GDS,
  build-step list): none supplied.
- **Ana notebook + session notes** backing the transport call:
  `20260818_ana.ipynb` (parse it; do not execute it), `session_notes.md`
- **Device card**: `device_card.md`

If a listed input is missing, stop and report — don't reconstruct it.

## Data isolation — strict

Your only inputs are the files above. No repository or notes
directory is an input: do not read `~/sharpelab/measurement-env` or any
other repo path, any prior fusion attempt, draft, or verdict for this
device, any human's read, lean, or reaction to either modality's call, or
any document not in your input list. No web fetches or searches, no email,
chat, or wiki. Public libraries for file parsing and numerics (via
`uv run --with …`) are fine; documents about this device are not.

- If forbidden material reaches you anyway, stop and report the exposure —
  a contaminated fusion is not repaired by ignoring what you saw.
- Your output carries a **provenance line**: what you received, and that
  you saw no prior fusion attempt and no third-party view of either call.

## Output contract

One file, `/data/sharpelab/hera-data/raman-vti-01-fusion-20260824/fusion-verdict.md`:

1. **Per-channel table** — one row per named transport channel (sr1, sr2,
   sr3): transport verdict + strength | Raman verdict + strength + the
   build stage it attaches to | fused verdict + strength word (`weak` /
   `moderate` / `strong`) | the stated basis for the fused row.
2. **Registration** — place the Raman regions and the transport channels
   on one coordinate frame using the frame bridges you actually have, and
   produce the artifact (image + machine-readable form) with the
   registration uncertainty stated against the scale of the features it
   must resolve; where correspondence cannot be established for a channel,
   say so explicitly and bound what that costs the row. Same for the
   timeline: state what build stage each leg's evidence attaches to.
3. **Named hedges** — what limits the fused verdict, each named.
4. **What would settle it** — for every row the two modalities leave
   unresolved or in tension.
5. Plus the provenance line (Data isolation, above).

Archive figures, intermediates, and the scripts that regenerate them under
`/data/sharpelab/hera-data/raman-vti-01-fusion-20260824/` and cite them by
path.
