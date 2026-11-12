# Cell ↔ file_id mapping

Mapping from cells in `./241207_measure__c0-93.ipynb` (fixture indices ==
source indices, cropped from 0) to data directories under `./data/<file_id>/`.
RPL_10's **first cooldown**, so the data dirs are the earliest in the device's
life: file_ids start at 0. Verified against each `data/<id>/metadata.json`
(`function`, `param`/`setpoints` for 1D sweeps, `slow/fast_setpoints` and
`comments` for 2D maps, and `start_time`).

## Gate checks (`# Gate checks`, cells 21–42) — 1D `s.sweep`, function `sweep`

| Cell | Subsection | Sweep | file_id | metadata check |
|---|---|---|---|---|
| 23 | Initial checks | `s.sweep(k_tg.volt, linspace(0,1,101), delay=1)` | **0** | param `k_tg_volt`, 0→1, n=101 |
| 24 | Initial checks | `s.sweep(k_bg.volt, linspace(0,1,101))` | **1** | param `k_bg_volt`, 0→1, n=101 |
| 25 | Initial checks | `s.sweep(k_si.volt, linspace(0,10,101))` | **2** | param `k_si_volt`, 0→10, n=101 |
| 28 | Top gate (26 nm) | `s.sweep(k_tg.volt, linspace(0,13,401))` | **3** | param `k_tg_volt`, 0→13, n=401 |
| 30 | Top gate (26 nm) | `s.sweep(k_tg.volt, linspace(0,13,401))` | **4** | param `k_tg_volt`, 0→13, n=401 |
| 31 | Top gate (26 nm) | `s.sweep(k_tg.volt, linspace(0,-13,401))` | **5** | param `k_tg_volt`, 0→−13, n=401 |
| 34 | Bottom Gate (40 nm) | `s.sweep(k_bg.volt, linspace(0,20,401))` | **6** | param `k_bg_volt`, 0→20, n=401 |
| 36 | Bottom Gate (40 nm) | `s.sweep(k_bg.volt, linspace(0,20,401))` | **7** | param `k_bg_volt`, 0→20, n=401 |
| 37 | Bottom Gate (40 nm) | `s.sweep(k_bg.volt, linspace(0,-20,401))` | **8** | param `k_bg_volt`, 0→−20, n=401 |

Cells 27 / 33 (`remove_validator` / `add_validator` to ±13 / ±20) and 35 / 38
(`nplci` changes), 39 (`s.reset()`), 40–42 (`s.ramp` parks gates) produce no
data dirs. **`latest_fileid` for `after-gate-checks` = 8** (cell 37, last
bottom-gate sweep).

## First gate map (`# Gatemap`, cells 43–54) — 2D maps, function `megasweep`

All ten are `s.megasweep(k_bg.volt, linspace(...,201), k_tg.volt, linspace(...,201), slow_delay=3, fast_delay=1)` at various V_Si.

| Cell | V_Si comment | file_id | metadata check (slow=k_bg, fast=k_tg) |
|---|---|---|---|
| 44 | V_si = 10 | **9** | slow −9→5, fast −5.5→6, n=201×201 |
| 45 | V_si = 10 | **10** | fast −4.5→5 |
| 46 | V_si = 10 | **11** | (V_si ramped to 10) |
| 47 | V_si = 10 | **12** | |
| 48 | V_si = −10 | **13** | comment `V_si = -10` |
| 49 | V_si = 10 | **14** | fast −4.5→3 |
| 50 | V_si = 10 | **15** | slow −9→5, fast −4.5→3 |
| 51 | V_si = 20 | **16** | comment `V_si = 20` |
| 52 | V_si = 20 | **17** | |
| 53 | V_si = 20 | **18** | fast −4.5→2.5 |

Cell 54 (`k_bg.volt(0)`) parks the back gate, no data. **`latest_fileid` for
`after-first-gatemap` = 18** (cell 53, last gate-map of the first section).

## Post-cut (answer key — NOT in any allowlist)
| Cell | Section | Sweep | file_id |
|---|---|---|---|
| 57 | quick-DC config | DC-bias 1D sweep (mc_2) | 19 |
| 58 | quick-DC config | DC-bias 1D sweep (mc_2) | 20 |
| 61 | returning to gate map | gate map V_si=20 (mc_2) | 21 |
| 64–65 | config change | gate maps | 22, 23 |
| 70–71 | after rat cleansing | gate maps V_si=−20 | 24, 25 |
| 74 | after rat cleansing | gate map (mc_3) | 26 |
| 75–77 | Si back gate testing | Si-BG 1D sweeps | 27–33 (range) |
| 78+ | Fraunhofer / I_dc / hysteresis | field × bias maps | 34+ |

These are listed only so the human author can see what the post-cut sections
do; their data dirs are **excluded** from both frontiers' allowlists.

## Notes / ambiguities
- The gate-check sweeps and the gate-map sweeps are distinguished cleanly by
  `function` (`sweep` = 1D gate check; `megasweep` = 2D map) and by `param`
  vs `slow/fast_setpoints`. The 1:1 cell→id mapping above is unambiguous for
  cells 23–53 (9 sweeps + 10 maps, consecutive ids 0–18).
- file_ids 19/20 are the post-cut DC-bias 1D sweeps (function `sweep`,
  no comment) — chronologically after the gate maps and before the next
  gate-map cell (61 → id 21). They belong to the post-cut DC section, so they
  are excluded from `after-first-gatemap`.
