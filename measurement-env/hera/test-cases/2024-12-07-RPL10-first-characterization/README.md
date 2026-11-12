# Test case: RPL_10 — first-cooldown characterization

Offline HERA replay fixture. Captures the opening of RPL_10's **first cooldown**
(Aaron's rhombohedral-graphene device; top hBN 26 nm, bottom 40 nm, Si global
back gate), from session setup through gate validation, the first (n, D)
transport maps, and into the DC-bias / Fraunhofer characterization. Two frontiers
freeze the campaign at the two early branch points.

## Source

- Notebook: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_10/241207_measure.ipynb`
- Cropped to: cells 0–93 (`241207_measure__c0-93.ipynb`, fixture indices ==
  source indices). Outputs preserved.
- Device's first cooldown ⇒ data file_ids start at 0 (the earliest in the
  device's life). Data dirs 0–18 captured (~6.4 MB).

## Goal

See `goal.md` — get the gates working, map the (n, D) landscape, chase the SC
features.

## Frontiers

| Slug | Type | cut_index | next section (answer) | latest_fileid | #data |
|---|---|---|---|---|---|
| `after-gate-checks` | DEPTH / early | 42 | `# Gatemap` (first (n,D) map) | 8 | 9 (0–8) |
| `after-first-gatemap` | CONTESTED | 54 | DC-bias / Fraunhofer work | 18 | 19 (0–18) |

- **`after-gate-checks`** — cut at the end of `# Gate checks`. Gate-validation
  data exists (data/0–8: not a cold start) but no transport map yet. Depth probe
  (`quick` / `deep` / `paper`) on the directive anchor "do the first (n, D) map":
  tests how the depth level sets a first map's resolution.
- **`after-first-gatemap`** — cut at the end of the first `# Gatemap` section.
  First maps done, candidate SC regions located — what next? DC-bias vs field /
  Fraunhofer vs finer maps vs Si-BG survey. Contested ⇒ full 2×2 brief grid
  (`open/directive × short/long`, depth held = deep).

## Layout

- `goal.md` — campaign framing (blockquote = the goal).
- `device_card.md` — device physical properties + measurement setup wired this
  cooldown (gates incl. Si back gate, DC-bias source, 9× SR830, heater, AMI430
  magnet). First cooldown ⇒ card and data are the same run (no drift).
- `241207_measure__c0-93.ipynb` — cropped source notebook (cells 0–93).
- `data/<file_id>/` — sweep outputs (TSV + metadata.json + plot.png), ids 0–18.
- `cell-to-fileid.md` — cell ↔ file_id map (human aid; not served).
- `frontiers/<slug>.md` — the two frontier contracts.
- `ground_truth/<slug>/{next_move,reading}.md` — per-frontier expert path +
  perception read.
- `briefs/<slug>/` — depth probe (after-gate-checks) and 2×2 (after-first-gatemap).

## Notable data-quality gotchas (carried in the readings)

- The gate-map `plot.png`s show only the **live gate-leakage monitor**, not a
  transport colormap — the (Vbg, Vtg) transport is in the run TSVs (`sr830_4` =
  current channel). See `ground_truth/after-first-gatemap/reading.md`.
- The first gate maps are **partial / interrupted** (data/18 ≈ 16 of 201 slow
  lines; earlier ones shorter) — first-look rasters, not finished phase maps.

## Section structure (source headers, cells 17–93)

| Cells | Header | Family |
|---|---|---|
| 17–20 | `# Configs` | mc_1, validators |
| 21–42 | `# Gate checks` (Initial / Top gate 26 nm / Bottom Gate 40 nm) | 1D gate sweeps |
| 43–54 | `# Gatemap` | 2D (Vbg, Vtg) maps × V_Si |
| 55–59 | `# Changing config to do quick DC` | DC-bias 1D (post-cut) |
| 60–77 | gate-map returns / config changes / Si-BG testing | (post-cut) |
| 78–93 | `# Fraunhofer check` / `# Real Fraunhofer now` | field × bias (post-cut) |
