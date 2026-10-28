# Test case: b1c2 — superconducting-state characterization

Offline HERA test fixture. Captures a contiguous block of measurements Isaac
ran on b1c2 (dual-device chip on the toploader) intended to characterize the
superconducting state, plus the expert-framed goal as it would be handed to
HERA at session start. Intended use: feed these inputs to HERA-shaped agents
and judge how well the analysis tracks what an expert would do.

## Source

- Notebook: `~/sharpelab/dgglab-measurements/toploader/Isaac/b1c2_toploader/20260415_measure.ipynb`
- Cells: 243–299 (57 cells)
- Captured: 2026-05-06 (notebook last touched 2026-05-06 15:00 — Isaac may
  add more cells to the same section after this snapshot)

## Goal

See `goal.md` — Isaac's expert framing: "characterize the superconducting state".

## Layout

Mirrors a real measurement directory's shape so HERA's tactical agent
can be rooted here directly (`device_card.md`, the working notebook, and
`data/` all at the top level).

- `goal.md` — the expert framing in Isaac's words, plus a one-paragraph
  preamble for an offline HERA test
- `device_card.md` — copied from `toploader:~/measurements/Isaac/b1c2_toploader/device_card.md`
  on 2026-05-06 (current-cooldown state; data was taken in a prior cooldown
  — see `hera_session.md` for the drift caveat)
- `hera_session.md` — the "first message" handoff per `hera/session_template.md`,
  adapted for offline-test mode (analysis only, no nb-collab proposals)
- `cell-to-fileid.md` — mapping from notebook cells to `data/<file_id>/`
  subdirectories
- `20260415_measure__c243-299.ipynb` — measure-side cropped notebook,
  cells 243–299 from the source. Outputs preserved.
- `20260415_ana__c0-6_60-89.ipynb` — ana-side cropped notebook. Cells 0–6
  are the source's setup (imports, constants, helper defs); cells 60–89
  cover the analysis sections that touch our data dirs (`# nD map, Beff = 0
  / ## 100nA Idc`, two `# nT map` sections, `# B vs Idc`). A markdown
  cell between the two slices flags the elision. Outputs preserved.
- `data/<file_id>/` — sweep outputs (TSV + metadata.json + per-run plot.png)
  for each sweep in the campaign. file_ids 75–90 (15 dirs, ~11 MB total).
- `images/cell<N>_out<M>.png` — every PNG output across cells 243–299,
  named by source-cell index. Candidate inputs for `hera-classify` (where
  the cell's plot is a 2D gate map of transport data) — most are not gate
  maps, see "Per-cell modality" below.

## Section structure (Isaac's headers)

| Cells | Header | Sweep family |
|---|---|---|
| 243–262 | `# nT map at Beff = 0` | heater × (Vtg, Vbg) |
| 263–271 | `# Idc vs T` | heater × DC bias |
| 272–275 | `# Idc vs n` | (Vtg, Vbg) × DC bias |
| 276–283 | `# B vs Idc` | field × DC bias |
| 284–299 | `# find 90 degrees theta` | calibration tail (likely separate concern) |

## Per-cell modality (relevant for `hera-classify` scope)

`hera-classify` is scoped to **2D gate maps of transport data** — (Vbg, Vtg)
or (n, D). Out of scope: anything else (heater × x, B × x, 1D sweeps,
calibration). The classifier is expected to politely refuse out-of-scope
inputs (empty findings + scratchpad noting wrong modality).

| Cell | PNG | Sweep | Modality vs classifier |
|---|---|---|---|
| 254 | `cell254_out2.png` | `multisweep([k_tg, k_bg], …)` | **In scope** — true (Vtg, Vbg) gate map |
| 255 | `cell255_out45.png` | `multimegasweep([heater], …, [k_tg, k_bg])` | Per-frame — each frame is a (Vtg, Vbg) gate map at fixed heater |
| 260 | `cell260_out38.png` | same family, heater 6.5→3 | Per-frame |
| 261 | `cell261_out18.png` | same family, heater 3→0 | Per-frame |
| 269 | `cell269_out38.png` | `megasweep(heater, …, dc205, …)` | Out of scope — heater × bias |
| 270 | `cell270_out18.png` | same family, heater 3→0 | Out of scope |
| 274 | `cell274_out53.png` | `multimegasweep([k_tg, k_bg], …, [dc205])` | Per-frame — (Vtg, Vbg) at fixed bias |
| 282 | `cell282_out53.png` | `megasweep(mag.field, …, dc205, …)` | Out of scope — B × bias |
| 289 | `cell289_out3.png` | `s.sweep(k_tg2.volt, …)` | Out of scope — 1D |
| 292 | `cell292_out2.png` | `s.sweep(mag.field, …)` | Out of scope — 1D |
| 294 | `cell294_out3.png` | same as 289 | Out of scope — 1D |
| 299 | `cell299_out3.png` | same as 289 | Out of scope — 1D |

The `cell<N>_out<M>.png` filename's `_outM` is the byte-offset index `nb
extract` assigns; M doesn't carry semantics beyond "Mth PNG output of cell N".

## Not yet captured (gaps for later)

- **Per-image scan-context.** `hera-classify` accepts `--scan-context` for
  per-image biasing context (carrier-density anchors, what's expected).
  Isaac's cells embed some of this in `meas_config["comment"]`; pulling
  those into per-image context files is a follow-up.
- **Ana notebook gaps.** The cropped ana notebook references data_id=93
  in its `## full D, -n` cells (67–71) but data_id=93 isn't in this
  fixture — the embedded plot outputs render fine, but anyone trying to
  re-execute those cells will hit a load failure. Acceptable for read-only
  agent inspection; flag if re-execution becomes a use case.
- **Ground-truth annotations.** No "expected output" files yet — the test
  judges agent output qualitatively. If the test gets re-run frequently,
  worth writing a short "what an expert would say" rubric per finding.
- **`hera-classify` baseline runs.** Could pre-run the classifier on the
  in-scope images now (cells 254 / 255 / 260 / 261 / 274 frames) and store
  sidecars + annotated overlays alongside, so subsequent runs can compare
  against a "day-one baseline" rather than the live API every time.
