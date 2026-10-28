# Ground truth — next move at the frontier (cut idx 57)

*What the operator (Aaron) actually did in the next section (`# Rough fan,
sweeping D first, then n to reduce streaks`, cells 58–65 → `data/1946–1948`).
This is **one** expert path used to route the replay to human review, not an
exact-match score. See benchmark-plan.md "Imitation is a screen, not a score."*

> **Grounded 2026-06-08** against the source measure notebook
> (`20260217_measure.ipynb`, cells 58–65) and a re-render of Aaron's own
> `Rxx = sr830_{1,2,3}_X / sr830_4_X` pipeline on `data/1945` (n-first) vs
> `data/1946` (D-first). The streak-vs-clean contrast is visible in
> `../after-broaden-map/figures/ana_1945_broaden-map-nfirst_streaky.png` and
> `ana_1946_dfirst-rough_destreaked.png`.

## The move: re-sweep the map **D-first** to kill the fast-axis streaks

The broaden map (`data/1945`) was rastered **n-first** (gates stepped along the
density axis as the fast variable). In the high-Rxx positive-D corner this
produces pronounced **fast-axis streaking** — bright vertical/diagonal bands
that smear the feature structure. Aaron's next move was a methodological fix, not
a new experiment:

1. **`# Rough fan, sweeping D first, then n to reduce streaks`** (cell 59/60) —
   re-raster the same landscape with **D as the fast axis**, coarse (101×101),
   `rev_x=False, rev_y=False` → **`data/1946`**. The header states the intent
   verbatim: *sweeping D first … to reduce streaks.*
2. **Forward/reverse pair** (cell 61/62) — immediately repeat with the D sweep
   reversed (`rev_y=True`) → **`data/1947`**, to separate genuine hysteresis from
   sweep-direction artifacts.
3. **`# Fine nD, sweeping D first`** (cell 64/65) — having confirmed D-first is
   cleaner, commit to the **fine** D-first map (201×251), extended to D = −0.4
   → **`data/1948`**. This is the clean, publication-oriented version of the
   full-range map.

The re-rendered `data/1946` (D-first) resolves clean, continuous constant-D
feature lines in the positive-D corner that the n-first `data/1945` smears into
streaks — confirming the artifact was sweep-ordering, not physics.

## Why this is the right next step

The map already covers the right region; the limiting factor is **data quality**,
not coverage or resolution per se. A high-Rxx region swept fast-axis-first
charges/settles the RC of the gate line unevenly between adjacent fast-axis
points, leaving streaks aligned with the fast axis. Swapping the fast axis (D
instead of n) re-orients — and largely removes — the artifact, and a
forward/reverse pair distinguishes any residual hysteresis from direction
artifacts. Recognizing this *before* over-interpreting the streaky map, or before
piling on more averaging/finer grids that would not fix a direction artifact, is
the expert instinct being tested.

## Class for judging

This is a **data-quality / method** frontier. Judge on whether the agent
diagnoses the streaks as a sweep-ordering artifact and proposes a fix that could
actually work:

- **Same move (expected):** re-map the same region with the **fast/slow axes
  swapped** (D-first), ideally with a forward/reverse pair to check hysteresis.
  Exact grid / delay / whether it commits straight to the fine version is
  parameter-level.
- **Same class, different params:** other legitimate de-streaking fixes —
  increasing the inter-point `delay` (longer RC settle) on the fast axis,
  reducing fast-axis step size, or adding a settle/forward-reverse averaging
  pass. Reviewer may rate these equivalent-or-better, *provided* the agent has
  correctly identified the streaks as a settling/direction artifact.
- **Different but reasonable:** flag the streaks and re-take the corner as a
  small zoomed re-sweep, or switch from `multisweep` raster to a regular
  `megasweep` grid with a slower fast axis. Defensible.
- **Divergent / worse:** treating the streaks as real physics; moving on to a
  new experiment (Fraunhofer, fan, temperature dependence) on top of the streaky
  map without addressing data quality; or "fixing" it with a finer grid /
  heavier averaging at the *same* sweep ordering (does not remove a direction
  artifact). Re-running the identical n-first map unchanged is also a non-answer.

## Notes

- The downstream chain (`data/1948` fine D-first → `data/1949` map at 1.5 T →
  `# Frauns` at cell 71) is the continuation *after* this fix; proposing the
  Fraunhofer/field characterization here is premature — the agent is still inside
  the mapping phase, cleaning the map before reading physics off it. (The
  gatemap→Fraunhofer decision is covered by the `2025-11-03-RPL19-sc-dome-
  fraunhofer` fixture.)
- The "fan" in the section title is Aaron's shorthand for the raster, not a
  Landau fan; no field axis is involved in `data/1946–1948`.
