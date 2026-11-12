# Gatemap

## What
2D raster sweep over an axis-aligned rectangle in `(V_tg, V_bg)`-space at
zero field, via `s.megasweep(k_tg.volt, ..., k_bg.volt, ...)`. All lock-in
channels read at every grid point; gate-current channels monitored for live
leakage. The first map you take when cap ratios `dtg` / `dbg` are not yet
trusted — sweeping in raw gate voltages avoids any `(n, D) ↔ (V_tg, V_bg)`
calibration error. Plots via
`sharpelab_nb.plotting.plot_gatemap(file_path, file, nD=True)` (the analysis
side reprojects to physical `(n, D)` after the fact, using the cap ratios
in scope at plot time — separate from the sweep itself).

For the polygon-in-`(n, D)` variant (rasterized parallelogram via
`raster.rasterize` + `multisweep`), see `nD-map`. The two recipes share
external structure (AsyncStation, fp/plot, comments) but differ in their
sweep call and their cap-ratio dependency.

## When
Once the device-init validators are in place: hard dependency is
`gate-current-sanity-check` with Cell B committed (the safe `(V_tg, V_bg)`
ranges define the maximum extent of the megasweep box) and, for
rhombohedral devices, `silicon-backgate-survey` (`V_si` is held at the
operating point this gatemap commits to). A `gate-leakage-survey` should
have been done already — or, for any gatemap that ventures far from
`(0, 0)`, have a leakage-check `register_run_before` callback installed
(see `gate-leakage-survey` Flavor B). After the first gatemap is in hand,
the campaign branches by scientific question (see `## Next`).

The natural predecessor of `nD-map`: a clean axis-aligned gatemap is the
substrate from which `cap-ratio-calibration` extracts the CNP slope, which
is what makes a polygon-in-`(n, D)` sweep trustworthy.

## Why
The gatemap is the only measurement in the toploader pipeline that surveys
the gate plane densely without committing to a particular feature or to a
particular set of cap ratios. Every downstream Block 1 recipe targets a
specific point or line — and you can only pick one if you've seen the
map. A 201×201 megasweep at `slow_delay=3, fast_delay=1` is the densest
first-look you can get without dropping into rasterized-polygon sweeps
(`nD-map`); price the wall-clock from the rig card's Timing rules.

The axis-aligned form has two failure modes the polygon form doesn't:
(1) it wastes 30–60% of points outside the safe polygon when the
`(n, D)` region of interest is a tilted parallelogram, and (2) on a
device with strongly-coupled top/bottom gates, a rectangle in
`(V_tg, V_bg)` is a sheared parallelogram in `(n, D)` and the CNP cuts
the rectangle diagonally. Both are worth tolerating on the *first* map,
because the alternative requires cap ratios you don't yet trust.

## Recipe

1. Decide the `(V_bg, V_tg)` extent. Stay strictly inside the validators
   set by the device-init recipes; for a first gatemap pick a rectangle
   that brackets the working setpoint with margin (e.g.
   `V_bg ∈ [-8, 6.5]`, `V_tg ∈ [-6.5, 6.5]` for a 25.5/16 nm device at
   `V_si = 48 V`).
2. Build `s = sweep.AsyncStation(mc)`. `s.add_comment('gatemap')` first,
   then optional structured tags identifying the operating point, e.g.
   `s.add_comment(f'MC{N}, Vsi = {V_si}V')`. Call
   `s.add_comment(grab_metadata())` if the notebook has the helper (RPL_19
   idiom — captures device/run state into the comments list).
3. `s.ramp` all relevant gates and the field to their start values.
   `time.sleep(10)` (or `interruptible_sleep(30)` for a slower settle when
   `V_si` just moved).
4. `fp` temperature (and `fridge_temperature` if available), all three
   gate currents, and every lock-in `X` and `P`. `plot` `k_bg.volt` vs
   `k_bg.curr` and `'time'` vs `k_tg.curr` / `k_si.curr` so live leakage
   is visible; for a survey gatemap also `s.plot(k_bg.volt, sr.X)` over
   each lock-in.
5. (Optional) `s.register_run_before(autorange_sr830s, [sr830s_2_autorange])`
   if you want sensitivity to track during the slow axis. Aaron typically
   leaves this commented out for the canonical 201×201 — autorange
   disturbs the lock-ins mid-fast-row. With autorange off (the canonical
   choice), set each voltage lock-in's sensitivity to the **largest
   resistance you need to resolve**, and fold in the voltage preamp gain G
   from the card: the lock-in sees V_xx×G, so a sensitivity sized from the
   bare V_xx under-ranges by G and clips R_max. Use sens ≳ R_max × I_ac × G
   with ~×2 headroom.
6. `s.megasweep(k_tg.volt, np.linspace(V_tg_lo, V_tg_hi, 201), k_bg.volt, np.linspace(V_bg_lo, V_bg_hi, 201), slow_delay=3, fast_delay=1)`.
   Slow-axis convention varies — Aaron's recent style is TG slow, BG
   fast (cf. RPL_19/20251220 cell 70); RPL_10/241207 used BG slow, TG
   fast. Either works; the analysis-side `plot_gatemap(..., nD=True)`
   reprojects to `(n, D)` regardless.
