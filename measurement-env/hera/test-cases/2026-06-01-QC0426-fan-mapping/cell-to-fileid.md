# Cell ↔ file_id map — QC0426 fan-mapping

Human navigation aid; **not served** to the replay agent. Maps measure-notebook
cells (`20260601_measure__c0-201.ipynb`, fixture index == source index) to the
`data/<id>/` run dirs. Run identities are from each run's `metadata.json`
signature (function / axes / config), which is authoritative; the cell→run
sequence is reconstructed from execution order and is approximate around the
three interrupted runs (29, 59, 61, which consumed a run number but produced no
usable sweep).

`mms` = `multimegasweep`, `ms` = `multisweep`, `mega` = `megasweep`.

## Served region (cells 0-180, pre-cut)

| Cells | Section | Runs | What |
|---|---|---|---|
| 0-31 | Connect Instruments / test | — | FastBi1K5 magnet, LakeShore, lock-ins, DC205 (TG), Keithleys (BG, Si) |
| 36-48 | `# Measurement` | 0-12 | 1D `k_bg` gate-response sweeps (range-finding) |
| 54-75 | gate-range selection / `# check four corners` | 13-23 | 1D gate sweeps; pick `k_tg∈[−6.5,7.5]`, `k_bg∈[−5,4.8]` |
| 84, 88 | `# TG-BG sweep at 0T` | **24**, 25 | 0 T TG-BG gate maps (`mega`, DC_bias × k_bg) |
| 95 | `# gate sweeps at finite field` | **26** | finite-field gate map (`mega`) |
| 102 | `# B-n sweep at D = 0` | **27** | **D = 0 Landau fan to 8 T** (`mms`, [DC_bias,k_bg]×[mag 0-8]) |
| 107 | `# try Si gate -- TG-Si sweep` | 28, (29 intr.), 30 | TG-Si maps (`mega`, DC_bias × k_2410) |
| 110-115 | `# B-n sweep at D=0, Si=+60V` | **31**, 32, **33** | D = 0 fan to 13 T; Si-screened D = 0 fans |
| 123-150 | `# testing 2T contacts and Si gate at 6T` | 34-50 | 2T-contact checks, `ms`/`mms` density cuts at 6 T |
| 143-153 | `# quick Vtg-Vbg scan at 6T, finite VSi` | 51-60 | fast gate scans, freq sweeps (61 intr.) |
| 160 | `# gate map at 6T, Si=+95V` | **63** | **6 T gate map** (`mega`, DC_bias × k_bg) |
| 161-178 | (same section) | 64-78 | 6 T density-cut linecuts; n-Si maps (`mms` × k_2410) |
| 179-180 | (same section, sets up D=0.25 line) | **79** | **0-field density cut along the D = 0.25 line** (`ms`) — **latest result** |

## Answer key (cells 181-201, post-cut — never served)

| Cells | Section | Runs | What |
|---|---|---|---|
| 181-184 | `# B-n sweep at D=0.25` | **80** | Landau fan at D = 0.25 (`mms`, [mag 8→0]) |
| 185-188 | `# B-n sweep at D=1` | **81** | Landau fan at D = 1 (`vbg=vtg/1.3−8`) |
| 189-192 | `# B-n sweep at D=-1` | **82** | Landau fan at D = −1 (`vbg=vtg/1.3+8`) |
| 193-196 | `# B-n sweep at D=-0.25` | **83** | Landau fan at D = −0.25 |
| 197-200 | `# B-n sweep at D=-0.5` | **84** | Landau fan at D = −0.5 |

## Allowlist for this frontier (`included.data`)

`[24, 26, 27, 31, 33, 63, 79]` — 0 T gate map (24), finite-field map (26), D = 0
fans (27 @ 8 T, 31 @ 13 T), Si-screened D = 0 fan (33), 6 T gate map (63), latest
density cut (79). The post-cut fans **80-84** are the answer and are **not**
hardlinked into the served working copy.

## Analysis-side cross-reference

`analysis.ipynb` loads the fans at files **80-84** (cells 55, 62-65) and the
gate maps at **25-32, 63** — see `notebook-index-QC0426-3LGr.md`. The
ground-truth figures for this frontier are rendered from those same files via
the scripts in `ground_truth/after-density-cut/analysis/`.
