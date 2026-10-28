# Test case: QC0426 — trilayer-graphene Landau-fan mapping (VTI fridge)

Offline HERA test fixture. Captures the 2026-06-01 cooldown of **QC0426**, a
trilayer-graphene device run by **Qingrui** on the Sharpe Lab's **VTI** cryostat
— the **first non-toploader fixture** (different fridge, operator, material, and
analysis convention from the RPL/b1c2 toploader fixtures).

## The campaign in one paragraph

A **stacking-classification** run on a dual-gated (+ Si back gate) trilayer
graphene flake of *unknown* stacking: the sample was loaded into the VTI to
decide **ABA (Bernal) vs ABC (rhombohedral)** from its Landau-fan / quantum-Hall
fingerprint and displacement-field dependence. After instrument bring-up and
gate-range calibration, the operator takes a 0 T TG-BG gate map, establishes a
**B-n Landau fan at the charge-neutral D = 0 line** (to 8 T, then 13 T, then with
Si-gate screening), does a block of contact and 6 T characterization, and
finishes by sweeping the Landau fan across a **series of displacement fields**
(D = 0.25, 1, −1, −0.25, −0.5) — the discriminating measurement. **Outcome
(Qingrui, 2026-06-09):** the VTI didn't get cold enough for a definitive call;
he suspects **ABA**. The fans here are visibly washed out at ~1.2 K, consistent
with that.

## Frontiers

