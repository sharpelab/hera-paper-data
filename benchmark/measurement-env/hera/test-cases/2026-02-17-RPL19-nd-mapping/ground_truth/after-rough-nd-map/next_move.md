# Ground truth — next move at the frontier (cut idx 51)

*What the operator (Aaron) actually did in the next section (`# Fine nD map`,
cells 52–55 → `data/1945`). This is **one** expert path used to route the replay
to human review, not an exact-match score. See benchmark-plan.md "Imitation is a
screen, not a score."*

> **Re-grounded 2026-06-08 (Aaron, expert-review card).** Originally written as a
> "coarse→fine refine of the same region" (a depth move). That was a misread.
> Aaron: `data/1945` is *"not a fine map but rather a much larger-area map"* — he
> was *"trying to figure how low I can go in D for this larger-area map,"* and the
> rough map (1944) was his sanity check. The decision is **extend coverage** —
> map the full reachable (n, D) range, especially pushing D down — **not** raise
> resolution on a fixed region. The grid does increase (201×251), but that's
> incidental to the coverage move, not its point.

## The move: `# Fine nD map` — extend the map to the full reachable (n, D) range

Having confirmed the device with the coarse positive-D sliver, the next sweep
**broadens coverage** to the whole reachable landscape:

- The (n, D) polygon is **extended in D**: the new vertices run D from ≈ +1.06
  **down to −0.4 V/nm** (the rough map stopped at +0.70), carrying the map through
  charge neutrality into negative D — *"how low in D can I go for this contact
  config."* n is held to [0.2, 1.8].
- `s.multisweep([k_tg.volt, k_bg.volt], [raster_vtgs, raster_vbgs], delay=0.9)`
  → **`data/1945/`**, on a denser raster (`nx, ny = 201, 251`, oversample flag 1)
  with sensitivity tightened to `5e-3` — i.e. the bigger area is also swept more
  finely, but the *decision* is the coverage extension.
- Followed by a quick trapped-flux check (`mag.field` ±0.5 T, back to 0).

## Why this is the right next step

The rough map (1944) covers only a thin high-D sliver (D ∈ [0.70, 1.065]) — enough
to confirm the device survived the power loss and to see *roughly* where the low-n
structure sits, but it doesn't show the charge-neutrality line or the negative-D /
AHC side at all. Given the goal ("map the (n, D) landscape to localize the SC /
anomalous-Hall region"), the natural move is to **map the full range the gates can
reach in one sweep** — extend D down through 0 to −0.4 — so the whole landscape
(CNP line, positive-D corner, negative-D AHC side) is in view before committing to
finer or feature-targeted work. Finding how low in D the device tolerates is part
of this.

## Class for judging

A clear-answer **coverage** decision (Aaron did not treat it as contested):

- **Same move (expected):** extend the (n, D) map's range — especially in D,
  toward/through 0 into negative D — to cover the full reachable landscape in one
  sweep. Exact D extent, grid, and delay are parameter-level; whether it's also
  finer than the rough map is incidental.
- **Same class, different params:** broaden by another route — a wider (Vtg, Vbg)
  `megasweep` grid over the enlarged box, or extending n as well. Equivalent.
- **Different but reasonable:** a targeted zoom on the low-n/positive-D corner
  *first* (before full-range coverage) is defensible if well-argued, though it
  postpones seeing the rest of the landscape. A pure resolution refine of the same
  thin sliver, with no coverage extension, is weaker — it doesn't address the main
  gap (most of the (n, D) plane is unmapped).
- **Divergent / worse:** jumping to an unrelated axis (field map, Fraunhofer,
  Landau fan, temperature dependence) **before** a full-range (n, D) map exists —
  real later sections of this campaign, but premature here. Also divergent:
  re-running the same coarse sliver unchanged, or abandoning the mapping goal.

## Notes

- The continuation (`after-broaden-map`) is the *next* frontier: the broaden map,
  swept n-first, streaks in the positive-D corner, and the move there is to
  re-sweep **D-first** to clean it up. Don't conflate the two — extending coverage
  (here) and de-streaking the result (next) are different decisions.
- Later sections (`# nD map in field, 1.5T`, `# Frauns`) are the detailed
  follow-ups the full map enables; proposing them here skips the mapping step.
