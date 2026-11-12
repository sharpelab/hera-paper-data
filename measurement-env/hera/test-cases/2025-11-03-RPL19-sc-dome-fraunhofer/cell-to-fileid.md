# Cell ↔ file_id mapping

Mapping from cells in `./20251103_measure__c0-84.ipynb` to data directories
under `./data/<file_id>/`. Fixture cell indices == source indices (cropped from
cell 0). Inferred by sweep function/shape + chronology against the source data
dir `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/data/`, matching each
sweep cell's `add_comment` / function / params against `data/<id>/metadata.json`
`start_time`.

The 2025-11-03 notebook's first sweep is **file_id 130** (start_time
2025-11-03 22:14); file_ids ≤ 129 are from the prior (Oct 2025) cooldown. The
SC-gatemap section (cells 63–83) ends at **file_id 145**; the `# Fraunhofer`
answer begins at file_id 146 (post-cut, **not** in this fixture).

| Cell | Section | Sweep shape | file_id(s) | Notes |
|---|---|---|---|---|
| 54/55 | Gate checks · Top gate | `s.sweep(k_tg.volt, linspace(0,1,101))` | 130, 131 | top-gate responsiveness, nplc 10 then 1 |
| 60/61 | Gate checks · Backgate | `s.sweep(k_bg.volt, …)` | 132, 133 | back-gate responsiveness |
| 64 | Gatemap of SC | `s.megasweep(k_tg.volt, linspace(0,1,201), k_bg.volt, linspace(-7,-3,401))` | 134 | first (Vtg,Vbg) SC gate map, MC3/MC4, V_Si=−48 |
| (70) | Gatemap of SC | `s.ramp(mag.field, 0.00)` | 135 | ramp/park artifact (metadata function=None, no plot.png) |
| 71 | Gatemap of SC | `s.multimegasweep([mag.field], [linspace(0,0.005,21)], [k_tg,k_bg], [ys,xs])` | 136, 137 | gate-line × small field (0–5 mT); two passes |
| 72–75 | Gatemap of SC | `s.multisweep([k_tg.volt, k_bg.volt], [ys, xs])` | 138, 139, 140, 141 | gate-line cuts through the dome |
| 77 | Gatemap of SC | three `s.sweep(mag.field, …)` 1D field sweeps (0→10, 10→−10, −10→0 mT) | 142, 143, 144 | "trying to sweep field instead" — 1D field response of the dome point |
| 83 | Gatemap of SC | `s.multimegasweep([mag.field], [linspace(0,0.020,201)], [k_tg,k_bg], [ys,xs])` | **145** | **latest_fileid** — gate-line × field 0→20 mT (interrupted ~11.6 mT) |
| 87 | Fraunhofer (POST-CUT) | `s.sweep(dc205_1.volt, linspace(-2.5,2.5,101))` | 146 | (not in fixture) Ic at zero field |
| 100 | Fraunhofer (POST-CUT) | `megasweep(mag.field, …, dc205_1.volt, …)` | 150 | (not in fixture) 2D field × bias map |

## Allowlist

`included.data = [130 … 145]` (16 dirs) — all sweeps in
`[notebook_first_id=130, latest_fileid=145]`. file_id 135 has no `plot.png` (an
interrupted/ramp artifact); kept for completeness, harmless.

## Notes / ambiguities

- **All sweep cells embed only the gate-leakage live-monitor PNG** (output index
  203 of 206; `s.plot(k_bg.volt, k_bg.curr)` etc.) — *not* a transport heatmap.
  `data/<id>/plot.png` is the same leakage plot. Transport (`sr830_*_X`) is in the
  TSVs. So `included.images = []` (nothing useful to extract).
- The gate-line helper `draw_line_through_point((-5.2, 0.47), slope=0.3)` (cells
  65/79) defines the (Vbg, Vtg) line through the SC dome optimum used by the
  multisweep/multimegasweep cells.
- file_ids 136/137 both match cell 71's shape (21-pt field × gate line) — two
  passes; 142–144 are cell 77's three 1D field sweeps.
