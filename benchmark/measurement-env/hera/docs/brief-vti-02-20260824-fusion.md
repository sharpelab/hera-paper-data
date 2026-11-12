# vti-02 — Raman×transport fusion brief (2026-08-24 session)

*You are a fresh instance producing the fused stacking verdict for vti-02.
This brief names the goal, the inputs, the output contract, and the isolation
rules; the fusion method is yours to derive from them.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
derive and execute your own fusion analysis, and write one output file plus
its artifacts. Analysis only.

## Goal

**Produce the fused, region-resolved stacking verdict for vti-02** from the
transport contract and the Raman document below. A fused "cannot tell" or a
well-evidenced disagreement is a successful outcome; forcing concordance is
a protocol violation.

## Inputs — the complete set

All under `/data/sharpelab/hera-data/raman-vti-02-20260824-fusion/inputs/`:

- **Transport contract** (locked stacking call): `transport-call.md`.
- **Raman document**: `raman.md` — the device group's own Raman record,
  written by a human. This is the Raman leg in full: there is no raw map,
  no spectra, and no independent instrument Raman read for this device.
  Assess what it does and does not carry (evidence, positions, stage,
  acquisition facts) and weigh it accordingly — do not reconstruct missing
  evidence. The document's own verdict wording is an input to be assessed,
  not a conclusion to be inherited.
- **Frame bridges** beyond what `raman.md` itself contains (optical
  images, GDS, build-step list): none supplied. The parent-flake URL in
  `raman.md` is not an input — do not fetch it.
- **Ana notebook + session notes** backing the transport call:
  `20260824_ana.ipynb` (parse it; do not execute it), `session_notes.md`
- **Device card**: `device_card.md`

If a listed input is missing, stop and report — don't reconstruct it.

## Data isolation — strict

Your only inputs are the files above. No repository or notes
directory is an input: do not read `~/sharpelab/measurement-env` or any
other repo path, any prior fusion attempt, draft, or verdict for this
device, any human's read, lean, or reaction to either modality's call, or
any document not in your input list. No web fetches or searches, no email,
chat, or wiki.

- If forbidden material reaches you anyway, stop and report the exposure —
  a contaminated fusion is not repaired by ignoring what you saw.
- Your output carries a **provenance line**: what you received, and that
  you saw no prior fusion attempt and no third-party view of either call.

## Output contract

One file, `/data/sharpelab/hera-data/raman-vti-02-20260824-fusion/fusion-verdict.md`:

1. **Per-channel table** — one row per named transport channel (here the
   single wired pair, sr1 = B_1–B_2): transport verdict + strength |
   Raman verdict + strength + the build stage it attaches to | fused
   verdict + strength word (`weak` / `moderate` / `strong`) | the stated
   basis for the fused row.
2. **Spatial/temporal correspondence** — state, with the evidence the
   inputs actually give, whether the Raman evidence and the transport
   channel can be placed on one coordinate frame and one timeline; where
   they cannot, say so explicitly and bound what that costs the fusion.
3. **Named hedges** — what limits the fused verdict, each named.
4. **What would settle it** — for every row the two modalities leave
   unresolved or in tension.
5. Plus the provenance line (Data isolation, above).

Archive figures, intermediates, and the scripts that regenerate them under
`/data/sharpelab/hera-data/raman-vti-02-20260824-fusion/` and cite them by
path.
