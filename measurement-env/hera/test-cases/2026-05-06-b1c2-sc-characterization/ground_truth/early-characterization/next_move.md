# Ground truth — first move at the cold-start frontier

*Light reference (this frontier exists mainly to demo the depth axis, not as a
graded item). One expert path, not the only answer.*

> **Verified ana-grounded 2026-06-05 (audit).** Cross-checked against the measure
> notebook (cut idx 10 = `s.reset()`; idx 11 = `s.multisweep([k_tg.volt,
> k_bg.volt], …)` → data/75, confirmed `function: multisweep` in
> `data/75/metadata.json`) and Isaac's ana of data/75 (`data_id = 75`, his
> `Rxx = (sr830_4_X/100)/Ixx`, `Ixx = sr830_1_X/(-1e6)`). No change to the
> next-move text — the first move described here is correct. The baseline gate
> map his analysis produces is `../figures/ana_75_baseline-gatemap_sr830_4.png`
> (a high-Rxx CNP ridge running diagonally through the (Vtg,Vbg) window).

## What the operator actually did first
A baseline **(Vtg, Vbg) gate map** at base T, Beff = 0:
`s.multisweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], delay=1.2)`
(cell 11 → `data/75`) — a single-pass (n, D) map over the validated window.
Immediately after, the nT heater sweep (cell 12: `multimegasweep([heater], 0→7 V,
71 steps, …)` → the `# nT map at Beff = 0` section).

## Judging the depth contrast (the point of this frontier)
The *experiment* is fixed by the briefs (an (n,D) gate map). What should differ
between `quick` and `deep` is the **execution**:
- **quick** — coarse grid (few points per axis), short/zero settle delay, single
  pass, possibly a narrower or full-but-sparse window. A recon scan.
- **deep** — finer grid, RC-aware delay, resolution sufficient to locate the CNP
  and feature edges; may note averaging or a second pass.

A good result is that the proposed sweep parameters (point counts, delay, range,
passes) move substantially with the depth level while the sweep *call* stays the
same shape. If they don't, the agent isn't internalizing the rigor signal.
