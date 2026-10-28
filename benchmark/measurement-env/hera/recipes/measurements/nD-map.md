# nD map

## What
2D raster sweep over a polygon in physical `(n, D)`-space, executed as a
`multisweep` over precomputed `(V_tg, V_bg)` vectors. The polygon is
defined in `(n, D)` (typically a rectangle, sometimes a tilted
parallelogram), then `raster.rasterize` walks it on a regular grid and
`calc_tb` / `calculate_gate_voltages` projects each grid point into
`(V_tg, V_bg)` using cap ratios `dtg` / `dbg`. All lock-in channels read
at every grid point. Plots via
`sharpelab_nb.plotting.plot_gatemap(file_path, file, nD=True)`.

**Render.** Standard maps via `plot_gatemap(nD=True)`. For a *custom*
(n,D) panel (CNP overlay, candidate scatter, etc.), build it from
`raster.pcolorize_data(zs, vertices, nx, ny, fast_axis)` →
`pcolormesh(xs_mat, ys_mat, zs_mat)`.

For an axis-aligned rectangle in `(V_tg, V_bg)`-space (no cap-ratio
dependency, used as the first map of a fresh device), see `gatemap`. The
two recipes share external structure but differ in their sweep call and
their cap-ratio dependency.

## When
After a `gatemap` has confirmed the cap ratios are sane and (preferably)
after `cap-ratio-calibration` has refined them. The hard prerequisites
are stricter than `gatemap`'s: alongside the validators from
`gate-current-sanity-check`, **the cap ratios `dtg` / `dbg` must be
trusted** — a wrong slope places the polygon's `(n, D)` corners at the
wrong `(V_tg, V_bg)`, and on a strongly-coupled device the polygon can
walk *outside* the safe-gate rectangle even when the `(n, D)` extents
look conservative. `sanitize_tg_bg` mitigates this by clipping
out-of-validator points, but a polygon that needs heavy clipping is a
sign the caps are wrong, not that the clip is doing real work.

The standard arc:
1. `gatemap` — first map of the cooldown, axis-aligned. Sets the
   `(V_tg, V_bg)` bounding box, exposes the CNP line.
2. `cap-ratio-calibration` — fit the CNP slope from (1), refine
   `dtg` / `dbg`.
3. `nD-map` — the polygon you actually want, with caps you can trust.

Steps 2 and 3 can iterate (a small `nD-map` over a tiny polygon centered
on `(n=0, D=0)` is a good cap-ratio sanity check before committing to a
big map).

## Why
Three reasons to prefer `nD-map` over `gatemap` once caps are trusted:

1. **No wasted points.** A `(n, D)` rectangle of interest is typically a
   tilted parallelogram in `(V_tg, V_bg)`-space — the bounding rectangle
   wastes 30–60% of points outside the safe polygon. The rasterized
   polygon doesn't.
2. **Native `(n, D)` axes.** The data lands gridded in physical
   coordinates, no reprojection needed downstream. Plot heuristics, peak
   finders, line-cut definitions all simplify.
3. **Tunable polygon shape.** Once you know the device, the polygon can
   follow features — a long thin strip along a CNP line, a parallelogram
   tilted to the dome axis, a narrow wedge near a flavor transition. A
   rectangle in `(V_tg, V_bg)` can't do this.

The cost is the cap-ratio dependency. A wrong `dtg` / `dbg` projects the
polygon onto the wrong gates and the resulting map is uninterpretable
(the CNP doesn't land where you expect; features look stretched or
sheared). When in doubt, do a `gatemap` first.

## Recipe

1. Decide the `(n, D)` polygon. Typically a rectangle bracketing the
   feature of interest with margin: `n ∈ [-0.6e16, +0.6e16] cm⁻²`,
   `D ∈ [-0.68e9, +0.68e9] V/m` for an early survey on a 25.5/16 nm
   device. For a feature-targeted follow-up the polygon shrinks
   substantially.
2. Build cap-ratio constants in scope: typically `t_tg = 1.226 * t_bg`,
   `c_tg = calc_ctg(t_tg)`, `c_bg = calc_cbg(t_bg, t_bgSiO2)`. These
   *must* match the cap-ratio numbers blessed by
   `cap-ratio-calibration`. If you're freshly into the session and
   trusting numbers from a prior cooldown, note that in the comments.
