# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/1944/` (the rough nD map, cell 51 of the
served notebook), the freshest result at the frontier. Used to score the
perception layer (A) independently of the decision layer (B).*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of `data/1944` in `20260217_ana.ipynb` **cell 140**
> (`files = [1944]`, section `# After power loss`), not from the raw TSV +
> `metadata.json` + the leakage-only `plot.png`. The prior version **drifted**:
> it claimed the transport map "is **not** in `plot.png`" and could only be read
> from the TSV, that "the current channel (`sr830_4_X`) is comparatively uniform
> … so the contrast lives in the voltage channels," and that the structure is
> only "roughly resolved." Aaron's actual cell forms **`Rxx = sr830_{1,2,3}_X /
> sr830_4_X`** (sr830_4 is the *current*, the denominator — not a transport
> channel) and pcolormeshes a clean `Rxx(n, D)` map that clearly resolves a
> low-n band-edge wall and feature structure in the positive-D corner. Figures:
> `../figures/ana_1944_rough-nd-map_sr830_{1,2,3}.png`; the prior-section AHC
> zoom (negative D) is `../figures/ana_1933_negD-ahc-zoom_sr830_2.png`.

## What the sweep is

`s.multisweep([k_tg.volt, k_bg.volt], [raster_vtgs, raster_vbgs], delay=1)`
(`function: multisweep`, `mc_31`, comment `MC31, Vsi = 48V`).

- **What it maps:** a **rasterized (n, D) map at positive D**. The served notebook
  builds the raster from a polygon with vertices `n = [0.2, 0.72, 2.0, 2.0, 0.2]`,
  `D = [1.018, 1.065, 0.949, 0.70, 0.70]` V/nm at `nx, ny = 101, 101`, oversample
  flag 0, `rev_y=True` — a **coarse** scan. Gate voltages are computed from (n, D)
  via `calculate_gate_voltages(n, D, dtg=17.25, dbg=25.5)`, so `k_tg` and `k_bg`
  are driven together along the raster path.
- **Confirmed extent (from the TSV / map axes):** `n ∈ [0.2, 2.0]` (×10¹² cm⁻²),
  `D ∈ [0.70, 1.065]` V/nm. `k_si` held at +48 V.
- **Channels (mc_31):** current on `sr830_4` (`I_{30-21}`, gain −1E6); four-terminal
  voltages on `sr830_1 = 29-28`, `sr830_2 = 28-25`, `sr830_3 = 25-24` (gain 100).
  `sr830_5…9` are n.c. (Cell 140 plots the three voltage pairs — "long bot" —
  as `Rxx`.)
- **How Aaron reads it (cell 140):** `I = sr830_4_X`, `Vxx = sr830_{1,2,3}_X`,
  **`Rxx = Vxx / I`**; convert (Vtg, Vbg) → (n, D) with `calculate_n_D(dtg=17.25,
  dbg=25.5)`; `raster.pcolorize_data(..., 101, 101, 0, rev_x=False, rev_y=True)`;
  `pcolormesh(Rxx)` on a SymLog scale (linthresh 100, vmin 0, vmax 1e5 Ω).
- **Temperature:** base, T ≈ 0.028–0.031 K (~28–30 mK) — the characterization
  context.
- **Field:** nominally zero (a zero-field map).

So this is a **coarse (n, D) transport map of the positive-D landscape** taken
right after a power loss, to confirm the device survived and locate where the
interesting structure sits.

## What it shows (floor — the must-see findings)

(Read directly from Aaron's `Rxx(n, D)` pcolormesh in cell 140 — see the three
`ana_1944_rough-nd-map_*` figures, one per voltage pair.)

- **`sr830_4` is the current, not transport.** It is the **denominator** in
  `Rxx = Vxx / I`. Reading a "signal" *out of* sr830_4, or calling it "uniform
  contrast that lives in the voltage channels," is the mistake — using it as `I`
  is correct.
- **A high-Rxx band-edge wall at low n.** All three voltage pairs show a bright
  (~10⁴–10⁵ Ω) high-resistance wall at **low density (`n` ≲ 0.4 ×10¹²)**, running
  across the full D range — the band-insulating / charge-neutral edge of the map.
- **Resolved feature structure in the low-n, positive-D corner.** Just inside that
  wall, at **`n ≈ 0.4–0.7` and `D ≈ 0.75–1.05` V/nm**, there is clear
  low-Rxx / structured contrast (dark streaks and patches on `25-24` and `28-25`,
  greenish mid-Rxx structure on `29-28`) — the corner where this device's SC dome
  / anomalous-Hall (AHC) region is known to live from prior cooldowns. The map is
  coarse, so this localizes the structure *roughly* but does not pin feature edges.
- **Metallic background at high n.** Toward higher density (`n` ≳ 1) the map fades
  to a uniform low-Rxx (~10²–10³ Ω) metallic background — the device passes current
  everywhere swept (consistent with the post-power-loss gate checks: no leakage).

## Correct read (one or two sentences)

A coarse positive-D `Rxx(n, D)` map (Rxx = Vxx/I, sr830_4 = current) confirms the
device survived the power loss and is conducting across `n ∈ [0.2, 2.0]`, `D ∈
[0.70, 1.065]`, with a high-Rxx band-edge wall at low n and **structured low-Rxx
features in the low-n (n ≈ 0.4–0.7), positive-D (D ≈ 0.85–1.05) corner** — the
known SC/AHC region. It establishes *that* there is interesting structure and
*roughly where* — but it covers only a thin high-D sliver (`D ≥ 0.70`), so most
of the (n, D) plane (the charge-neutrality line, the negative-D side) is unmapped;
extending the map's range to cover the full reachable landscape is the obvious
next step.

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows only gate leakage, not transport.**
  `data/1944/plot.png` plots the registered live-monitor channels (`k_bg_curr`
  vs `k_bg_volt`, `k_tg_curr`/`k_si_curr` vs time), all essentially flat (good:
  no gate leakage). The actual `Rxx(n, D)` structure is **not** in the saved PNG —
  it requires forming `Rxx = sr830_{1,2,3}_X / sr830_4_X` from the TSV (which is
  exactly what Aaron's ana cell does). An agent that only looks at the on-disk PNG
  legitimately sees "no feature"; reconstructing Rxx is the correct sub-step —
  flag, don't penalize.
- **Rasterized scatter, not a regular grid.** The map is a polygon raster
  (scattered (n, D) points gridded via `pcolorize_data`), so a few interior
  pixels are dropouts (white). "Structure concentrated at low n / positive D" is
  the legible floor, not a precise phase boundary.
- **Physics labels are reviewable — flag for Aaron.** Calling the
  low-n/positive-D structure the "SC dome / AHC region" leans on this device's
  history (prior cooldowns mapped an SC dome and AHC there), not on anything a
  single coarse zero-field Rxx map proves. An agent that says "elevated-resistance
  band-edge plus structured low-Rxx features in the low-n/positive-D corner,
  likely the known SC/AHC region — needs a finer map to confirm" is reading it
  correctly. **Open question for Aaron:** is the structure at n ≈ 0.4–0.7 here the
  SC dome, the AHC/CSC region, or both, and does the band-edge wall position
  (n ≈ 0.3–0.4) match expectation for this cooldown?
- **Field zero is trapped flux, not an instrument zero.** The map is at "nominally
  zero field," but per Aaron (2026-06-05) the perpendicular null on this rig is
  **trapped flux: cooldown- and field-history-dependent, and it moves after large-
  field excursions** — so "zero field" means "the current trapped-flux null," not
  an absolute B = 0. Don't read an absolute field from this map.
- **Out of `hera-classify` scope as-is.** This is an (n, D) transport map (in the
  classifier's domain), but the saved `plot.png` is the leakage monitor — the
  classifier would need the re-formed `Rxx(n, D)` map, not the on-disk PNG.
