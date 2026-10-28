---
slug: after-rough-nd-map
user: aaron
cut_index: 51
latest_fileid: 1944
included:
  data: [1938, 1939, 1940, 1941, 1942, 1943, 1944]
  images: []
leak_terms:
  - "Fine nD map"
  - "251, 251"
  - "rev_y=False"
forward_scan: "kept region is cells 0-51 (Init / Configs / Checks after power loss / rough nD map at positive D). Grepped markdown + comments for forward references (fine, fan, Fraun, focus, hysteresis, next, later, TODO): the only 'next' hits are loop variables `v_next`/`i_next` in the cell-23 DC-source ramp helper (not a forward reference); no forward-looking markdown or comments. Section headers present in the kept region are all pre-cut (Init, Magnet, SRS, Keithley, Thermometry, Agilents, DC205 and Yokos, Custom functions, Configs, Checks after power loss, rough nD map at positive D). Clean."
---

# Frontier — cut at end of `# rough nD map at positive D`

*Defines the decision boundary at which this fixture freezes the campaign for
offline replay. The YAML frontmatter above is the machine-readable contract the
`hera-replay` driver reads; the prose below is for humans. This is a **COVERAGE**
decision frontier — given a coarse recon map of a thin slice, the move is to
**extend the map to the full reachable (n, D) range**. It is the first of two
frontiers this campaign carries (`after-broaden-map` is the continuation). Added
2026-06-01; re-grounded 2026-06-08.*

> **Re-grounded 2026-06-08 (Aaron).** This was originally filed as a DEPTH /
> "coarse→fine refine" frontier. That was a misread: Aaron's actual next move
> (`data/1945`) is a **larger-area map** that extends the D range down to −0.4
> V/nm ("how low in D can I go") to capture the full reachable landscape — **not**
> a higher-resolution refine of the same region, and the rough map (1944) was his
> sanity check, so this is a clear-answer coverage decision, not a depth/rigor
> contest. The prose, briefs, and ground truth below reflect the corrected
> framing; the frontmatter contract (cut, allowlist, leak terms) was already
> mechanically valid and is unchanged.

## The frontmatter contract

- **`cut_index` (51)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..51`; everything after is the answer key. (Fixture indices == source
  indices, since the stored notebook was cropped from 0.)
- **`latest_fileid` (1944)** — the rough nD map sweep (cell 51); the agent is
  pointed here as "the most recent result." See
  `../ground_truth/after-rough-nd-map/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: the six post-power-loss gate-check sweeps
  (1938–1943) plus the rough nD map (1944). Authoritative; adding the post-cut
  broaden-map id (1945) would be the leak.
- **`leak_terms`** — post-cut-only tripwires (see below).
- **`forward_scan`** — human attestation that the kept markdown/comments carry no
  forward references.

## Cut

- **Cut index 51** sits on a **section boundary**: cell 51 is the last cell of
  `# rough nD map at positive D` (the coarse `multisweep` raster → `data/1944/`,
  followed by parking the gates to 0). Cell 52 is the `# Fine nD map` markdown
  header — the first cell of the *next* section (the broaden map, despite the
  "Fine" label), which is what HERA must predict.
- **No mid-section header leak.** Truncating at 51 keeps the legitimate
  `# rough nD map at positive D` header (cell 48) and drops `# Fine nD map`
  (cell 52). No later headers survive.

## Leak terms (all verified post-cut-only)

Verified with `nb grep <notebook> -i <term>`; every match is at a cell index
> 51:

- **`Fine nD map`** — the next-section header (cells 52 and 209); the broaden map
  carries this (mislabeled) "Fine" header. The thing being predicted.
- **`251, 251`** — the broaden map's grid `nx, ny = 251, 251` (cell 53 only; note
  the served crop renders it as 201×251 in analysis — the served notebook string
  is `251, 251`). The rough map at the cut uses `nx, ny = 101, 101`. (The bare
  string `251` *does* appear pre-cut in the 251-point 1D gate checks of cells
  44–46 — so the tripwire is the full `251, 251` token, post-cut-only.)
- **`rev_y=False`** — the broaden map's oversampled raster call
  `raster.rasterize(verts, nx, ny, 1, rev_x=False, rev_y=False)` (cells ≥ 53).
  The rough map at the cut uses `..., 0, rev_x=False, rev_y=True`, so `rev_y=False`
  is a post-cut signature here.

Note on **`mag.field`**: deliberately *not* a leak term here. It appears in the
kept region (instrument setup cells 9/29/34/38, and a benign `s.ramp(mag.field, 0)`
in the rough-map cell 51 itself), so it is pre-cut capability, not an answer
signature — using it as a tripwire would false-positive.

## What's live at the cut

Post-power-loss session for an established RPL_19 cooldown:

1. `# Init` / `# Configs` (cells 0–38) — instruments instantiated (8× SR830 +
   1× SR860, three Keithley gates incl. Si back gate, DC205 bias sources, the
   superconducting magnet, thermometry), `mc_1…mc_32` defined, custom (n,D)
   helpers.
2. `# Checks after power loss` (cells 39–47) — 1D gate sweeps (k_si 0→48, k_bg
   and k_tg across their validators) confirming the device survived the power
   loss; gate currents flat (no leakage). → `data/1938–1943/`.
3. `# rough nD map at positive D` (cells 48–51) — a **coarse** rasterized
   `multisweep` over a polygon in (n, D) at positive D (`nx, ny = 101, 101`,
   `delay=1`, lock-in sensitivity `20e-3`), `mc_31`, Vsi = 48 V, base T.
   → `data/1944/` (the latest landed sweep).

State at the cut: gates parked to 0 after the map, Si gate at 48 V context,
nominally zero field, base temperature (~28–30 mK).

## Caveats carried into the cut

- **Coarse-map plotting limitation.** `data/1944/plot.png` shows only the
  gate-leakage monitor panels (flat); the (n, D) transport structure must be read
  from the TSV. Faithful to the live view — see `reading.md`.
- **Degraded input (v0).** No live kernel, no operator screen observations, and
  deliberately **no `live_notes.md`**: the next decision (extend the map's D range
  to cover the full reachable landscape) does not hinge on an unrecorded live
  fact — only the exact D extent / grid is parameter-level, which per the locked
  principle is not a reason to add live notes.