3. Rasterize the polygon and project to gate voltages:
   ```python
   verts = np.array([[n0, D0], [n1, D1], [n2, D2], [n3, D3], [n0, D0]])
   xs, ys = raster.rasterize(verts, 401, 401, 0, rev_x=False, rev_y=False)
   vtg_vec, vbg_vec = calc_tb(xs, ys, c_tg, c_bg, n_offset=0, D_offset=0)
   # Or, on Aaron's RPL_19 stack:
   #   Vtgs, Vbgs = calculate_gate_voltages(xs, ys, dtg=..., dbg=..., ep=3)
   ```
4. Clip to the gate validators. `sanitize_tg_bg(vtg_vec, vbg_vec, tg_lims, bg_lims)`
   returns `(vtg_new_vec, vbg_new_vec)` with out-of-range points dropped.
   Print the before/after counts; >5% clipping means revisit the
   polygon or the caps.
5. **Validate the polygon visually before running.**
   `plt.scatter(vtg_vec, vbg_vec, ...)` or
   `sharpelab_nb.plotting.plot_raster_preview(verts, 401, 401, nD=True, dtg=..., dbg=..., ep=3)`
   — pass this device's `dtg`/`dbg`/`ep` — confirms every traversed
   point lies inside the gate validators. This
   step is cheap and catches the "caps are wrong, polygon is outside
   the safe rectangle" failure mode before you commit hours of sweep
   time.
6. Build `s = sweep.AsyncStation(mc)`. `s.add_comment('nD-map')` first,
   then optional structured tags identifying the operating point and
   polygon: `s.add_comment(f'MC{N}, Vsi = {V_si}V, n ∈ [{n_lo}, {n_hi}], D ∈ [{D_lo}, {D_hi}]')`.
   Call `s.add_comment(grab_metadata())` if available.
7. `s.ramp` all relevant gates and the field to start values.
   `time.sleep(10)` settle. (Per Isaac's RPL_19 idiom, an `s.reset()`
   between Station construction and the sweep is reasonable when the
   prior cell already ramped to the polygon start — it skips the
   redundant ramp.)
