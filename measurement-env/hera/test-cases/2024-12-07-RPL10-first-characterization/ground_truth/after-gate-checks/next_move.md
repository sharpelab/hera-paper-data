# Ground truth — next move at the frontier (cut idx 42)

*What the operator actually did in the next section (`# Gatemap`, cells 43–54).
One expert path, not the only answer — used to route the replay to human review,
never as an exact-match score.*

> **Expert-confirmed 2026-06-09 (Aaron, review card).** Move capture "probably
> correct"; the not-contested + depth framing confirmed: *"Yes, the obvious
> thing is to start doing nD maps, start coarse then go fine."* Coarse→fine is
> his stated convention — a useful anchor for the quick/deep contrast below.

## The move: `# Gatemap` — first (n, D) transport map

After confirming the gates are alive and leak-free, the operator's next
experiment was the **first 2D transport gate map** over the validated window:

- `s.megasweep(k_bg.volt, np.linspace(-9., 5, 201), k_tg.volt, np.linspace(-5.5, 6, 201), slow_delay=3, fast_delay=1)`
  → **`data/9/`** (cell 44, comment `initial gatemap, V_si = 10`). Slow axis:
  back gate −9 → 5 V (201 pts). Fast axis: top gate −5.5 → 6 V (201 pts). The
  full set of lock-ins is followed (`sr830_4` = current channel, gain −1e6).
- Followed immediately by several more maps refining the window and stepping the
  Si back gate: V_Si = 10, −10, 20 V (cells 45–53 → data/10–18), each a
  ~201×201 (Vbg, Vtg) `megasweep` with `slow_delay=3, fast_delay=1`.

## Why this is the right next step

The gate checks established only that the device is **gate-able** (current
applies, no runaway leakage, breakdown beyond the working window). They reveal
nothing about *transport* — where the device conducts, where the CNP sits, where
correlated/SC features live. The canonical first transport measurement on a
fresh dual-gated 2D device is a **2D (Vbg, Vtg) → (n, D) map**: it locates the
charge-neutrality point, the band edges, and any features in one shot, and it
sets up every downstream decision (where to sit for DC bias, field, etc.). The
operator also varies V_Si to find the most informative global-back-gate setting.

## Class for judging

- **Same experiment:** propose a 2D (Vbg, Vtg) / (n, D) transport gate map over
  the validated window at base T. (Exact grid, delays, and V_Si choice are
  parameter-level — and are exactly what the **depth** level should move.)
- **Same class, different params:** an (n, D) map taken via an n/D-parameterized
  sweep instead of raw (Vbg, Vtg); a narrower-but-finer first map; a single V_Si
  rather than a sweep of V_Si.
- **Different but reasonable:** a coarse 1D line cut (e.g. Vbg at fixed Vtg)
  first to pick a map window before the 2D map — defensible as a recon step,
  especially under a *quick* depth.
- **Divergent / worse:** jumping straight to DC bias / field / Fraunhofer with
  no transport map to choose an operating point; re-running gate-leakage checks;
  proposing nothing measurable.

## Depth contrast (this is the point of the frontier)

The *experiment* is fixed (a first (n, D) map). What should move with the depth
level is the **execution**:
- **quick** — coarse grid (fewer points per axis), short/zero settle delay,
  single pass, maybe one V_Si — just enough to see if the device conducts and
  roughly where the CNP and features are.
- **deep** — finer grid, RC-aware `slow_delay`/`fast_delay` (the operator used
  3 s / 1 s), resolution sufficient to locate the CNP and feature edges; may
  step a couple of V_Si values.
- **paper** — high-resolution, averaged, reproducible map suitable for a figure;
  repeats / drift checks.

A good result is that the proposed grid / delay / coverage swings substantially
with the depth level while the sweep *call* stays the same shape. If it doesn't,
the agent isn't internalizing the rigor signal.
