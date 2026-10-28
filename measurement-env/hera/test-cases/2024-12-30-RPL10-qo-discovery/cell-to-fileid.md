# Cell ↔ file_id mapping

Mapping from cells in `./241230_measure__c0-65.ipynb` to data directories under
`./data/<file_id>/`. Inferred by matching each sweep cell's `add_comment` /
function / params against the source data dir's `metadata.json` (`function`,
`comments`, `slow_param`/`fast_param`, `start_time`). Source data dir:
`~/sharpelab/dgglab-measurements/toploader/aaron/RPL_10/data/`.

This notebook's file_id span is **132 → 159** (its first MC4 sweep through the
last executed QO fan). Files 130/131 (MC3, Dec 30 morning) belong to the prior
(241207) notebook's tail and are excluded. File 160+ is post-cut
(`# Temperature dependence`) — `data/160` is kept in the pool for ground-truth
reading only and is NOT in the frontier allowlist.

| Cell | Section | Sweep | file_id(s) | Notes |
|---|---|---|---|---|
| 23 | Taking gate maps in field / B=+100mT | `multisweep`, "B = 100 mT" | 132 | first MC4 sweep of this notebook |
| 25 | B=+100mT | `multisweep`, "B = 100 mT" | 133 | after 'undr'-error clock fix (cell 24) |
| 26 | B=+100mT | `multisweep`, "B = 100 mT" | (132/133) | second 100 mT pass |
| 28 | B=−100mT | `multisweep`, "B = -100 mT" | 134 | |
| 32 | multiferroism Hall check | `multisweep`, "fast axis is D, neg→pos D" | 135 | |
| 33 | multiferroism Hall check | `multisweep`, "fast axis is D, pos→neg D" | 136 | |
| 35 | High res gate map | `multisweep`, "B = 0 T" | 137 | |
| 36 | High res gate map | `multisweep`, "B = 0 T" | 138 | |
| 40–42 | Perusing Idc | `multimegasweep`, "sweeping Idc and n_e at various D" | 139–151 | DC-bias × density linecuts at a series of D values (D=0.176 etc.); many files |
| 43 | Perusing Idc | `multimegasweep`, "Idc and n_e at D = +0.221 V/nm" | 152 | last pre-QO-section sweep |
| 46 | QO / Gate maps in field | `multisweep`, "B = 1.0 T" | 153 | |
| 47 | QO / Gate maps in field | `multisweep`, "B = 1.0 T, higher res" | 154 | |
| 48 | QO / Gate maps in field | `multisweep`, "B = -1.0 T" | 155 | |
| 50 | QO / D = 0.31 V/nm | `multimegasweep([mag.field], …, [k_tg,k_bg])`, "QO, D=0.31, n=-2.9 to -2.1, B 1→0" (101 fast pts) | 156 | first n-vs-B fan at D=0.31 |
| 51 | QO / D = 0.31 V/nm | `s.sweep(mag.field, linspace(0,1,1001))`, "resolution check, n=-2.6, B 0→1" | 157 | 1D field sweep, single (n,D) point |
| 52 | QO / D = 0.31 V/nm | `multimegasweep([mag.field], …)`, fan, 201 fast pts, 351 field | 158 | |
| 53 | QO / D = 0.31 V/nm | `multimegasweep([mag.field], …)`, fan, **251 fast pts, 351 field** | **159** | **latest executed sweep at the cut (latest_fileid)** |
| 54 | QO / D = 0.31 V/nm | (raw, NOT executed) draft fan, D=0.25, n=-2.75 to -0.35 | — | raw cell, no data dir; this is the cut cell |
| 60 | Temperature dependence (POST-CUT) | `multisweep([k_bg,k_tg],…)`, "D = 0.35 V" gatemap after heater ramp | 160 | ground-truth only; NOT allowlisted |

## Allowlist (pre-cut, cells 0–54)

`data: [132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145,
146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]` — the full
contiguous span 132–159 (28 dirs).

## Ambiguous cases

- Cells 23/25/26 ("B = 100 mT") map onto files 132/133 (two distinct 100 mT
  passes plus the initial 'undr'-error one); exact 1:1 is approximate but all
  three land inside 132–134 and are allowlisted regardless.
- Cells 40–42 ("sweeping Idc and n_e at various D") are a long multi-D series
  spanning files 139–151; the per-cell split is approximate (they are re-runs /
  continuations of the same shape). All are inside the allowlist.
- Cell 53 → 159 is confirmed: `data/159/metadata.json` has `slow_param =
  ['magnet_field']`, 351 field points 1→0 T, fast `[k_tg_volt, k_bg_volt]`, comment
  "D = 0.31 V/nm, n = -2.9 to -2.1, B = 1 to 0 T", and is the last fan before the
  Temperature-dependence section's file 160.
