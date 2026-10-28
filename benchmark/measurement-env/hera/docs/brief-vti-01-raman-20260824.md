# vti-01 — Raman stacking read brief (2026-08-24)

*You are a fresh instance producing the Raman stacking call for vti-01. This
brief names the goal, the inputs, the output contract, and the isolation
rules; the analysis method is yours to derive from them.*

## Contract — offline analysis

No rig, no live notebook, no autonomy machinery. You read the inputs below,
derive and execute your own spectral analysis, and write the output files.
Analysis only.

## Goal

**Produce the spot-/region-resolved, stage-stamped stacking call for vti-01
(trilayer graphene, ABA vs ABC)** from the Raman data below. A "cannot tell"
with reasons, or a mixed-domain read, is a successful outcome; a confident
call without feature-level evidence is a protocol violation.

## Inputs — the complete set

- **Raman data**: `/data/sharpelab/hera-data/raman-vti-01/vti-01.wip` —
  WITec project, supplied by the device owner's group. Everything known
  about acquisition (wavelength, power, objective, grating, dates,
  stage-registered video images) is in-file.
- **Device facts**: material 3LGr (trilayer per the owner's
  characterization; no independent layer-count map supplied). Dual-gated,
  hBN-encapsulated Hall bar. No other device facts are inputs to this read.
- **Frame bridges** (optical images, GDS): none supplied.
- **Build-stage testimony** (which build step the map(s) were taken at;
  the steps between map and cooldown, with dates): none supplied.

If a listed input is missing, say so in the output and hedge accordingly —
don't reconstruct it.

## Data isolation — strict

Your only inputs are the files above. No repository or notes
directory is an input: do not read `~/sharpelab/measurement-env` or any
other repo path, any transport result, notebook, session note, or session
archive for this device, any human's read, lean, or reaction to this
device's stacking, or any prior Raman read of this device. No web fetches
or searches, no email, chat, or wiki. Public libraries for file parsing and
numerics (via `uv run --with …`) are fine; documents about this device are
not.

- If forbidden material reaches you anyway, stop and report the exposure.
- Your output carries a **provenance line**: what you received, and that
  you saw no transport result and no third-party views for this device.

## Output contract

Under `/data/sharpelab/hera-data/raman-vti-01-read-20260824/`:

- `provenance.md` — written **first, before any spectral analysis**: an
  inventory of the project file and every acquisition fact it carries.
- `result.md` — the call:
  1. **Per-spot/per-region verdict**, each with a strength word
     (`decisive` / `strong` / `weak` / `consistent-with` /
     `uninformative`), its stage stamp, and its coordinates in the stage
     µm frame: `region R (x,y µm, stage S): ⟨verdict⟩ (⟨strength⟩)`.
  2. **Evidence list** — metric values with their spectral coordinates,
     and what in the maps/spectra each verdict rests on.
  3. **Confidence + named hedges** — what limits each verdict, each named.
  4. **What would firm it.**
  5. A reasoned "cannot tell" (with the missing metadata or coverage
     named) is a successful outcome.
  Plus the provenance line (Data isolation, above).
- `regions.npz` (+ `regions.png`) — the region-label mask raster in the
  stage µm frame, with the label→verdict key (ship the raster alongside
  the prose coordinates).
- `s*.py` — the scripts that regenerate every figure and metric; archive
  figures and intermediates in the same dir and cite them by path.
