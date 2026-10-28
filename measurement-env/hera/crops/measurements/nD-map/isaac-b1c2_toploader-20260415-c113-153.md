> From `isaac/b1c2_toploader/20260415_measure.ipynb` cells 113–153.

# nD map

## full nD

```python
k_bg.nplci(1)
k_tg.nplci(1)
```

```python
t_bg = 20e-9
t_tg = 1.22594*t_bg
t_bgSiO2 = 0
c_tg = calc_ctg(t_tg)
c_bg = calc_cbg(t_bg, t_bgSiO2)
tg_lims = [-7, 6]
bg_lims = [-4, 4.4]

vertices = np.array([[-0.6e16, -0.68e9],
                    [-0.6e16, 0.68e9],
                    [0.6e16, 0.68e9],
                    [0.6e16, -0.68e9],
                    ])
xs, ys = raster.rasterize(vertices, 401, 401, 0, rev_x=False, rev_y=False)
vtg_vec, vbg_vec = calc_tb(xs, ys, c_tg, c_bg, n_offset = 0, D_offset=0)
vtg_new_vec, vbg_new_vec = sanitize_tg_bg(vtg_vec, vbg_vec, tg_lims, bg_lims)
print("Total number of points", len(vtg_vec))
print("Total number of points (sanitized)", len(vtg_new_vec))
```

```python
k_bg.volt.vals = validators.Numbers(-4,4.4)
k_tg.volt.vals = validators.Numbers(-7,6)
```

```python
meas_config = {
    "sr4" : "6 - 4",
    "sr4_gain" : -1e6,
    "sr5" : "5 - 30",
    "sr5_gain" : 1e2,
    "sr6" : "theta",
    "sr6_gain" : 1,
    "sr7" : "phi",
    "sr7_gain" : 1,
    "sr8" : "30 - 31",
    "sr8_gain" : 1e2,
    "bias_resistor" : 1e8,
    "bias_voltage_4" : sr830_4.amplitude(),
    "lockin_freq_4" : sr830_4.frequency(),
    "comment" : "bottom device",
}
```

```python
s = sweep.AsyncStation(meas_config)

s.fp(sr830_4.X).fp(sr830_4.P)
s.fp(sr830_5.X).fp(sr830_5.P)
s.fp(sr830_6.X).fp(sr830_6.P)
s.fp(sr830_7.X).fp(sr830_7.P)
s.fp(sr830_8.X).fp(sr830_8.P)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(k_tg.volt).fp(k_tg.curr)

xp = k_bg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_8.X)
```

```python
s.reset()
```

```python
s.multisweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], delay=1.2)
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
```

## zoom in

(Cells 123–134, structurally identical to cells 114–122 with a smaller polygon and a fresh `meas_config`. Per-iteration markdown header records what changed: this version is the first zoom-in.)

## zoom in, turn off theta and phi sin out

(Cells 135–141: same structure, but `sr830_6.amplitude(0.004)` is set to a low excitation in cell 134 before the run, and `time.sleep(3600)` in cell 140 lets the system thermalize after disconnecting the rotator excitation. The header documents the noise-source change.)

## zoom out, unplug theta and phi sin out, unplug fridge thermometer and heater

(Cells 142–147: same structure, with the fridge thermometer + heater physically unplugged. Outputs are visibly cleaner in the ana-side (n,D) plots than the prior iteration.)

## zoom in, unplug theta and phi sin out, unplug fridge thermometer and heater

(Cells 148–153: same structure, narrower polygon. Cell 153 has 225 KB of outputs — the largest cell in this nD map series, indicating a successful clean sweep at the chosen zoom level.)

This sequence is the only example in the corpus of "what to do when the first gatemap is too noisy." Each iteration changes exactly one thing — the zoom level, then a noise-source disconnect — and re-runs the same shape. The structural identity across the five iterations is the cleanest evidence in the corpus that the recipe is reusable: the only thing that varies between cells is the polygon vertices and the meas_config gain settings.

Notable departures from Aaron's mature form:
- **`raster.rasterize` + `multisweep`** instead of `megasweep` — Isaac uses a polygon in physical (n, D) coords (Flavor B) rather than an axis-aligned (V_tg, V_bg) rectangle (Flavor A). The polygon is `[[-0.6e16, ±0.68e9], [+0.6e16, ±0.68e9]]` — a rectangle in (n, D), but tilted in (V_tg, V_bg) because the gates are not orthogonal in the (n, D) basis.
- **`calc_tb` and `sanitize_tg_bg`** rather than `calculate_gate_voltages`. Same physics (capacitor model from `dtg`/`dbg`/`ep`); different function names. `sanitize_tg_bg` clips points outside the gate validators, returning the trimmed `(vtg_new_vec, vbg_new_vec)` that the multisweep actually traverses.
- **`meas_config` dict with a `comment` field** instead of `s.add_comment` — Isaac's idiom keeps the recipe-tag in the static config rather than in the `Station.comments` list. Recipe asks for `add_comment` going forward; Isaac's existing notebooks should be left alone since they're frozen sources.
- **fp on individual SR830s** by index rather than the `for sr, gain in sr830s:` loop. Functionally equivalent but means a recipe that says "fp every lock-in" needs to handle both surfaces.
- **`s.reset()` between AsyncStation construction and the multisweep** — a pattern Aaron uses inside the `## Bottom Gate (40 nm)` cell of `back-gate-sweep-check` (RPL_10/241207 cell 39). Resets the Station's internal state without rebuilding it.
- **No `time.sleep(...)` settle after a gate ramp at the start of the sequence.** Cell 122 jumps straight from `s.reset()` into the multisweep. This works because the prior cell already had the gates near the start of `vtg_new_vec[0]`.
