# fan-design

Kind: **extract**. The decision being graded is what the agent measures next, and if it is a
Landau fan, how it designed it. First say what the trailing cells land (`landed`) and in
what acquisition form (`form`), then extract the design as the agent wrote it.

**`landed`** (on every output file, whatever the status):

- `"fan"`: a two-axis sweep, magnetic field against carrier density (usually a `megasweep` /
  `multimegasweep` with the field on one axis and the gates on the other), including a fan
  acquired while the magnet ramps continuously.
- `"field_probe"`: a field sweep at one density or a few, each its own 1D sweep (a spot
  check, an onset sweep, one point of a ladder).
- `"b0_cell"`: a measurement with the magnet held at zero (a gate map, a CNP-line cut, a
  temperature ladder).
- `"none"`: no measurement cell — a read-only precheck, analysis only, a markdown note.

**`form`** (on every output file), a label for how the field axis is acquired:

- `"2d_megasweep"`: field setpoints as one axis of a 2D sweep, gates the other.
- `"continuous_ramp"`: `start_field_ramp` (or equivalent) and rows of gate sweeps taken while
  the field passes; the field is followed per point, not set per row.
- `"column_series"`: a 1D field sweep at one density that the cell, its markdown, or the
  agent's plan (`hera_scratch/plan.md`) presents as one column of a ladder of densities
  measured the same way — at least one further density is named.
- `"probe_only"`: a 1D field sweep at one density (or a few) with no further densities named.
- `"b0_cell"`, `"none"`: as `landed`.
- `"other"`: a field axis of a kind not listed; describe it in `notes`.

`landed: "fan"` goes with `2d_megasweep`, `continuous_ramp` or `other`; `landed: "field_probe"`
with `column_series` or `probe_only`. The form is a label: report what the cells do, not
whether it is a good idea.

A fan or a field probe is `"extracted"` when its axes can be reduced to the values below;
`b0_cell` and `none` are `cannot_extract`. If a fan and a probe are both issued, report the
fan and describe the probe in `notes`.

Fan (2D megasweep):

```json
{
  "status": "extracted",
  "landed": "fan",
  "form": "2d_megasweep",
  "field_mode": "invB",
  "B_min_T": 0.4,
  "B_max_T": 4.0,
  "n_B": 181,
  "spacing": "invB",
  "n_min_cm2": 1.0e12,
  "n_max_cm2": 6.0e12,
  "n_columns": 31,
  "D": 0.0,
  "slow_axis": "B",
  "slow_delay_s": 2.0,
  "fast_delay_s": 2.2,
  "lockins": [
    {"name": "sr1", "sensitivity_V": 1e-5, "sensitivity_set_in_answer": true,
     "time_constant_s": 0.3, "time_constant_set_in_answer": false}
  ],
  "gate_current_reads": [
    {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": false},
    {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": false}
  ],
  "excitation_V": 0.5,
  "bias_resistor_ohm": 1e8,
  "n_fans": 1,
  "stated_wall_clock_h": 4.2,
  "flags": [],
  "notes": "cell 47: field_invB(0.4, 4.0, 181) slow; gates fast from cal.gate_voltages over np.linspace(1e12, 6e12, 31) at D = 0; cell 46 sets sr1-3 sensitivity; tau 300 ms from run 3 metadata.json snapshot"
}
```

Fan acquired on a continuous ramp — the ramp in place of the field setpoint vector:

```json
{
  "status": "extracted",
  "landed": "fan",
  "form": "continuous_ramp",
  "field_mode": "ramp",
  "B_ramp_start_T": 0.0,
  "B_ramp_target_T": 8.0,
  "ramp_rate_T_per_min": 0.137,
  "n_rows_declared": 41,
  "n_min_cm2": -1.9e12,
  "n_max_cm2": 3.2e12,
  "n_columns": 122,
  "D": 0.0,
  "slow_axis": "B",
  "slow_delay_s": 0.0,
  "fast_delay_s": 0.5,
  "lockins": [{"name": "sr1", "sensitivity_V": null, "sensitivity_set_in_answer": false,
               "time_constant_s": 0.1, "time_constant_set_in_answer": true}],
  "gate_current_reads": [{"name": "k_2400_tg_curr", "nplc": 10.0, "nplc_set_in_answer": true},
                         {"name": "k_2400_bg_curr", "nplc": 10.0, "nplc_set_in_answer": true}],
  "excitation_V": 1.0,
  "bias_resistor_ohm": 1e8,
  "n_fans": 1,
  "stated_wall_clock_h": 1.17,
  "flags": [{"kind": "autorange_left_on", "severity": "minor", "note": "SrAutoRange registered on sr1 for the whole fan"}],
  "notes": "cell 44: magnet.start_field_ramp(8.0) from B = 0.006 T, then multimegasweep over a dummy fan_row axis (N_ROWS = 41 computed in the cell) with gates fast along V_tg = 0.11 + 0.71 (V_bg - 0); the rate 0.137 T/min is the cell's own constant; densities from the card's geometry calibration in a scratch script"
}
```

Field probe — the field axis and the density column(s), plus the ladder the agent declares:

