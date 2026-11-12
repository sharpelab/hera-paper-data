---
slug: after-broaden-map
user: aaron
cut_index: 57
latest_fileid: 1945
included:
  data: [1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945]
  images: []
leak_terms:
  - "sweeping D first"
  - "to reduce streaks"
  - "Rough fan"
forward_scan: "kept region (cells 0-57) greped for forward references (streak / 'D first' / 'Rough fan' / fan / Fraun / next). The n-first maps in the kept region (rough 1944 cell 51, broaden 1945 cell 55) and the trapped-flux field check (cells 56-57) carry no forward reference to the D-first re-sweep. Section headers present in the kept region are all pre-cut: `# rough nD map at positive D` (48), `# Fine nD map` (52). The post-cut `# Rough fan, sweeping D first, then n to reduce streaks` (58) is dropped. Clean."
---

# Frontier — cut at end of `# Fine nD map` (the broaden map + flux check)

*Defines the decision boundary at which this fixture freezes the RPL_19
2026-02-17 campaign for offline replay. The YAML frontmatter above is the
machine-readable contract the `hera-replay` driver reads; the prose below is for
humans. This is the **second** frontier in this campaign (the continuation of
`after-rough-nd-map`); one notebook carries both. This is a **DATA-QUALITY /
METHOD** decision frontier — the experiment ("map this (n,D) region") is held
fixed and the question is how to fix a sweep artifact. Added 2026-06-08.*

## The frontmatter contract

- **`cut_index` (57)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..57`; everything after is the answer key. (Fixture indices == source
  indices; the stored notebook was cropped from 0.)
- **`latest_fileid` (1945)** — the **broaden map** (cell 55): the large-area,
  n-first (n,D) raster that extends D down to −0.4 V/nm. This is the freshest
  *data* at the cut; cells 56–57 are a trapped-flux field check that lands no
  sweep. The agent is pointed here as "the most recent result." See
  `../ground_truth/after-broaden-map/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: the six post-power-loss gate checks
  (1938–1943), the rough map (1944), and the broaden map (1945). Authoritative;
  adding the post-cut D-first re-map (1946+) would be the leak.
- **`included.images`** — empty. Every sweep cell embeds only the live
  gate-leakage monitor PNG, not a transport heatmap; the (n,D) maps live in the
  TSVs. See `reading.md`.
- **`leak_terms`** — post-cut-only tripwires, each verified by cell index in the
  c0-65 crop: `sweeping D first` (cells 58, 63), `to reduce streaks` (cell 58),
  `Rough fan` (cell 58) — all > 57, and all naming the D-first answer. The
  broaden-map terms (`Fine nD map`, `251, 251`, `rev_y=False`, `-0.4`) sit at
  cells 52/53 and are therefore *inside* the agent's view at this cut — they are
  not tripwires here (they were the previous frontier's answer signature).
- **`forward_scan`** — human attestation that the kept markdown/comments carry
  no forward reference to the D-first re-sweep.

## Cut

- **Cut index 57** sits on a **section boundary** once the trailing field check
  is included: cell 55 is the broaden-map sweep (→ `data/1945`), cells 56–57 are
  `s.ramp(mag.field, ±0.5)` / `s.ramp(mag.field, 0)` (a trapped-flux check, no
  data). Cell 58 is the `# Rough fan, sweeping D first, then n to reduce streaks`
  markdown header — the first cell of the next experiment, which is what HERA
  must predict.
- **No mid-section header leak.** Truncating at 57 keeps the legitimate
  `# Fine nD map` header (cell 52) and drops the D-first header (cell 58).

## What's live at the cut

The post-power-loss mapping phase has, in order:

1. `# Checks after power loss` (cells 39–47) — 1D gate sweeps confirming the
   device survived (no leakage). → `data/1938–1943`.
2. `# rough nD map at positive D` (cells 48–51) — a coarse n-first raster over a
   thin high-D sliver (`n ∈ [0.2, 2.0]`, `D ∈ [0.70, 1.065]`, 101×101).
   → `data/1944` (the previous frontier's cut).
3. `# Fine nD map` (cells 52–55) — the **broaden map**: an n-first raster that
   extends coverage down to `D = −0.4` V/nm at 201×251. → `data/1945` (the
   latest sweep at *this* cut).
4. A trapped-flux field check (cells 56–57): `mag.field` ramped to ±0.5 T and
   back to 0.

**Latest landed sweep: `data/1945/`.** State at the cut: gates parked to 0,
Vsi = 48 V context, field returned to the trapped-flux null, base T (~28–30 mK).
The broaden map is in hand — but, swept n-first, it **streaks along the fast
axis in the high-Rxx positive-D corner** (see `reading.md`).

## The decision being tested

*"The full-range (n,D) map is in hand, but it streaks. What next?"* The
expert-correct move is **not** a new experiment — it is to recognize the
fast-axis streaking as a sweep-ordering artifact and **re-map the same region
with D as the fast axis** ("sweeping D first … to reduce streaks", → `data/1946`),
taking a forward/reverse pair (`data/1947`) to separate true hysteresis from
sweep-direction artifacts, before committing to the fine D-first full map
(`data/1948`). This tests **artifact awareness**, a skill distinct from the
"what experiment next" decisions elsewhere in the suite. See
`../ground_truth/after-broaden-map/next_move.md`.

## Caveats carried into the cut

- **Degraded input (v0).** No live kernel, no operator screen observations, and
  deliberately **no `live_notes.md`**: the streaking is legible in the landed
  `data/1945` TSV (re-formed as `Rxx(n,D)`), so the decision class ("fix the
  streaks by re-sweeping D-first") does not hinge on an unrecorded live fact.
- **The streak read requires re-forming Rxx.** As with the rough map, the
  on-disk `data/1945/plot.png` is only the gate-leakage monitor; the streaks
  live in `Rxx = sr830_{1,2,3}_X / sr830_4_X` reconstructed from the TSV.
  Reconstructing it is the expected sub-step — flag, don't penalize.
