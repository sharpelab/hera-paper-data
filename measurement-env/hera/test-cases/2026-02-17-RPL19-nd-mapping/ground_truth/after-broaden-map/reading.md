# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/1945/` (the broaden map, cell 55 of the served
notebook), the freshest result at the `after-broaden-map` frontier. Used to score
the perception layer (A) independently of the decision layer (B). The decisive
thing to see here is the **streaking artifact** — it is what motivates the next
move.*

> **Grounded 2026-06-08** by re-rendering Aaron's own analysis pipeline
> (`Rxx = sr830_{1,2,3}_X / sr830_4_X`, (n,D) axes via `calculate_n_D(dtg=17.25,
> dbg=25.5)`, `raster.pcolorize_data` at 201×251, SymLog norm linthresh 100) on
> `data/1945`. Figure: `../figures/ana_1945_broaden-map-nfirst_streaky.png`
> (three voltage pairs).

## What the sweep is

`s.multisweep([k_tg.volt, k_bg.volt], [raster_vtgs, raster_vbgs], delay=0.9)`
(`function: multisweep`, `mc_31`, comment `MC31, Vsi = 48V`).

- **What it maps:** a large-area **(n, D) map**, swept **n-first** (the density
  axis is the fast variable). Polygon vertices `n = [0.2, 0.72, 1.8, 1.8, 0.2]`,
  `D = [1.018, 1.065, 0.949, −0.4, −0.4]` V/nm at `nx, ny = 201, 251`, oversample
  flag 1, `rev_y=False`.
- **Confirmed extent:** `n ∈ [0.2, 1.8]` (×10¹² cm⁻²), **`D ∈ [−0.4, 1.065]`**
  V/nm — i.e. the previous rough map's thin positive-D sliver (`D ≥ 0.70`)
  **extended all the way down through D = 0 to −0.4**. `k_si` held at +48 V.
- **Channels (mc_31):** current on `sr830_4` (`I_{30-21}`, gain −1E6); four-probe
  voltages on `sr830_1 = 29-28`, `sr830_2 = 28-25`, `sr830_3 = 25-24` (gain 100).
- **How to read it:** `I = sr830_4_X`, `Vxx = sr830_{1,2,3}_X`, **`Rxx = Vxx/I`**;
  convert gates → (n, D); pcolormesh on SymLog.
- **Temperature / field:** base T (~28–30 mK); field at the trapped-flux null.

## What it shows (floor — the must-see findings)

(Read from the re-formed `Rxx(n, D)` map — see `ana_1945_broaden-map-nfirst_streaky.png`.)

- **`sr830_4` is the current, not transport** — the denominator of `Rxx = Vxx/I`.
- **Full-range landscape now in view.** Extending D to −0.4 captures (i) a bright
  **charge-neutrality / band-edge line near `D ≈ −0.1` to −0.2** running across
  the map, (ii) fan-like **constant-D feature lines** through the positive-D
  half, and (iii) the low-n / positive-D corner structure (the known SC/AHC
  region) — plus a metallic low-Rxx background at high n. The broaden move
  succeeded in its goal: the device's reachable (n, D) range is mapped in one
  sweep.
- **Streaking in the high-Rxx positive-D corner (the key defect).** Because the
  map is swept **n-first**, the bright high-Rxx positive-D corner shows
  pronounced **fast-axis streaks** — vertical/diagonal bands of scattered
  high/low Rxx that smear the feature edges there. This is a **sweep-ordering /
  RC-settling artifact**, not physics: the same region re-swept D-first
  (`data/1946`, the next move) resolves into clean continuous feature lines.

## Correct read (one or two sentences)

A large-area `Rxx(n, D)` map (Rxx = Vxx/I, sr830_4 = current) that extends the
prior positive-D sliver down to D = −0.4, capturing the charge-neutrality line,
constant-D feature lines, and the low-n/positive-D corner — i.e. the full
reachable landscape in one sweep. **But, swept n-first, the high-Rxx positive-D
corner streaks along the fast axis** (a settling/sweep-ordering artifact), so the
feature structure there is smeared and the natural next step is a D-first re-sweep
to clean it up.

## Honest limitations / open questions (don't penalize the agent for these)

- **The on-disk `plot.png` is the leakage monitor, not the map.** As with
  `data/1944`, the streaks/structure require re-forming `Rxx` from the TSV.
- **"Streaks" vs "hysteresis."** A correct read calls the corner artifact a
  sweep-ordering/settling effect (fast-axis-aligned) rather than a physical
  feature; distinguishing it from genuine hysteresis is exactly what the
  forward/reverse D-first pair (`data/1946`/`1947`) is for. An agent that notes
  "the positive-D corner looks streaky/under-settled, likely a fast-axis
  artifact" is reading it correctly.
- **Physics labels are reviewable.** Calling the low-n/positive-D structure the
  SC/AHC region leans on this device's history, not on this zero-field map alone.
- **Trapped-flux null.** "Zero field" is the current trapped-flux null
  (cooldown- and history-dependent), not an absolute B = 0.
