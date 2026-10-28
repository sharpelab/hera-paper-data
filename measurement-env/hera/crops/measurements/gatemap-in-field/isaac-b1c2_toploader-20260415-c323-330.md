> From `isaac/b1c2_toploader/20260415_measure.ipynb` cells 323–330.

# nD map at B = 1T

```python
meas_config = {
    "sr1" : "28 - 4",
    "sr1_gain" : -1e6,
    "sr2" : "28 - 4",
    "sr2_gain" : 1e2,
    "sr3" : "5 - 30",
    "sr3_gain" : 1e2,
    "sr4" : "30 - 31",
    "sr4_gain" : 1e2,
    "bias_resistor" : 1e8,
    "bias_voltage_1" : sr830_1.amplitude(),
    "lockin_freq_1" : sr830_1.frequency(),
    "comment" : "bottom device",
}
```

```python
s = sweep.AsyncStation(meas_config)

s.fp(sr830_1.X).fp(sr830_1.P)
s.fp(sr830_2.X).fp(sr830_2.P)
s.fp(sr830_3.X).fp(sr830_3.P)
s.fp(sr830_4.X).fp(sr830_4.P)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(k_tg.volt).fp(k_tg.curr)

xp = k_bg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_1.X)
s.plot(xp, sr830_2.X)
s.plot(xp, sr830_3.X)
s.plot(xp, sr830_4.X)
```

```python
t_bg = 20e-9
t_tg = 1.18*t_bg
t_bgSiO2 = 0
c_tg = calc_ctg(t_tg)
c_bg = calc_cbg(t_bg, t_bgSiO2)
tg_lims = [-7, 6]
bg_lims = [-4, 4.4]

vertices = np.array([[-0.6e16, -0.7e9],
                    [-0.6e16, -0.45e9],
                    [0, -0.45e9],
                    [0, -0.7e9],
                    ])
xs, ys = raster.rasterize(vertices, 201, 201, 0, rev_x=False, rev_y=False)
vtg_vec, vbg_vec = calc_tb(xs, ys, c_tg, c_bg, n_offset = 0, D_offset=0)
vtg_new_vec, vbg_new_vec = sanitize_tg_bg(vtg_vec, vbg_vec, tg_lims, bg_lims)
print("Total number of points", len(vtg_vec))
print("Total number of points (sanitized)", len(vtg_new_vec))
```

```python
k_bg.volt.vals = validators.Numbers(-4,4.4)
k_tg.volt.vals = validators.Numbers(-7,6)
```

(Cell 328: `n_vec = 0e16; D = -0.45e9; vtg_vec, vbg_vec = calc_tb(n_vec, D, c_tg, c_bg, n_offset=0, D_offset=0)` — single-point gate-coordinate computation for the start of the polygon. Print-only.)

```python
s.ramp(k_tg.volt, vtg_vec)
s.ramp(k_bg.volt, vbg_vec)
```

```python
s.multisweep([k_tg.volt, k_bg.volt], [vtg_new_vec, vbg_new_vec], delay=1.2)
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
```

This section is structurally identical to Isaac's zero-field nD map (cells 113–122) except:
- The polygon is much smaller — a 600×250 µm rectangle in (n, D) at D ∈ [−0.7, −0.45] V/nm, n ∈ [−0.6e16, 0] cm⁻². Targeted at a feature visible in the zero-field map.
- **There is no `s.ramp(mag.field, 1.0)` call in this section.** The magnet was ramped to 1 T in the prior section ("B vs n", cells 300–313) and held there. The only signal that this is a finite-field map is the markdown header `# nD map at B = 1T` at cell 323.
- `t_tg = 1.18 * t_bg` here — different ratio than the 1.22594 used in cell 117 of the zero-field nD map. The dielectric ratio has been refit between the two sections (cf. ana-side capacitance refits across the device's lifetime).

This is exactly the pattern that makes finite-field maps fragile to interrupt-and-resume: the field setpoint is implicit in the kernel state, not in the cell. A recipe that asks for an explicit `s.ramp(mag.field, B)` plus a settle inside the gatemap-in-field cell — even when the field is "already" at the target — is more robust against crashes and post-hoc reproducibility.

No `add_comment` calls; the `comment` field of `meas_config` carries `"bottom device"` only — does not encode the field. Recipe asks for `add_comment(f'gatemap-in-field, B = {B}T')` going forward; Isaac's existing notebooks should be left frozen.
