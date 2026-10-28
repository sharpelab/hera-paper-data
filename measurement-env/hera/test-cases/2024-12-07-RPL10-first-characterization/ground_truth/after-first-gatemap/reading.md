# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/18/` (the last gate map of the first section,
cell idx 53), the freshest result at the `after-first-gatemap` frontier. Floor +
caveats, not an exhaustive key.*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/18` in `241207_ana.ipynb` **cell 12**
> (`files = [18]`), not from the raw TSV + leakage `plot.png`. The prior version
> was authored before the ana figures were in hand and **drifted**: it framed the
> map as a generic "partial first-look raster" and said the transport map "must
> be made from the TSV," without showing what the map actually contains. Aaron's
> cell-12 figure **does** form `Rxx = sr830_{ind}_X / sr830_4_X` and renders the
> 2D map — it shows a clear vertical low-Rxx feature at V_tg ≈ +0.8 V in the
> landed V_bg ≈ −9…−7.9 strip, and he marks the candidate operating point
> `(V_tg, V_bg) = (0.825, −8.5)` with a red dot — the exact point he then takes to
> DC bias. Figures: `../figures/ana_18_gatemap_sr830_3_13-14.png` (and the other
> voltage channels + `ana_18_gatemap_current.png`). The DC-bias follow-up his
> map motivates is `../figures/ana_20_dcbias_sr830_3_13-14.png`.

## What the sweep is

`s.megasweep(k_bg.volt, np.linspace(-9., 5, 201), k_tg.volt, np.linspace(-4.5, 2.5, 201), slow_delay=3, fast_delay=1)` at V_Si = 20 V — a 2D (Vbg, Vtg)
transport gate map intended to be 201 × 201 over the working window, at base
temperature and no field. Followed: `T`, both gate leakage currents, and all
nine SR830 `X`/`P` channels (`sr830_4` = current channel, gain −1e6; the rest
voltage probes).

**How Aaron reads it (cell 12):** for each voltage probe `ind`, `I = sr830_4_X`
(the AC current bias), `Vxx = sr830_{ind}_X`, **`Rxx = Vxx / I`**, plotted as a
2D `pcolormesh` of `Rxx(V_tg, V_bg)` (SymLog, linthresh 100, 0–1e4 Ω for the
"long1" probes; 5e3–5e4 Ω for the higher-resistance "long2" probe 17-19) plus
the lock-in phase. The view is zoomed to `ax.set_ylim(-9, -6)` and he overplots
`ax.plot(0.825, -8.5, '.r')` — the candidate point. A final panel plots the
current `I*1e9` (≈ 0.9–1.1 nA, flat) to confirm the bias is steady.

## What it shows (floor — the must-see findings)

- **The transport map IS recoverable and Aaron rendered it.** `Rxx = Vxx/I`
  shows, across multiple voltage channels (9-11, 13-14, 14-15, …), a **vertical
  low-Rxx stripe at V_tg ≈ +0.8 V** crossing the landed V_bg ≈ −9…−7.9 strip — a
  gate-tunable low-resistance feature. The candidate operating point he marks,
  `(V_tg, V_bg) = (0.825, −8.5)`, sits on this stripe. This is the candidate-SC
  region that drives the next experiment.
- **`sr830_4` is the current, not transport.** The current panel shows it flat at
  ≈ 1 nA — it is the AC current bias and the **denominator** of `Rxx`. Forming
  `Rxx = sr830_{ind}_X / sr830_4_X` is the correct read; reading a "signal" out of
  `sr830_4` itself would be the mistake.
- **Phase channels are quiet** away from the feature and twist at the V_tg ≈ 0.8
  edge, consistent with a real resistance change rather than a wiring artifact.

## CRITICAL data-quality caveats (the agent should catch these)

- **The disk `plot.png` is NOT the transport map.** The operator's live `s.plot()`
  for this section registered only the **gate leakage monitor** (`k_tg_curr`,
  `k_bg_curr`) — *not* the lock-ins. So `data/18/plot.png` shows gate-charging
  traces, not a colormap. The transport map lives in `data/18/data.tsv.gz`
  (columns `sr830_1..9_X/P`, `sr830_4_X` the current) and is exactly what Aaron's
  cell-12 figure reconstructs. An agent that reads only the PNG sees "gate
  currents fine" and misses the feature; the correct read flags this and rebuilds
  `Rxx` from the TSV (a legitimate sub-step).
- **The map is INTERRUPTED / partial.** `data/18/metadata.json` has
  `interrupted: true`; the TSV holds ~3.4k rows vs the intended 40,401 (201×201).
  The slow axis starts at V_bg = −9.0, so the **landed strip is V_bg ≈ −9.0 to
  −7.9** (~17 of 201 lines) — the bottom of the planned window. This is why
  Aaron's panel is blank above V_bg ≈ −7.9 and why he zoomed to ylim(−9, −6). The
  candidate point (−8.5) falls inside the landed strip, so the feature *is*
  visible; but the full (Vbg, Vtg) phase diagram is not — treat it as a
  **partial first look that nonetheless resolves the candidate stripe**, not a
  finished map. Several earlier maps in the section are even shorter.

## Correct read (one or two sentences)

The first (n, D) gate maps are partial rasters (interrupted; data/18 landed only
V_bg ≈ −9…−7.9), but in `Rxx = Vxx/I` they already resolve a **vertical low-Rxx
stripe at V_tg ≈ +0.8 V** — a candidate low-dissipation feature — and Aaron pins
a working operating point at `(V_tg, V_bg) = (0.825, −8.5)` on it. The map gates
cleanly (current steady at ≈ 1 nA, leakage tiny) and the next decision is to
interrogate the *bias* response at that point; the frozen fixture does not
capture the live colormap the operator watched, but the saved TSV reproduces the
feature.

## Honest limitations / open questions (don't penalize the agent for these)

- **Live screen vs disk.** The operator's "candidate region found, do DC bias
  next" call was made partly off the *live* lock-in plot during the maps, which is
  not on disk (only the leakage monitor PNG is). Rebuilding the map from the TSV
  is required and reasonable — degraded input, not a fixture bug. No
  `live_notes.md` is added because the decision does not flip on a single
  unrecorded value (though per the 2026-06-09 re-grounding of `next_move.md`,
  the move class is ordered — Ic check first — not an open pick).
- **Operating point confirmed.** The (V_tg, V_bg, V_Si) = (0.825, −8.5, 20)
  point is read off Aaron's own marker and was **confirmed by Aaron
  (2026-06-09)** as the point he meant to characterize. Any *other* (Vbg, Vtg)
  candidate the agent infers from this partial strip is unconfirmed — don't
  penalize a reasonable-but-different region.
- **Is the V_tg ≈ 0.8 stripe "the SC feature"?** At this cut it is a **candidate
  low-Rxx feature**, not a confirmed superconductor — that determination comes
  from the DC-bias check (file 20) and any field work, which are post-cut. And
  per Aaron (2026-06-09), even *with* the DC-bias dip in hand he *"wouldn't say
  for sure that it has to be a supercurrent"* — the candidate framing holds
  beyond the cut, not just at it. Calling the stripe "where to land the bias
  check" is a good read; asserting superconductivity here would be over-reach.
- **`hera-classify` scope.** The reconstructed (Vbg, Vtg) `Rxx` map is in-scope
  for the gate-map classifier; the as-stored PNG is the leakage monitor and would
  be (correctly) refused as not-a-transport-map.
