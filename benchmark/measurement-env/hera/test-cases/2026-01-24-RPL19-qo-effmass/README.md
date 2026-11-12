# Test case: RPL_19 — effective mass + quantum oscillations

Offline HERA replay fixture. Captures a contiguous block of measurements Aaron
ran on RPL_19 (rhombohedral-graphene SC / AHC device on the toploader) during
the 2026-01-24 cooldown, covering anomalous-Hall spot checks, an effective-mass
temperature series, and Landau-fan / quantum-oscillation work. Two frontiers
freeze the campaign at two decision boundaries.

## Source
- Notebook: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/20260124_measure.ipynb`
  (379 cells in source; cropped here to cells 0–190).
- Index synopsis: `hera/docs/notebook-indexes/notebook-index-RPL19.md`
  (2026-01-24 entry).
- Cropped from cell 0, so **fixture cell indices == source cell indices.**

## Frontiers
| Slug | Type | cut_index | next section (answer) | latest_fileid |
|---|---|---|---|---|
| `before-effmass` | DEPTH (quick/deep/paper) | 100 | `# Effective mass` (cell 101) | 1638 |
| `after-qo-confirmed` | CONTESTED (2×2) | 176 | `# Cuts at fixed n and D` (cell 177) | 1776 |

- **`before-effmass`** — cut at the end of `# Preping for effective mass`. The
  experiment class is essentially fixed (a temperature-dependent field-sweep
  series at fixed (n, D) to extract m*); the open question is **depth** — how
  many temperatures, what field range/resolution, how much averaging. Briefs:
  `quick` / `deep` / `paper` on a single directive anchor.
- **`after-qo-confirmed`** — cut at the end of `# Small fan to check if
  oscillations are real`. The oscillations were just confirmed real; **what
  next is genuinely contested** (fixed-(n, D) line cuts to read the QO frequency
  vs. a full effective-mass temperature series vs. broader Landau-fan mapping).
  Briefs: the full 2×2 `open-short` / `open-long` / `directive-short` /
  `directive-long` (depth held = deep).

## Section structure (Aaron's headers, source indices)
| Cells | Header | Sweep family |
|---|---|---|
| 0–40 | `# Init` / `# Configs` | instrument setup, mc_1…mc_27 |
| 41–58 | `# AH Spot Checks` | `mag.field` 1D loops at (0.465, 1.000) |
| 59–71 | `# AH in the normal state` / `## Gatemaps` | `mag.field` loops + (n,D) maps |
| 72–84 | `# Rerun hall map …` / `# Cool back down` | repeat AH maps |
| 81–84 | `# Large AH MAP` | big (n,D) maps in field |
| **85–100** | **`# Preping for effective mass`** | (n,D)-line maps + field fans → **`before-effmass` cut at 100** |
| 101–145 | `# Effective mass` (+ `## Test fan`, `# Zoomed in fan`) | temp-dependent `mag.field` sweeps at (n=1,D=1) |
| 146–172 | `# Resuming effective mass` | longer temp series, higher field range |
| **173–176** | **`# Small fan to check if oscillations are real`** | small Landau fans → **`after-qo-confirmed` cut at 176** |
| 177–184 | `# Cuts at fixed n and D` (+ `## Large series`) | fixed-(n,D) 1D `mag.field` cuts (2001/3001 pt) |
| 185–190 | `# Heating at CSC` (start) | (kept for ground truth; post-cut for both) |

## Layout
- `device_card.md` — RPL_19 device + this-cooldown rig setup.
- `goal.md` — campaign framing.
- `20260124_measure__c0-190.ipynb` — cropped source notebook (outputs preserved).
  The driver re-crops to each frontier's `cut_index` at replay time.
- `data/<file_id>/` — `data/1541`…`data/1776` (236 dirs, ~90 MB), each with
  `metadata.json` + `data.tsv(.gz)` + `plot.png`.
- `cell-to-fileid.md` — cell ↔ file_id map (human aid; not served).
- `frontiers/<slug>.md`, `ground_truth/<slug>/`, `briefs/<slug>/` — per frontier.

## A note on `plot.png` (modality caveat)
Aaron only registers gate-leakage monitors in `s.plot(...)` (`k_bg.curr`,
`k_tg.curr`, `k_si.curr` vs time / Vbg), so **`data/<id>/plot.png` is the
leakage monitor, not the transport data** — for these maps it is essentially
blank (gate currents pinned at 0, i.e. no leakage). The actual transport signal
(the lock-in `sr830_*_X` channels) lives only in `data.tsv(.gz)`. An agent that
wants to *read* the latest sweep must load the TSV; do not penalize it for the
empty PNG. See `ground_truth/<slug>/reading.md`.
