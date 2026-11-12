# Test case: RPL_19 — nD mapping (coverage → de-streak)

Offline HERA test fixture. Captures the post-power-loss **(n, D) mapping phase**
of Aaron's 2026-02-17 RPL_19 cooldown and carries **two chained decision
frontiers** drawn from how the mapping actually unfolded:

1. **`after-rough-nd-map`** (COVERAGE) — a coarse recon map of a thin high-D
   sliver is in hand; the move is to **extend the map to the full reachable
   (n, D) range** (push D down to −0.4).
2. **`after-broaden-map`** (DATA-QUALITY / METHOD) — the broaden map is in hand
   but, swept n-first, **streaks in the positive-D corner**; the move is to
   **re-sweep D-first** to suppress the artifact (+ a forward/reverse hysteresis
   pair).

> **History.** This fixture was originally filed (2026-06-01) as a single DEPTH /
> "coarse→fine refine" frontier. Aaron's expert review (2026-06-08) corrected
> that: the post-rough-map move is a *coverage* extension, not a resolution
> refine, and the campaign's genuinely distinct skill is the *de-streaking*
> decision. The fixture was re-grounded into the two frontiers above and renamed
> from `…-nd-map-resolution`. The "gatemap → Fraunhofer" SC-characterization
> decision that comes later in this campaign is deliberately **not** captured
> here — it is already covered by `2025-11-03-RPL19-sc-dome-fraunhofer`.

## Source

- Notebook: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/20260217_measure.ipynb`
- Cells stored: 0–65 (cropped from 0, so **fixture index == source index**). The
  driver re-crops the *served* notebook to each frontier's `cut_index` (51 for
  F1, 57 for F2); the later cells are kept only as ground-truth answer keys and
  are never served.
- Captured 2026-06-01; re-grounded + recropped (c0-57 → c0-65) 2026-06-08.

## Goal

See `goal.md` — map the (n, D) landscape (find the SC / anomalous-Hall region and
pin down where it sits), cleanly enough to choose detailed follow-ups.

## Layout

- `goal.md` — campaign-goal framing for the baseline (non-brief) run.
- `device_card.md` — RPL_19 physical properties + rig setup this cooldown.
- `cell-to-fileid.md` — cell ↔ `data/<file_id>/` mapping (human aid; not served).
- `20260217_measure__c0-65.ipynb` — cropped measure notebook, cells 0–65.
- `data/<file_id>/` — sweep outputs. file_ids 1938–1945 (the union of both
  frontiers' allowlists; 1945 is post-cut for F1 but pre-cut for F2).
- `frontiers/` — `after-rough-nd-map.md` (F1, COVERAGE), `after-broaden-map.md`
  (F2, DATA-QUALITY).
- `ground_truth/after-rough-nd-map/` and `ground_truth/after-broaden-map/` —
  `next_move.md` + `reading.md` (+ `analysis/`, `figures/`).
- `briefs/<slug>/` — `open-{short,long}.md` + `directive-{short,long}.md`
  (autonomy × length; decision-frontier grid).

## Section structure (operator's headers)

| Cells | Header | Sweep family | file_id |
|---|---|---|---|
| 0–38 | `# Init` / `# Configs` | instrument instantiation, mc_1…mc_32, custom fns | — |
| 39–47 | `# Checks after power loss` | 1D gate sweeps (k_si, k_bg, k_tg) | 1938–1943 |
| 48–51 | `# rough nD map at positive D` | coarse n-first raster, thin high-D sliver — **F1 cut (51)** | 1944 |
| 52–55 | `# Fine nD map` | broaden map: n-first raster extended to D = −0.4 — **F1 answer / F2 latest** | 1945 |
| 56–57 | (trapped-flux field check) | `mag.field` ±0.5 T → 0 — **F2 cut (57)** | — |
| 58–62 | `# Rough fan, sweeping D first…` | D-first re-map (+ fwd/rev) — **F2 answer** | 1946, 1947 |
| 63–65 | `# Fine nD, sweeping D first` | fine D-first full map (answer-key context) | 1948 |

## The frontiers

- **`after-rough-nd-map`** — cut_index 51, latest `data/1944`. Answer: extend the
  map's range to cover the full reachable (n, D) landscape (cell 55 → 1945). A
  clear-answer COVERAGE decision (not contested, not depth).
- **`after-broaden-map`** — cut_index 57, latest `data/1945`. Answer: recognize
  the n-first fast-axis streaking and re-sweep **D-first** (cell 60 → 1946) with a
  forward/reverse pair (1947). A DATA-QUALITY / artifact-awareness decision.

## Per-cell modality (relevant for `hera-classify` scope)

`hera-classify` targets **2D gate maps of transport data** — (Vbg, Vtg) or
(n, D). Both 1944 and 1945 *are* (n, D) transport maps in scope, but they are
**rasterized polygon `multisweep`s** (scattered (n, D) points, not regular grids),
and their `plot.png`s show only the gate-leakage monitor — the transport channels
are in the TSV. A classifier needs the re-formed `Rxx(n, D)` map, not the on-disk
PNG.

## Notes / gaps

- **`plot.png` caveat (both cuts).** `data/<id>/plot.png` is the live gate-leakage
  monitor (flat `k_*_curr`), not the transport map; the (n, D) structure (and, for
  1945, the streaks) require re-forming `Rxx = sr830_{1,2,3}_X / sr830_4_X` from
  the TSV. Faithful to the live view; flagged in both `reading.md`s.
- **Physics labels flagged for review** in F1's `reading.md`: identifying the
  low-n / positive-D structure as SC/AH precursors is defensible-but-reviewable
  from a coarse zero-field map.
- **F2 figures are renders** of Aaron's pipeline (he re-swept rather than
  re-analyzed 1946); see `ground_truth/after-broaden-map/analysis/README.md`.
- **`runs/after-rough-nd-map/`** holds a replay output from the *original* depth
  framing — stale against the re-grounded answer key; kept as history.
