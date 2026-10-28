# sdh-field-resolution

The answer is a Shubnikov–de Haas measurement: a magnetic-field sweep at one carrier density
(a spot check) or repeated over a series of densities (a fan, usually a `megasweep` with the
gates on the other axis). Extract the field axis and the density column(s), in cm⁻².

Spot check:

```json
{
  "status": "extracted",
  "B_min_T": 0.0,
  "B_max_T": 4.0,
  "n_points": 501,
  "spacing": "B",
  "n_cm2": -5.0e12,
  "flags": [],
  "notes": "cell 42: np.linspace(0.0, 4.0, 501); n_target = -5e12 stated in the cell (gates -2.278/-1.763 V from its gates_for())"
}
```

Fan:

```json
{
  "status": "extracted",
  "B_min_T": 0.6,
  "B_max_T": 8.0,
  "n_points": 300,
  "spacing": "invB",
  "n_min_cm2": -8.0e12,
  "n_max_cm2": 8.0e12,
  "n_columns": 41,
  "flags": [],
  "notes": "cell 48: field_invB(0.6, 8.0, 300) fast; gates per column from cal.gate_voltages over np.linspace(-8e12, 8e12, 41), D = 0 co-swept"
}
```

**Field axis**: `B_min_T`, `B_max_T`, `n_points` for the setpoint vector passed to the sweep, in
tesla; `spacing` is `"B"` for uniform in field (`np.linspace`) or `"invB"` for uniform in 1/B
(`field_invB`). If the vector is stitched or otherwise not uniform in either, give the whole
vector as `"B_values": [...]` instead and omit the three numbers and `spacing`.

**Density**, one of:

- `n_cm2`: one number for a spot check, or a short list when the sweep visits a few densities
  (a two-point gate bundle co-swept with the field, a handful of columns);
- `n_min_cm2`, `n_max_cm2`, `n_columns`: a fan whose columns are uniform in density.

When the cell states or computes the density, use that. When it only sets gate voltages,
convert them with the device card's (n, D) calibration: `hera.analysis.GateCalibration`
(constructed from the card's values) or `sharpelab_nb.gates.calc_nD`, run in a scratch
script, and say in `notes` which voltages and calibration you used. A fan whose columns are
set as gate pairs is converted the same way; if the converted columns are not uniform,
give them as the `n_cm2` list.

Which axis is slow and which is fast does not matter. Whether the second gate is co-swept
(the D = 0 line) or held fixed does: if fixed, say so in `notes` with its value.

If the cell issues more than one field sweep, report the one it presents as the measurement
and mention the others in `notes`.

Sign convention: hole doping is negative. A density stated in m⁻² must be converted
(1 m⁻² = 1e-4 cm⁻²).