8. `fp` temperature(s), all three gate currents, and every lock-in `X`
   and `P`. `plot` `k_bg.volt` vs `k_bg.curr`, `'time'` vs `k_tg.curr`,
   plus `k_bg.volt` vs each lock-in `X` for live feature-tracking. (For
   Isaac's idiom: `xp = k_bg.volt; s.plot(xp, sr830_8.X)`.)
9. (Optional) `s.register_run_before(autorange_sr830s, ...)` if you
   want sensitivity to track. Same caveat as `gatemap` — autorange
   disturbs lock-ins mid-row; leave commented out for clean maps. With
   autorange off, set a fixed sensitivity sized to the **largest** R you
   need to resolve, folding in the voltage preamp gain G from the card
   (sens ≳ R_max × I_ac × G, ~×2 headroom) — same sizing as `gatemap`
   step 5.
10. `s.multisweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], delay=1.2)`.
    Delay matches the lock-in time-constant ladder (3 × TC is the rule
    of thumb); 1.0–1.5 s is the typical band.
11. Park gates: `s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)`. Send a
    Discord/Slack ping if the alert hooks are installed.

## Verify

The map is unrolled into flat rows like `gatemap`'s, with the same
column-wise statistics. The new wrinkle: confirm the polygon was
actually traversed (rather than the validator clipping having silently
trimmed most of it).

```python
from hera.analysis import open_run, summarize_run
import numpy as np

run = open_run("<notebook_dir>/data/<file_id>")
print(summarize_run(run))
# expect: type 2D, recipe 'nD-map', complete, tags carrying polygon extents.

# 1. Sweep completeness.
assert not run.interrupted, "sweep was interrupted; investigate"

# 2. Polygon traversal — k_tg_volt and k_bg_volt should span the expected
#    extents (allowing for sanitize_tg_bg clipping). col() resolves the
#    swept-also-fp'd duplicate to the planned setpoint column.
vtg_planned = run.col("k_tg_volt")
vbg_planned = run.col("k_bg_volt")
print(f"V_tg traversed: {vtg_planned.min():.3f} → {vtg_planned.max():.3f}")
print(f"V_bg traversed: {vbg_planned.min():.3f} → {vbg_planned.max():.3f}")
# Compare to the validators / planned polygon — anything tighter than
# expected means sanitize_tg_bg clipped, which means the caps may be off
# or the polygon over-reached.

# 3. Leakage — same threshold as gatemap.
i_tg_max = np.abs(run.col("k_tg_curr")).max()
i_bg_max = np.abs(run.col("k_bg_curr")).max()
assert i_tg_max < 1e-9 and i_bg_max < 1e-9, (
    f"leakage exceeded 1 nA: |I_tg|={i_tg_max:.3e}, |I_bg|={i_bg_max:.3e}"
)

# 4. Lock-in channels not stuck or NaN.
for name in run.cols:
    if not (name.startswith("sr830_") and name.endswith("_X")):
        continue
    x = run.col(name)
    if np.allclose(x, x[0]):
        raise RuntimeError(f"{name} is flat across the map — lock-in / wiring")
    if np.isnan(x).any():
        raise RuntimeError(f"{name} has NaNs — sweep aborted mid-row?")

# 5. Eyeball plot.png. The (n, D) projection should land features at
#    physically-meaningful coordinates — CNP at n=0, dome centroids at
#    plausible D. If the CNP is offset from n=0, the cap ratios are
#    likely wrong: kick back to cap-ratio-calibration before any further
#    nD-map work.
```

The CNP-at-n=0 check in step 5 is the most useful sanity gate this
recipe has: a clean `nD-map` whose CNP doesn't land at `n=0` is the
clearest signal that `cap-ratio-calibration` should run (or re-run)
before the next sweep.

## Examples
- `isaac/b1c2_toploader/20260415_measure.ipynb` cells 113–153 — canonical
  Flavor B with iterative noise reduction across four versions: full nD
  (cells 113–122), zoom-in (123–134), zoom-in with theta/phi sin-out off
  (135–141), zoom-out with thermometer + heater unplugged (142–147),
  zoom-in with same (148–153). Each iteration is structurally identical:
  (1) `meas_config = {...}` dict with a `comment` field; (2)
  `s = sweep.AsyncStation(meas_config)` + fp/plot block; (3)
  `t_bg, t_tg, c_tg, c_bg = ...` capacitance setup; (4)
  `vertices = np.array([...])` `(n, D)` parallelogram; (5)
  `xs, ys = raster.rasterize(vertices, 401, 401, 0, ...)`; (6)
  `vtg_vec, vbg_vec = calc_tb(xs, ys, ...)`; (7)
  `vtg_new_vec, vbg_new_vec = sanitize_tg_bg(...)`; (8) validators; (9)
  `s.multisweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], delay=1.2)`.
  No `s.add_comment` calls — Isaac uses the `comment` field of
  `meas_config` instead, which preserves intent in metadata but is not
  the same surface as `add_comment`. Recipe asks for `add_comment` going
  forward (now with the slug `'nD-map'`); Isaac's iterative-noise-
  reduction sequence is otherwise the cleanest example in the corpus of
  "what to do when your first map is too noisy" — unplug noise sources
  one at a time and re-sweep.
- `aaron/RPL_10/241230_measure.ipynb` cells 22–28 — early example in
  finite-field context (the polygon `[[-0., -9], [-4.5, -2], [-4.5, 5], [-0.5, 5], [2, 1.5], [2, -9]]`
  is a tilted hexagon used for ±100 mT pair sweeps). Same shape:
  `from sweep import raster`, `raster.rasterize(...)`,
  `calculate_gate_voltages(xs, ys)`, `s.multisweep([k_tg.volt, k_bg.volt], [Vtgs, Vbgs], delay=1)`.
  Comment string `'MC4, Vsi = -20V, B = ±100 mT'` is parseable.

## Next
- **CNP doesn't land at n=0 in the rendered map**: kick back to
  `cap-ratio-calibration`, refit, re-run.
- **Polygon clipped heavily by `sanitize_tg_bg`** (>5% of points dropped):
  caps may be wrong; revisit `cap-ratio-calibration`. Or polygon over-
  reached — narrow it.
- **Map is too noisy to read features**: walk Isaac's noise-reduction
  ladder — disconnect rotator excitations, unplug fridge thermometer +
  heater, increase `delay` toward 3 × TC, narrow the polygon for higher
  effective density.
- **Features look interesting**: branch by question, same as `gatemap`.
  `gatemap-in-field` for finite-field maps; `field-sweep-1d` or
  `gate-axis-linecut` for 1D feature characterization;
  `hysteresis-check` for history-dependence; `gatemap-feature-locator`
  for a ranked candidate list.
- **Want a denser version of the same polygon**: bump 401 → 601 grid
  density, raise `delay` to 1.5 s, accept the wall-clock cost.

Block 2: `landau-fan`, `temperature-dependence`; deferred: `fraunhofer`,
`bias-spectroscopy` — same as for `gatemap`.
