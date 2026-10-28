# Cell ↔ file_id mapping

Mapping from cells in `./20260415_measure__c243-299.ipynb` to data
directories under `./data/<file_id>/`. Inferred by sweep-shape and
chronology against the source data dir on
`~/sharpelab/dgglab-measurements/toploader/Isaac/b1c2_toploader/data/`.

Confirm against the cell's text + the `metadata.json`'s `function`,
`slow_params`, `fast_params`, and `start_time` fields if any mapping
looks off.

| Cell | Section | Sweep shape | file_id(s) | Notes |
|---|---|---|---|---|
| 254 | nT map at Beff = 0 | `multisweep([k_tg, k_bg], [vtg_vec, vbg_vec], delay=1.2)` | 75 | First gatemap of this section, before nT scans |
| 255 | nT map at Beff = 0 | `multimegasweep([heater], np.linspace(0, 7, 71), [k_tg, k_bg], …)` | 76 or 77 | nT, heater 0→7 V, 71 steps |
| 260 | nT map at Beff = 0 | `multimegasweep([heater], np.linspace(6.5, 3, 36), [k_tg, k_bg], …)` | 79 | nT, heater 6.5→3 V, 36 steps |
| 261 | nT map at Beff = 0 | `multimegasweep([heater], np.linspace(3, 0, 16), [k_tg, k_bg], …)` | 80 | nT, heater 3→0 V, 16 steps |
| 269 | Idc vs T | `megasweep(heater, np.linspace(6.5, 3, 36), dc205_1, np.linspace(-15…))` | 81 or 82 | 36 heater setpoints |
| 270 | Idc vs T | `megasweep(heater, np.linspace(3, 0, 16), dc205_1, np.linspace(-15, …))` | 83 | 16 heater setpoints |
| 274 | Idc vs n | `multimegasweep([k_tg, k_bg], [vtg_vec, vbg_vec], [dc205_1.volt], …)` | 84 | (Vtg, Vbg) × dc205 |
| 282 | B vs Idc | `megasweep(mag.field, np.linspace(-0.012, -0.002, 51), dc205_1, np.linspace(…))` | 85 | 51 field setpoints |
| 289 | find 90 degrees theta | `s.sweep(k_tg2.volt, np.linspace(0, 0.1, 2001), delay=1)` | one of 86/87/89/90 | 2001-pt 1D sweep of k_tg2 |
| 292 | find 90 degrees theta | `s.sweep(mag.field, np.linspace(-0.0075, -0.006, 51), delay=2)` | 88 | 51-pt 1D sweep |
| 294 | find 90 degrees theta | `s.sweep(k_tg2.volt, np.linspace(0, 0.1, 2001), delay=1)` | one of 86/87/89/90 | 2001-pt |
| 299 | find 90 degrees theta | `s.sweep(k_tg2.volt, np.linspace(0, 0.1, 2001), delay=1)` | one of 86/87/89/90 | 2001-pt |

## Ana-side ↔ data_id mapping

The ana notebook (`./20260415_ana__c0-6_60-89.ipynb`) reaches into the same
data dirs to plot/process. Reverse mapping (data_id → ana cell):

**Cell numbers below are the *source* notebook indices** (`20260415_ana.ipynb`
on the toploader, 183 cells). In the cropped fixture notebook the same cells
appear shifted: setup 0–6 maps 1:1, gap-marker md cell sits at index 7,
source cells 60–89 land at fixture indices 8–37.

| data_id | Measure cell (src) | Ana cell(s) (src) | What the ana cell does |
|---|---|---|---|
| 75 | 254 (gatemap, 100nA Idc) | 64–66 | `## 100nA Idc` — load + 3-panel plot of the (Vtg, Vbg) gatemap |
| 79 | 260 (nT, heater 6.5→3) | 73–74 | `# nT map` (first) — load + 3-panel plot |
| 80 | 261 (nT, heater 3→0) | 75–76 | `# nT map` (first) — load + 3-panel plot |
| 79 (again) | 260 | 77–78 | `dat79 = sl.pload(folder, 79)` — re-load with different post-processing |
| 82 | 269 (Idc vs T, heater 6.5→3) | 80 | `# nT map` (second occurrence — header is mislabeled; this is `# Idc vs T` analysis). Variable name `dat79` is also misleading — actually data_id=82. |
| 83 | 270 (Idc vs T, heater 3→0) | 80 | Same cell — concatenated with data_id=82 as `dat80` |
| 85 | 282 (B vs Idc) | 86–89 | `# B vs Idc` — load, 2-panel plot, B-slice extraction |

Data dirs in the fixture but **not analyzed** in the ana notebook: 76, 77,
81, 84, 86, 87, 88, 89, 90. Most are intermediate / second-pass runs of
the same shape (e.g., 76 vs 77 are both heater-axis multimegasweeps).

## Ambiguous cases (measure side)
- Cells 255 picks one of (76, 77) — the other is a re-run / second pass.
- Cells 289 / 294 / 299 share the same sweep shape (2001-pt 1D of k_tg2);
  available file_ids 86, 87, 89, 90 are all 2001-pt 1D sweeps. Order is
  almost certainly chronological (86 = cell 289, 87 = cell 294, 89/90 =
  cell 299 + final retry).
- Cell 282 specifies `np.linspace(-0.012, -0.002, 51)` — file_id 85's
  metadata.json has `slow_setpoints` of length 51 with that exact range,
  confirming.
- File_id 78 (a `multisweep` between 77 and 79) is likely an `s.ramp`
  or `s.reset` artifact — included in `./data/` for completeness but not
  one of the canonical campaign sweeps.
