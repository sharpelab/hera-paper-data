# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around this frontier so a future
harness can pose the second test: **given a raw sweep, can HERA (a) reproduce the
analysis Aaron did, and (b) produce the result he drew from it?** This is the
analysis-layer analogue of the next-move test — one turn back, with Aaron's ana
notebook (`20260217_ana.ipynb`) as ground truth.

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id (loads
via `sl.pload`, forms `Rxx = sr830_{1,2,3}_X / sr830_4_X`, converts the gate axes
to (n, D), rasterizes the polygon onto a grid, pcolormeshes `Rxx(n, D)`). The
expected output is the matching figure under `../figures/`. The harness will need
plotting tooling + a data loader (`easyload`/`sl.pload`) + the `sweep.raster`
helpers (`pcolorize_data`) and the notebook's `calculate_n_D` /
`calculate_gate_voltages` (n,D) helpers wired for HERA — TBD.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/1933` | `method_1933.py` (cell 136) | `ana_1933_negD-ahc-zoom_sr830_2.png` | **Prior section, pre-power-loss.** A *negative*-D (n, D) zoom on the device's AHC corner (n ∈ [0.2, 0.8], D ∈ [−0.4, −0.8]): high-Rxx ridge structure plus an antisymmetric-Rxx (Hall-like) signal — the kind of resolved (n, D) map the campaign aims for. Context for "we already know how to map this device." |
| `data/1944` | `method_1944.py` (cell 140) | `ana_1944_rough-nd-map_sr830_{1,2,3}.png` | **The rough nD map at the cut (latest sweep).** `Rxx(n, D)` over n ∈ [0.2, 2.0], D ∈ [0.70, 1.065] V/nm, 101×101 coarse raster. Shows a high-Rxx band-edge wall at low n (n ≲ 0.4, Rxx ~1e4–1e5 Ω) and **resolved low-Rxx / feature structure in the low-n (n ≈ 0.4–0.7), positive-D (D ≈ 0.75–1.05) corner**, fading to a uniform metallic background (~10²–10³ Ω) at high n. Device survived the power loss and conducts everywhere; structure is legible but coarse. See `../reading.md`. |
| `data/1945` | `method_1945.py` (cell 141) | `ana_1945_broaden-map_sr830_{1,3}.png` | **The next move (broaden map).** Same Rxx pipeline, polygon **extended in D down to −0.4 V/nm** (n to 1.8) — a coverage extension capturing the full reachable landscape (the rough map stopped at D = +0.70). Resolves the charge-neutrality line near D ≈ −0.1 to −0.2 and fan-like feature lines across (n, D). The grid is also denser (201×251), but the *move* is the coverage extension, not resolution. *Post-cut — answer-key only. Swept n-first, this map streaks in the positive-D corner — the basis for the `after-broaden-map` frontier.* |

**Leakage note:** `data/1945` is post-cut for *this* frontier (the answer-key
broaden map; it is in the **next** frontier's allowlist). It belongs to
the analysis-reproduction ground truth and to the human review card, **never** to
the served (≤ cut) workdir. `data/1933` and `data/1944` are pre-cut (1944 is in
the frontier allowlist; 1933 is prior-cooldown-section context). The on-disk
`data/1944/plot.png` is only the **gate-leakage monitor** (flat `k_*_curr`), not
the transport map — the transport read above comes from Aaron's ana cell, not the
saved PNG.

## Open design question (for the later harness)
The analysis test needs HERA to *run* code (load, form Rxx, build the (n, D)
axes, rasterize, plot), so it requires a tool surface the next-move test doesn't:
a data loader + matplotlib + the `sweep.raster` + (n,D)-conversion helpers + a way
to compare its figure/result to Aaron's. Scoring is likely "does it form `Rxx =
sr830_{1,2,3}_X / sr830_4_X` correctly (the sr830_4-as-current insight), build the
(n, D) axes, and read the low-n/positive-D structure," judged against the result
column — not pixel match.
