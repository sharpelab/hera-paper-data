# Cell ↔ file_id mapping

Mapping from cells in `./20260124_measure__c0-190.ipynb` (fixture indices ==
source indices — the notebook was cropped from cell 0, so they match) to data
directories under `./data/<file_id>/`. Inferred by matching each sweep cell's
function / `slow_param` / `fast_param` / setpoint length+range and chronology
(`start_time`) against the source data dir on
`~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/data/`.

**Notebook file_id range.** The first sweep executed by this notebook is the
AH-spot-check field sweep in cell 42 → **`data/1541`** (`start_time` 2026-01-25
00:16; the 751-/1501-pt `mag.field` sweeps in `data/1510–1540` belong to the
*prior* 2026-01-12 notebook). The fixture pools `data/1541` … `data/1776`
(236 dirs). The `metadata.json` `add_comment` strings are mostly stale
boilerplate (`'MC6, Vsi = 48V, gate map in -100 mT'`) — trust `function` +
`slow_param`/`fast_param` + setpoints, not the comment.

| Cell | Section | Sweep shape | file_id(s) | Notes |
|---|---|---|---|---|
| 42 | AH Spot Checks | `s.sweep(mag.field, linspace(0, 0.1, 101))` at (0.465, 1.000) | 1541 | First sweep of the notebook |
| 43–53 | AH Spot Checks | `s.sweep(mag.field, …)` widening ranges (±0.1 → ±1 T) | 1542–1553 | AH-switching hysteresis loops |
| 55 / 57 | AH in the normal state | loop of `s.sweep(mag.field, ±0.35, 701)` over 17 (n,D) points (two directions each) | 1554–1595 | Many 701-pt ±0.35 T loops |
| 66 / 72 / 81 | Gatemaps / Rerun hall / Large AH MAP | `multisweep([k_tg, k_bg], …)` big (n,D) maps in field (45000-pt) | 1596–1599, 1628–1631 | Normal-state AH maps; 45k-pt (≈201²) gate maps |
| 87 / 89 | Preping for effective mass | `multisweep([k_tg, k_bg], …)` n=0.35–1.35, D=1, 51 pts | 1632, 1633 | 51-pt (n,D)-line maps (→ 102 gate cols) |
| 90 / 98 | Preping for effective mass | `multisweep([k_tg, k_bg], …)` 201 pts, D=1 | 1634, 1636 | 201-pt (n,D)-line maps (→ 402 gate cols) |
| 94 / 99 | Preping for effective mass | `multimegasweep([mag.field], 1.5→0, 151], [k_tg, k_bg], …)` D=1, n 0.35–1.35 | 1635, 1637 | field × (n,D)-line fan, D=1 |
| **100** | **Preping for effective mass** | `multimegasweep([mag.field], 0→1.5, 151], [k_tg, k_bg], …)` **D=0.2, n 0–1.5 (301 pts)** | **1638** | **`before-effmass` latest_fileid** — last real sweep at the cut |
| 105 / 107 / 109 / 112 | Effective mass | `s.sweep(mag.field, 1.5→0, 751)` at fixed (n=1, D=1), repeated after stepping `heater` | 1639–1642 | *(answer for `before-effmass`)* temp-dependent field sweeps |
| 119 / 122 | Test fan / Zoomed in fan | `multimegasweep([mag.field], …], [k_tg, k_bg], …)` small fans | 1644, 1645 | (post-1638) |
| 147–172 | Resuming effective mass | repeated `mag.field` field sweeps at heater temps, then higher-field range | 1646–1773 (range) | long temp series + fans |
| 175 / 176 | Small fan to check if oscillations are real | `multimegasweep([mag.field], 0.9→2.5, 161], [k_tg, k_bg], 0.9→0.5, 151], D=0.2 / D=1` | 1774, 1775, 1776 | small Landau fans; 1774 is a narrow first attempt, 1775/1776 the full D=0.2 / D=1 fans |
| **176** | **Small fan …** | (the D=1 fan) | **1776** | **`after-qo-confirmed` latest_fileid** — last real sweep at the cut |
| 178 / 180 | Cuts at fixed n and D | `s.sweep(mag.field, 3→1 / 1→3, 2001)` at fixed (n, D) | 1777, 1778 | *(answer for `after-qo-confirmed`)* fixed-(n,D) 1D field cuts |
| 183 | Cuts at fixed n and D / Large series | loop `s.sweep(mag.field, 4↔1, 3001)` over 13 densities at D=1 | 1779–1791 (range) | the follow-on density series |

## Notes on the cut sweeps (the two `latest_fileid`s)
- **`before-effmass` → `data/1638`** (cell 100): a `multimegasweep` with
  `mag.field` on the slow axis (0 → 1.5 T, 151 points) and the (Vtg, Vbg) gate
  pair on the fast axis stepping along an (n, D) line at **D = 0.2**, n = 0 → 1.5
  (301 points). I.e. a **density × field map (a Landau fan) at D = 0.2** — the
  last "prep" map taken before the dedicated effective-mass series begins.
- **`after-qo-confirmed` → `data/1776`** (cell 176): a `multimegasweep`,
  `mag.field` 0.9 → 2.5 T (161 pts) slow, (Vtg, Vbg) along n = 0.9 → 0.5 at
  **D = 1** (151 pts) fast — a **small Landau fan** taken specifically to confirm
  the field-periodic oscillations are real (and not noise) before committing to
  the larger fixed-(n, D) cut campaign.

## Ambiguous / pooled cases
- The 17-point AH loops (cells 55/57) and the long "Resuming effective mass"
  temperature series (cells 147–172) produce *many* same-shape file_ids; the
  exact 1:1 cell↔id within those blocks is by chronology and not individually
  pinned here (not needed — both frontier cuts land on cleanly-identified maps).
- `data/1539`, `data/1540` (just below the fixture floor) are the prior
  notebook's tail; the fixture floor is `1541` (cell 42).