This campaign carries **three decision frontiers** along its arc; **all three are
now built** (Zack, 2026-06-09: "start with your suggested frontier and then we'll
work on the other two").

1. **`after-0T-gatemap`** (DECISION, **built**) — 0 T and 3 T gate maps in hand →
   **go to field and measure the first B-n Landau fan at D = 0** (the step that
   starts resolving the QHE structure that discriminates the stacking).
2. **`after-D0-fan`** (DECISION — *contested*, **built**) — first D = 0 fan
   established but washed out at ~1.2 K → the goal points at sweeping the D-series,
   but Qingrui detoured to **introduce the Si back gate** (TG-Si map → Si-screened
   fan) first. The one genuine fork in the campaign (Si-gate-first vs
   D-series-first); the judging rubric credits both branches.
3. **`after-density-cut`** (COVERAGE, **built**) — device fully characterized and
   a 0-field density cut along the D = 0.25 gate-line just landed → sweep it into
   a Landau fan and map the fan across a D-series. **The suggested frontier.**

## Source

- Notebook: `~/sharpelab/dgglab-measurements/vti/qingrui/20260601-QC0426-3LGr/measurement.ipynb`
- Analysis: `…/analysis.ipynb` (convention reference; indexed in
  `hera/docs/notebook-indexes/notebook-index-QC0426-3LGr.md`)
- Cells stored: 0-201 (cropped from 0, so **fixture index == source index**). The
  driver re-crops the *served* notebook to each frontier's `cut_index`
  (`after-0T-gatemap` → 95, `after-D0-fan` → 102, `after-density-cut` → 180);
  cells past the cut are kept only as that frontier's answer key and are never
  served.
- Captured 2026-06-09.

## Layout

- `goal.md` — campaign-goal framing for the baseline (non-brief) run.
- `device_card.md` — QC0426 physical properties + VTI rig setup this cooldown.
- `cell-to-fileid.md` — cell ↔ `data/<file_id>/` mapping (human aid; not served).
- `20260601_measure__c0-201.ipynb` — cropped measure notebook, cells 0-201.
- `data/<file_id>/` — sweep outputs for the union of the built frontiers'
  allowlists: `after-0T-gatemap` {24, 25, 26} + `after-D0-fan` {24, 26, 27} +
  `after-density-cut` {24, 26, 27, 31, 33, 63, 79} (the dirs are shared).
- `frontiers/<slug>.md` — one per built frontier (`after-0T-gatemap` DECISION,
  `after-D0-fan` contested DECISION, `after-density-cut` COVERAGE); YAML contract
  + prose.
- `ground_truth/<slug>/` — `next_move.md` + `reading.md` (+ `analysis/` method
  scripts, `figures/`), per built frontier.
- `briefs/<slug>/` — `open-{short,long}.md` + `directive-{short,long}.md`
  (autonomy × length; decision-frontier grid), per built frontier.

## Section structure (operator's headers)

| Cells | Header | Sweep family | run(s) |
|---|---|---|---|
| 0-80 | Connect Instruments / gate-range selection / four corners | 1D gate sweeps | 0-23 |
| 81-88 | `# TG-BG sweep at 0T` | `megasweep` DC_bias×k_bg | 24, 25 |
| 89-95 | `# gate sweeps at finite field` | `megasweep` (B=3T) — **cut (95)** | 26 |
| 96-102 | `# B-n sweep at D = 0` | `multimegasweep` ×[mag] | 27 — `after-0T-gatemap` **answer**, `after-D0-fan` **cut (102)** |
| 103-110 | `# try Si gate -- TG-Si sweep` | `megasweep` ×k_2410 | 28, 30 — `after-D0-fan` **answer** |
| 111-115 | `# B-n sweep at D=0, Si=+60V` | fans + Si | 31, 32, 33 |
| 116-154 | `# testing 2T contacts…` / `# quick Vtg-Vbg scan at 6T` | `multisweep`/`mms` | 34-61 |
| 155-180 | `# gate map at 6T, Si=+95V` (+ D=0.25 density cut) | `mega` 63; density cut 79 — **cut (180)** | 62-79 |
| 181-200 | `# B-n sweep at D=0.25 / 1 / −1 / −0.25 / −0.5` | `mms` Landau fans — **answer** | 80-84 |

## The frontiers built here

- **`after-0T-gatemap`** (DECISION) — cut_index 95, latest `data/26` (the B = 3 T
  finite-field gate map). Answer: **go to field and take the first B-n Landau fan
  at the D = 0 line** (run 27 → 8 T, then run 31 → 13 T). A clear-answer decision
  (the prerequisite for resolving the QHE structure that classifies the stacking).
- **`after-D0-fan`** (DECISION — *contested*) — cut_index 102, latest `data/27`
  (the D = 0 fan to 8 T). Answer: **introduce the Si back gate** — a TG-Si gate map
  (run 28), the Si-screened D = 0 fan (run 31, Si = +60 V, to 13 T), and VSi-n maps
  (32/33). The goal points at sweeping the D-series, but Qingrui detoured to bring
  up the Si gate first; the rubric credits both branches.
- **`after-density-cut`** (COVERAGE) — cut_index 180, latest `data/79`. Answer:
  sweep the D = 0.25 density cut into a Landau fan (run 80) and **repeat the fan
  across a D-series** (D = 1, −1, −0.25, −0.5 → runs 81-84). A clear-answer COVERAGE
  decision (Qingrui did not treat it as contested).

## Per-cell modality (relevant for `hera-classify` scope)

For `after-density-cut`, the latest result (`data/79`) is a **1D density cut**
(`Rxx` vs n at fixed D, 0 field), not a 2D map — outside the `hera-classify`
2D-gate-map scope. For `after-0T-gatemap`, the latest result (`data/26`) **is** a
2D `Rxx(Vtg, Vbg)` gate map (at B = 3 T) — in `hera-classify` scope. In both
cases the on-disk `plot.png` shows only the live monitor; the transport map must
be re-formed from the TSV as `sr{1,2,3}_X / (sr0_X / sr0_gain)` and reshaped over
the sweep grid (regular megasweep grid for the gate maps; `multimegasweep` raster
for the fans).

## Notes / gaps

- **First non-toploader convention** — current on `sr0` with explicit gain
  division, capacitance-based `calc_nD` with a SiO₂ term, per-run contact configs,
  TG driven by the DC205 (`DC_bias` column). All captured in `device_card.md` /
  the notebook index.
- **VTI base T ≈ 1.2 K**, not mK — bounds the resolvable QHE physics, and was the
  campaign's limiting factor: too warm for a definitive ABA/ABC call.
- **Stacking unconfirmed, leaning ABA (Bernal)** — classifying it was the run's
  purpose; Qingrui's post-hoc suspicion is ABA, not the earlier ABC guess.
- **Figures are renders** of the answer-key fans/maps via Qingrui's own analysis
  convention; see `ground_truth/<slug>/analysis/README.md` (the built frontiers
  share the same `render` convention — `render_fans.py` / `render_maps.py`).
- **All three frontiers are now built** (`after-0T-gatemap`, `after-D0-fan`,
  `after-density-cut`).
