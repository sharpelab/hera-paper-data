# vti-02 — Raman×transport fusion brief

*You are a fresh instance producing the fused stacking verdict for vti-02.
This brief names the goal, inputs, and isolation rules; the method lives in
the recipe.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
execute the fusion recipe, and write one output file plus its artifacts.
Analysis only.

## Goal

**Produce the fused, region-resolved stacking verdict for vti-02** — execute
`~/sharpelab/measurement-env/hera/recipes/investigations/stacking-raman-transport-fusion.md`
and deliver its Step 5 output contract. A fused "cannot tell" or a
well-evidenced disagreement is a successful outcome; forcing concordance is
a protocol violation.

## Inputs — the complete set

All under `/data/sharpelab/hera-data/raman-vti-02-fusion/inputs/`:

- **Transport contract** (locked stacking call, tetralayer Step 7):
  `transport-call.md`
- **Raman document**: `raman.md` — the device group's own Raman record,
  written by a human. This is the Raman leg in full: there is no raw map,
  no spectra, and no independent HERA Raman read for this device. Treat
  it as the Raman contract and run recipe Step 1 on it as written: it
  either carries the weight words, evidence, positions, and stage stamp
  the recipe requires, or it is not fusible on those axes. Where it
  falls short, say exactly which axis fails and degrade the fusion
  accordingly (consistency narrative, uncovered rows) — do not
  reconstruct the missing evidence. The document's own verdict wording
  is an input to be assessed, not a conclusion to be inherited.
- **Frame bridges** beyond what `raman.md` itself contains (optical
  images, GDS, build-step list): none supplied. The parent-flake URL in
  `raman.md` is not an input — do not fetch it.
- **Ana notebook + session notes** backing the transport call:
  `20260821_ana.ipynb`, `session_notes.md`
- **Device card**: `device_card.md`

If a listed input is missing, stop and report — don't reconstruct it.

## Data isolation — strict

Your only inputs are the files above plus the corpus:
`~/sharpelab/measurement-env/hera/recipes/`,
`~/sharpelab/measurement-env/hera/models/`, and the papers and docs they
cite (`hera/docs/papers/`, `hera/docs/raman-public-data.md`).

- **Never read**: any prior fusion attempt, draft, or verdict for this
  device; any document not in your input list — no other directories
  under `hera/`, no session archives, no email, chat, or wiki.
- `raman.md` is a human-authored document and may carry its author's
  lean. That is the Raman leg's verdict, admitted by this brief; it is
  not a view on the transport call, and nothing in it about transport or
  about this device's stacking beyond the Raman evidence is an input.
- If other forbidden material reaches you anyway, stop and report the
  exposure — a contaminated fusion is not repaired by ignoring what you saw.
- Your output carries a **provenance line**: what you received, and that
  you saw no prior fusion attempt and no third-party view of the
  transport call.

## Arc

1. **Admissibility + independence** (recipe Step 1 and the independence
   audit) — these gate everything downstream; expect the Raman leg to be
   the binding constraint.
2. **Recipe Steps 2–5** as written. The registration artifact (Step 2) is
   binding — produce it from the frame bridges you actually have (the
   device card's contact map, the ana notebook's geometry, whatever
   positions `raman.md` gives), and state the registration uncertainty
   against the domain scale. Where coverage cannot be established, the
   row is uncovered — no interpolation.
3. **Verify** — all four audits.

Archive figures, intermediates, and the scripts that regenerate them under
`/data/sharpelab/hera-data/raman-vti-02-fusion/` and cite them by path.

## Output

One file, `/data/sharpelab/hera-data/raman-vti-02-fusion/fusion-verdict.md`:
the Step 5 output contract (the Step 4 table over the wired channel —
sr1 (B_1–B_2) — and any region `raman.md` resolves, per-region verdicts
on the strength scale, the registration-artifact pointer, named hedges,
what-would-settle for every unreconciled row) plus the provenance line.
