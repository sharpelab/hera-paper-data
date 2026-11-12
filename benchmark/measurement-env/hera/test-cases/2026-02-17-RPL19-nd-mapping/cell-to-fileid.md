# Cell ↔ file_id mapping

Mapping from cells in `./20260217_measure__c0-65.ipynb` (fixture indices ==
source indices; cropped from 0) to data directories under `./data/<file_id>/`.
Inferred by sweep-shape + chronology + `add_comment` against the source data dir
`~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/data/`.

Confirm against the cell text + each `metadata.json`'s `function`, `columns`,
`measurement_config`, and `start_time`.

This notebook's sweeps begin at the "Checks after power loss" section (cell 39);
the device's global file_id counter is well past 1900 by this cooldown. The
stored crop (cells 0–65) spans **file_ids 1938–1948**. It carries two frontiers:
`after-rough-nd-map` (cut 51, latest 1944) and `after-broaden-map` (cut 57,
latest 1945).

| Cell | Section | Sweep shape | file_id | Notes |
|---|---|---|---|---|
| 40 | Checks after power loss | `s.sweep(k_si.volt, np.linspace(0, 48, 201), delay=1)` | 1938 | 201-pt Si-gate sweep; confirm device survived power loss |
| 42 | Checks after power loss | `s.sweep(k_bg.volt, np.linspace(0, 1, 101), delay=1)` | 1939 | 101-pt back-gate check |
| 43 | Checks after power loss | `s.sweep(k_bg.volt, np.linspace(0, 7, 101), delay=1)` | 1940 | 101-pt back-gate check |
| 44 | Checks after power loss | `s.sweep(k_bg.volt, np.linspace(0, -8.5, 251), delay=1)` | 1941 | 251-pt back-gate check to negative validator edge |
| 45 | Checks after power loss | `s.sweep(k_tg.volt, np.linspace(0, 6.5, 251), delay=1)` | 1942 | 251-pt top-gate check |
| 46 | Checks after power loss | `s.sweep(k_tg.volt, np.linspace(0, -6.5, 251), delay=1)` | 1943 | 251-pt top-gate check |
| 47 | Checks after power loss | `shutdown()` | — | ramps gates/bias to 0; no data dir |
| 49 | rough nD map at positive D | raster geometry build + preview plots (no sweep) | — | builds `raster_vtgs`/`raster_vbgs` over a polygon in (n, D); see cell output for the swept region |
| 50 | rough nD map at positive D | `sr830_*.sensitivity(20e-3)` | — | sets coarse lock-in sensitivity for the rough map |
| 51 | rough nD map at positive D | `s.multisweep([k_tg.volt, k_bg.volt], [raster_vtgs, raster_vbgs], delay=1)` | **1944** | the rough nD map — coarse n-first raster, ~8.6k pts; **F1 latest sweep (cut 51)** |
| 53 | Fine nD map | raster build, `sr830_*.sensitivity(5e-3)` | — | builds the broaden-map raster (D extended to −0.4, `nx, ny = 251, 251`) |
| 55 | Fine nD map | `s.multisweep([k_tg.volt, k_bg.volt], [raster_vtgs, raster_vbgs], delay=0.9)` | **1945** | the **broaden map** — n-first, full range; **F1 answer / F2 latest sweep (cut 57)** |
| 56–57 | (field check) | `s.ramp(mag.field, ±0.5)` / `s.ramp(mag.field, 0)` | — | trapped-flux check; no data dir. **F2 cut at 57** |
| 60 | Rough fan, sweeping D first… | `s.multisweep(...)` D-first, 101×101 | **1946** | D-first re-map to reduce streaks — **F2 answer** |
| 62 | Rough fan, sweeping D first… | `s.multisweep(...)` D-first, reversed | **1947** | forward/reverse pair (hysteresis check) — **F2 answer** |
| 65 | Fine nD, sweeping D first | `s.multisweep(...)` D-first, 201×251 | **1948** | fine D-first full map (answer-key context) |

**Latest landed sweeps:** F1 (cut 51) → `data/1944/`; F2 (cut 57) → `data/1945/`.

## Allowlists
- **`after-rough-nd-map`** (F1): **1938–1944** (7 dirs). 1945+ are post-cut.
- **`after-broaden-map`** (F2): **1938–1945** (8 dirs). 1946+ are post-cut.

Earlier file_ids (≤ 1937) belong to prior notebooks / cooldown days and are not
served. `data/` here holds the union: **1938–1945**.

## Notes / ambiguous cases
- 1944's `metadata.json` carries `function: multisweep`, `delay: 1`,
  `measurement_config` = `mc_31` (current on `sr830_4 = I_{30-21}`), and
  `comments[0] == 'MC31, Vsi = 48V'` — matching cell 51 exactly. Its raster
  setpoints cover `n ∈ [0.22, 2.0]` (1e12 cm⁻²) and `D ∈ [0.70, 1.06]` V/nm,
  consistent with cell 49's `ns/Ds` polygon at `nx, ny = 101, 101`.
- 1945 (cell 55) is the broaden map: n-first raster, `n ∈ [0.2, 1.8]`,
  `D ∈ [−0.4, 1.065]`, `nx, ny = 201×251`. Post-cut for F1, pre-cut (allowlisted)
  for F2.
- 1946 (cell 60) is the D-first re-map (`Ds` to 0.4, 101×101, `rev_y=False`);
  1947 (cell 62) its reverse pair. Both post-cut answer-key for F2; **not** served.
