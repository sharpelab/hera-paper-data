# zf1-run1 — recipe followups (for Aaron)

Recipe-layer changes distilled from the zf1-run1 notes
([wiki 8NbxR877nE](https://wiki.sharpelab.science/doc/zf1-run1-8NbxR877nE),
"Revise investigation process flow"). Device-card fixes already landed
(`templates/zf1/device_card.md`); tooling/backlog items tracked separately.
These four are protocol-coupled and shared (Aaron's people read the recipes),
so they wait on Aaron rather than auto-landing.

## B1 — gate green-lighting: corner *direction*, not just corners

`recipes/device-init/gate-range-finding.md` Step 2 already does four-corners,
but holds neither an ordering nor a safe→dangerous direction. Aaron's note:
sweep 0 → ± limits on **both** gates first, then park at the **safe** corner
and sweep **toward** the dangerous corner (e.g. +/+ → +/−). Fold the direction
discipline into Step 2.

## B2 — large gatemap names the capacitance-ratio check

The first survey map has a second job beyond candidate-spotting: a large
gatemap to read the **gate capacitance ratio** (the geometry prior is
uncalibrated — device card flags it). Name that purpose in
`recipes/investigations/sc-characterization.md` Step 1 (and/or `gatemap.md`).

## B3 — zoom into the expected SC region by heuristic (the meaty one)

Aaron: finding the SC "even with a zoom-in map is probably too much unless it
*really* zooms." The fix is to drive the zoom from a heuristic instead of a
blind search:

- Push holes toward the WSe₂ → **negative D** in our convention (device card:
  bilayer above WSe₂).
- Use the rough gate capacitance ratios + a provided **expected SC region and
  extent** to place the zoom window.
- It should **not** need the trapped flux to find the region.

Lands in `sc-characterization.md` Step 1 (candidate ID / coarse→fine). Needs
the expected-region inputs to come from the session brief or device card, not
be hard-coded in the recipe.

## B4 — checkpoint: read the first row or two for railing

Checkpoint guidance should be: look at the **first row or two** of a fresh
sweep for railing before trusting the run. General epistemics — candidate for
`recipes/STYLE.md` or a recipe Verify block; check it isn't already covered by
the TSV-checkpoint guidance before adding.

*(Leave the rest of the process flow untouched — Aaron's call.)*