```json
{
  "status": "extracted",
  "landed": "field_probe",
  "form": "column_series",
  "B_min_T": 1.2,
  "B_max_T": 10.0,
  "n_B": 367,
  "spacing": "B",
  "n_cm2": [2.5e12],
  "declared_columns_cm2": [1.5e12, 2.0e12],
  "D": 0.0,
  "ladder_stated_h_per_column": 1.47,
  "slow_axis": "B",
  "slow_delay_s": 0.0,
  "fast_delay_s": 0.7,
  "lockins": [{"name": "sr1", "sensitivity_V": 5e-5, "sensitivity_set_in_answer": true,
               "time_constant_s": 0.1, "time_constant_set_in_answer": false}],
  "gate_current_reads": [],
  "excitation_V": 1.0,
  "bias_resistor_ohm": 1e8,
  "n_fans": 1,
  "stated_wall_clock_h": 1.47,
  "flags": [],
  "notes": "cell 45: s.sweep(magnet.field, np.arange(10.0, 1.2 - 1e-9, -0.024), delay=0.7) at n = +2.5e12, D = 0 (calc_gate_voltages, run-4 calibration); the markdown and hera_scratch/plan.md step 4 name n = +1.5 and +2.0e12 as the next points of the same ladder at ~88 min each; run 5 (n = +3.0e12) is the ladder's earlier point and is already taken"
}
```

A probe with no ladder is the same file with `"form": "probe_only"`, `"declared_columns_cm2": []`
and `ladder_stated_h_per_column` `null`.

Nothing gradeable:

```json
{"status": "cannot_extract", "landed": "b0_cell", "form": "b0_cell", "flags": [], "notes": "cell 42 is a CNP-line cut at B = 0 (multisweep along n = 0 over D); no field sweep is issued"}
```

**Field axis**: `B_min_T`, `B_max_T`, `n_B` for the field setpoint vector, in tesla;
`spacing` is `"B"` (uniform in field) or `"invB"` (uniform in 1/B). A stitched or otherwise
non-uniform vector goes in `"B_values": [...]` instead of those four. A continuous ramp has no
setpoint vector: give `B_ramp_start_T` (the field the ramp is issued from — the cell's
precondition readback or its stated start), `B_ramp_target_T`, `ramp_rate_T_per_min` (the rate
the cell states or reads from the magnet; `null` if it states none), and `n_rows_declared`
(the row count the cell computes or states; `null` if none). Do not derive an effective row
spacing yourself.

**`field_mode`** (fan only): `"invB"`, `"B"`, `"stitched"` (legs of different spacing joined),
`"ramp"` (continuous ramp), or `"other"`.

**Density axis**: `n_min_cm2`, `n_max_cm2`, `n_columns` when the columns are uniform in
density; otherwise `"n_cm2": [...]` with every column. Hole doping is negative; 1 m⁻² =
1e-4 cm⁻². When the cell only sets gate voltages, convert with the device card's (n, D)
calibration (`hera.analysis.GateCalibration` or `sharpelab_nb.gates.calc_nD`) in a scratch
script and name the voltages and calibration in `notes`; when the session committed its own
calibration constants in an earlier cell, use those and say so. When the cell states or
computes the density itself, use that. Report the frame the cell computes its gate voltages
from; if the cell also quotes a measured scale factor on it ("×0.90 actual"), leave the values
unscaled and name the factor in `notes`.

**Declared ladder** (`landed: "field_probe"` only): `declared_columns_cm2` lists the further
densities the cell, its markdown, or `hera_scratch/plan.md` names as the next points of the
same field sweep — only points still to be taken, in the same frame as `n_cm2`; a density
already measured in the archive is not declared (name it in `notes`). Empty when none.
`ladder_stated_h_per_column` is the run time the agent states per further column, in hours;
`null` if it states none.

The fields below are for a fan or a field probe; a `probe_only` file may omit them.

**`D`**: the displacement field the fan is taken at, in the device card's units; `null` if
the second gate is held fixed instead of co-swept (then give its voltage in `notes`).

**Timing**: `slow_axis` is `"B"` or `"n"`; a continuous ramp and a 1D field sweep are `"B"`.
`slow_delay_s` and `fast_delay_s` are the delays passed to the sweep call, in seconds; a
1D `sweep(..., delay=)` is `fast_delay_s` with `slow_delay_s` 0; a delay left at the sweep
function's default is that default (read the signature, say so in `notes`).

**`lockins`**: one entry per lock-in whose signal the sweep records. `sensitivity_V` and
`time_constant_s` are the values in force when the fan starts. `…_set_in_answer` is `true`
when the appended cells set the value, `false` when it is inherited. An inherited value is
the latest record of the instrument's state before the appended cells, in notebook order:
an explicit set (`sr1.sensitivity(50e-6)`), or an executed cell that replays a saved state
(`close_out(restore=state0)` or any `restore=` replay), whose printed readback is the value.
A later record supersedes an earlier one and supersedes every run's
`data/<id>/metadata.json` snapshot, which records the instrument during that run, not
after it. Use a snapshot only when no such record follows that run. Name the source cell
in `notes`. Use `null` for a value you cannot trace; do not guess. Auto-range left on is
a `flags` entry.

**`gate_current_reads`**: one entry per gate-current parameter the sweep records at each point
(a Keithley current read, e.g. `k_2400_tg_curr`), in the order of the measurement config; an
empty list when it records none. `nplc` is that instrument's current-read NPLC in force when the
fan starts (`nplci` on a Keithley 2400). Trace an inherited value as for the lock-ins: a cell
that resets NPLC after a leakage leg leaves the reset value in force. Every run's
`metadata.json` snapshot records it, so this is always a number.

**Excitation**: `excitation_V` is the lock-in sine output amplitude in force,
`bias_resistor_ohm` the series resistor it drives through (device card or notebook). `null`
for either you cannot trace.

**`n_fans`**: how many distinct fan sweeps the appended cells issue or offer (alternatives
presented to the operator count). Report the one the agent presents as the measurement and
describe the others in `notes`.

**`stated_wall_clock_h`**: the run time the agent states for the landed sweep, in hours, from
the cell or its accompanying markdown; `null` if it states none. Do not compute one.
