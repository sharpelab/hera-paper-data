# vti-01 — Raman stacking read brief

*You are a fresh instance producing the Raman stacking call for vti-01. This
brief names the goal, inputs, and isolation rules; the method lives in the
recipe.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
execute the recipe, and write the output files. Analysis only.

## Goal

**Produce the spot-/region-resolved, stage-stamped stacking call for vti-01
(trilayer graphene, ABA vs ABC)** — execute
`~/sharpelab/measurement-env/hera/recipes/investigations/raman-stacking-id.md`
and deliver its Step 6 output contract, with the region-label mask raster
shipped alongside the prose. A "cannot tell" with reasons, or a
mixed-domain read, is a successful outcome; a confident call without
feature-level evidence is a protocol violation.

## Inputs — the complete set

- **Raman data**: `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip` —
  WITec project, supplied by the device owner's group. Everything known
  about acquisition (wavelength, power, objective, grating, dates,
  stage-registered video images) is in-file; Step 0 inventories it.
- **Device facts**: material 3LGr (trilayer per the owner's
  characterization; no independent layer-count map supplied). Dual-gated,
  hBN-encapsulated Hall bar. No other device facts are inputs to this read.
- **Frame bridges** (optical images, GDS): none supplied.
- **Build-stage testimony** (which build step the map(s) were taken at;
  the steps between map and cooldown, with dates):
  none supplied.

If a listed input is missing, say so in the contract and hedge accordingly
(the recipe: data lacking metadata supports at most weak calls) — don't
reconstruct it.

## Data isolation — strict

Your only inputs are the files above plus the corpus:
`~/sharpelab/measurement-env/hera/recipes/`,
`~/sharpelab/measurement-env/hera/models/raman_stacking/`, and the papers
and docs those cite (`hera/docs/papers/`, `hera/docs/raman-public-data.md`).

- **Never read**: any transport result, notebook, session note, or session
  archive for this device; any human's read, lean, or reaction to this
  device's stacking; any prior Raman read of this device; any document
  not in your input list — no other directories under `hera/`, no email,
  chat, or wiki.
- If forbidden material reaches you anyway, stop and report the
  exposure — a contaminated read is not repaired by ignoring what you saw.
- Your output carries a **provenance line**: what you received, and that
  you saw no transport result and no third-party views for this device.

## Arc

1. **Tool gates** — re-run `models/raman_stacking/validate.py` before any
   metric; report the gate tally.
2. **Step 0** — inventory + provenance from in-file metadata (write
   `provenance.md` first, before any spectral analysis).
3. **Recipe Steps 1–5** as written: layer count before stacking; the
   differential two-population read; strain, terrace, and through-stack
   screens; M-band / G-width as quantitative secondaries only; per-spot
   reads with mixed spectra as mixtures.
4. **Verify** — every audit in the recipe's Verify section.
5. **Step 6** — the call, all five parts.

Archive figures, intermediates, and the scripts that regenerate them under
`/data/sharpelab/hera-data/raman-vti-01-read/` and cite them by path.

## Output

Under `/data/sharpelab/hera-data/raman-vti-01-read/`:

- `result.md` — the Step 6 output contract (per-region verdicts on the
  strength scale with stage stamps and stage-frame coordinates; evidence
  list; confidence + named hedges, sub-spot blindness stated; what would
  firm it) plus the provenance line.
- `provenance.md` — Step 0.
- `regions.npz` (+ `regions.png`) — the region-label mask raster in the
  stage µm frame, with the label→verdict key.
- `s*.py` — the scripts that regenerate every figure and metric.