7. Park gates: `k_bg.volt(0); k_tg.volt(0)`. (Don't park `V_si` unless
   you're done with this `V_si` entirely.) Send a Discord/Slack ping
   (`alerts.discord('🐍jobs done🐍')`) if the alert hooks are installed.

## Verify

Post-hoc disk checks. The map's `data/<file_id>/` directory has
`metadata.json`, `data.tsv.gz`, and `plot.png`. The `Run` loader unrolls
the 2D megasweep into flat rows, so column-wise statistics work the same
way they do for 1D sweeps.

```python
from hera.analysis import open_run, summarize_run
import numpy as np

run = open_run("<notebook_dir>/data/<file_id>")
print(summarize_run(run))
# expect: type 2D, recipe 'gatemap', complete (rows == n_slow * n_fast),
#         tags carrying MC label / Vsi.

# 1. Sweep completeness — interrupted sweeps usually mean leakage abort or
#    operator stop; treat as block until the human explains.
assert not run.interrupted, "sweep was interrupted; investigate before advancing"

# 2. Leakage stayed below threshold across the whole map. Threshold matches
#    the gate-leakage-survey abort thresholds (~5e-11 to 8e-11 A); use 1 nA
#    as a soft ceiling and surface anything closer than 100 pA.
i_tg_max = np.abs(run.col("k_tg_curr")).max()
i_bg_max = np.abs(run.col("k_bg_curr")).max()
assert i_tg_max < 1e-9 and i_bg_max < 1e-9, (
    f"leakage exceeded 1 nA: |I_tg|={i_tg_max:.3e}, |I_bg|={i_bg_max:.3e}"
)
if max(i_tg_max, i_bg_max) > 1e-10:
    print(f"⚠️  approaching leakage threshold: |I_tg|={i_tg_max:.3e}, |I_bg|={i_bg_max:.3e}")

# 3. Lock-in channels not stuck or saturated. Flat-zero or flat-nonzero on
#    every channel is the grounded-device failure mode (cf. gate-current-
#    sanity-check failure-mode catalog); flat anything is suspicious for a
#    map that's supposed to vary across (V_tg, V_bg).
for name in ("sr830_1_X", "sr830_2_X", "sr830_3_X", "sr830_4_X"):
    if name not in run.cols:
        continue
    x = run.col(name)
    if np.allclose(x, x[0]):
        raise RuntimeError(f"{name} is flat across the map — check lock-in / wiring")
    if np.isnan(x).any():
        raise RuntimeError(f"{name} has NaNs — sweep aborted mid-row?")

# 4. Eyeball the rendered plot — Read('<notebook_dir>/data/<file_id>/plot.png').
#    The gatemap's qualitative features (CNP line slope, dome shapes, flavor
#    transitions) are easier to assess visually than numerically; the
#    numeric checks above are necessary, not sufficient.
```

If a CNP-line extraction or feature catalog is needed downstream, defer
that to `gatemap-feature-locator` (separate recipe). The Verify block
here is just "is this map clean enough to advance from".

## Examples
- `aaron/RPL_19/20251220_measure.ipynb` cells 69–76 — canonical mature
  form. Cell 70 is the 201×201
  `s.megasweep(k_tg.volt, np.linspace(-6.5, 6.5, 201), k_bg.volt, np.linspace(-8, 6.5, 201), slow_delay=3, fast_delay=1)`
  at `V_si = 48 V` using `mc_9`; cell 71 reverses the slow axis (sweep
  direction check). Cell 72 is a markdown interlude ("THink there is a
  problem with a bnc t so swapping that out"); cell 73 retries cell 71's
  range. Cells 74–75 are silicon-backgate-survey forms (`V_si` as slow
  axis with `np.linspace(48, -48, 101)` — strictly belongs to
  `silicon-backgate-survey`, included here because the same `# Gatemap`
  markdown header parents them). Cell 76 is the same 201×201 at
  `V_si = -48 V`. The `add_comment('MC6, Vsi = -48V, gate map')` plus
  `add_comment(grab_metadata())` is the canonical comment idiom; this
  recipe's slug is now `gatemap` rather than the older `'gate map'`
  freeform string.
- `aaron/RPL_10/241207_measure.ipynb` cells 43–53 — first-cooldown form,
  predates the mature shape. Cell 43 is the markdown header; cells 44–53
  are 10 megasweeps over progressively-refined `(V_tg, V_bg)` rectangles
  at `V_si = +10, -10, +20 V`. Cell 44 omits the `s.ramp(k_si.volt, ...)`
  (V_si already at default); cells 46–47 add the explicit ramp + sleep.
  Cell 48 is `V_si = -10 V`; cells 51–53 are `V_si = +20 V`. Notable:
  each cell carries `s.add_comment('initial gatemap, V_si = 10')` —
  Aaron's `add_comment` discipline begins exactly here in this notebook
  (gate-checks at cells 22–42 had none). The autorange callback is
  commented out for these runs.

## Next
Default branches by what you saw on the map:
- **Cap ratios not yet trusted (or first cooldown of this device)**:
  `cap-ratio-calibration` — extract CNP slope from this gatemap, refine
  `dtg` / `dbg`. Required before any `nD-map` you want to trust.
- **Caps already trusted, want a denser polygon survey**: `nD-map` over
  the `(n, D)` parallelogram of interest.
- **No clear features at this V_si**: revisit `silicon-backgate-survey`
  for a different operating point.
- **Features visible, want them at finite field**: `gatemap-in-field`
  (the same shape with `s.ramp(mag.field, B)` first; bake settling time
  in for a strong magnet).
- **Specific point looks SC / AHC / flavor-transition-shaped**:
  `field-sweep-1d` to characterize how that feature responds to B at
  fixed gate; `gate-axis-linecut` for a denser 1D cut along an n- or
  D-line through the feature.
- **Suspect history dependence (asymmetric or noisy-looking gatemap)**:
  `hysteresis-check` along an n-line through the feature.
- **Want a ranked list of candidate features to follow up**:
  `gatemap-feature-locator` (HERA-side analysis).

Block 2 branches once Block 1 is exhausted: `landau-fan` (B × n at
fixed D), `temperature-dependence`; deferred: `fraunhofer` (B × bias at
fixed gate), `bias-spectroscopy`. Reach for these only after the
zero-field map is well-characterized.
