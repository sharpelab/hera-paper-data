# `hera.analysis` API Reference

Analysis primitives for `sweep` runs: open + summarize a run, resolve lock-in
channels and gains, re-form 2D fans into grids, compute gain-applied
resistances, and the Shubnikov–de Haas / gate-calibration math.

Source: `src/hera/analysis.py`. Depends only on `numpy` + `scipy`.

A *run* is a directory written by `sweep`: `data.tsv(.gz)` (headerless, one row
per setpoint) + `metadata.json` (column names, sweep config, comments).

---

## Loading runs

### `open_run(path)` → `Run`
Open a run directory (e.g. `<notebook>/data/119`). Loads `metadata.json` and
`data.tsv(.gz)` into an `(rows, ncols)` float array; raises if the directory,
`metadata.json`, the `columns` entry, or the TSV is missing, or if the column
count disagrees with `metadata['columns']`.

### `Run` (dataclass)
`Run(path, meta, cols, data)`.

| member | description |
|---|---|
| `col(name)` | column `name` as a 1-D array; raises `KeyError` if absent, `ValueError` if the name is duplicated (use `col_at`) |
| `col_at(idx)` | column by index |
| `col_indices(name)` | all indices with column name `name` |
| `metadata` | alias for `meta` (the parsed `metadata.json` dict) |
| `recipe` | first metadata comment (conventional recipe slug), or `None` |
| `tags` | comments after the first |
| `swept_axis` | `metadata['param']` (1D sweeps) |
| `setpoints` | `metadata['setpoints']` as a list, or `None` |
| `interrupted` | `metadata['interrupted']` |
| `kind` | `metadata['type']` (`'0D'`/`'1D'`/`'2D'`) |
| `rows` | row count |

Duplicate column names occur (planned setpoint + readback share a name; some
older data has two `T` columns). `col(name)` raises on duplicates — resolve
with `col_indices` + `col_at`.

### `summarize_run(run)` → `str`
Multi-line human summary: recipe, type, sweep range + monotonicity, row
completeness vs planned setpoints, and mean/range T if a `T` column is present.
Lines with no data are omitted.

---

## Lock-in channel / gain model

Shared with `hera.watch`. The physical value of a lock-in `*_X` column is
`X / gain`, with the gain read from `measurement_config` — never hardcode it.

### `resolve_channels(meta, include=None)` → `list[Channel]`
Resolve every `_X` (in-phase) column into a `Channel`. Gains and role labels
come from `meta['measurement_config']`, matched `srN_X` ↔ `srN_gain` by the
channel's trailing integer (so both `sr0_X`↔`sr0_gain` and `sr830_1_X`↔`sr1_gain`
resolve); missing/zero gain defaults to `1.0`. `include` restricts to given
channel ids or column names. A channel `is_current` (reported as amps, not
converted to resistance) when its gain is negative, `|gain| ≥ 1e4`, or its
label mentions "current".

### `Channel` (dataclass)
`col` (e.g. `'sr0_X'`), `idx` (column index), `cid` (id without `_X`), `n`
(trailing-integer index), `gain`, `label` (mc role string), `is_current`.

### `current_channel(channels)` → `Channel | None`
The single transimpedance current channel, or `None` if not exactly one. This
is the denominator of four-probe resistance R = V / I.

---

## Fan re-forming and resistances

### `fan_grids(run, columns=None)` → `FanGrids`
Re-form a 2D fan (a flat-row `megasweep`/`multimegasweep`) into per-column
grids, keeping only complete slow rows. `run` is a directory, path, or loaded
`Run`. `nfast` (points per slow row) comes from `metadata['fast_setpoints']`
— never hardcoded; trailing partial rows of an in-progress sweep are dropped
(`nrows = total // nfast`). `columns` restricts which columns are retained.

### `FanGrids` (dataclass)
`nrows`, `nfast`, `cols`, `data` (truncated to whole rows), `meta`,
`slow_param`.
- `grid(name)` → `(nrows, nfast)` array (duplicate names resolve to the first
  occurrence, i.e. the planned setpoint).
- `slow` → slow-axis value per row, `(nrows,)`.
- `metadata` → alias for `meta`.

### `resistance_grids(fan, channels=None)` → `ResistanceGrids`
Per-channel four-probe resistance grids `R = (V / gain_V) / I` from a
`FanGrids`, where `I` is the **measured** drain current
`I = X_cur / gain_cur` (a grid — it sags where the device is resistive), not a
nominal bias. Gains come from `measurement_config`. Raises if not exactly one
current channel is resolvable. `channels` restricts the voltage channels
returned. Returned R is **signed** (X/I): take `np.abs` for Rxx, keep the sign
for Rxy/Hall.

### `ResistanceGrids` (dataclass)
`current` (I grid, A), `current_channel` (cid), `R` (dict: voltage cid →
signed R grid, Ω).

---

## Shubnikov–de Haas

### `field_invB(B_start, B_end, N)` → `np.ndarray`
`N` field points from `B_start` to `B_end`, **uniform in 1/B** (SdH
oscillations are periodic in 1/B). Both endpoints must be `> 0`. Argument order
sets sweep direction. Sweeping these setpoints hands `sdh_fft` an already-even
1/B record (no resample needed).

### `sdh_fft(R_grid, B, *, b_range=None, nfft=512, bg_degree=5, window='hann', log=True, floor=1.0, uniform_rtol=0.1)` → `(freqs, spec)`
Per-column SdH FFT in 1/B.

- **Input `R_grid` is `(n_B, n_fast)`** — rows are field (the `FanGrids` row
  axis), columns are the fast axis. **2-D is required**; a single trace must be
  passed as `R[:, None]` (and the output column squeezed back). Raises if
  `R_grid.shape[0] != len(B)`.
- `B` is the per-row field `(n_B,)`, arbitrarily spaced.
- Per column: select `b_range`, optionally `log10(max(R, floor))`, subtract a
  degree-`bg_degree` polynomial background **in B-space** (`None` skips — the
  magnetoresistance background is smooth in B, not 1/B, so it is removed before
  the 1/B step), then FFT in 1/B. The 1/B resample is conditional: data already
  uniform in 1/B (decided from the spacing distribution within `uniform_rtol`)
  is FFT'd directly, zero-padded to `nfft`; uniform-in-B data is interpolated
  onto a regular `nfft`-point 1/B grid.
- **Returns `(freqs, spec)`**: `freqs` in Tesla `(n_freq,)`, `spec` the FFT
  magnitude **`(n_fast, n_freq)`** (note the transpose vs the input).

### `sdh_onset(R, B, *, b_hi=None, b_lo=0.3, r_full_scale=None, headroom=0.95, bg_degree=5, f_min=3.0, snr_threshold=5.0, n_periods=3.0, min_periods=2.0, step_frac=0.25, gap_widths=0.5, min_pts=8, max_tones=8, tone_floor_mult=4.0, marginal_mult=2.0)` → `SdhOnset`
Per-tone low-B onsets of the SdH oscillations in a single trace.
**`R` is a single 1-D longitudinal-resistance trace `(n_B,)`** (contrast
`sdh_fft`'s 2-D grid); `B` is the matching field `(n_B,)`. Removes a B-space
polynomial background, identifies every SdH tone via nested high-B FFT scans,
then walks each tone's Gaussian matched filter (FWHM = `n_periods` periods of
that tone) from high B down to where its amplitude sinks into the record's
white-noise floor — a statistical (≈`snr_threshold`·σ) onset, which can
legitimately sit below a by-eye read. `onset_b` is the minimum onset over
robust tones — the `landau-fan` step-1 `B_lo`, correct even when a light tone
outlives the dominant one. Pass `r_full_scale` (sensitivity / I_bias, Ω) to
enable soft-clip detection: samples ≥ `headroom`× full scale truncate the
analysis window (reported via `clip_high_b`) with a warning.
**Failure is never a nan** — raises `SdhOnsetError` (a `ValueError`: record
too short, no tones above the spectral floor, or no tone trackable) with
specifics; partial failures warn and land in `.untracked`.

### `SdhOnset` (dataclass)
`onset_b` (min onset over robust tones, Tesla — the record's low edge, flagged,
when the carrying tone is *censored*, i.e. still above threshold at the last
window), `onset_freq` (tone carrying it), `clip_high_b` / `b_lo_record` (the
analyzed window's edges), `noise_sigma`, `tones` (list of `SdhTone`, contrast
descending), `untracked` (`(freq, reason)` pairs). Convenience properties map
to the dominant tone: `consensus_freq`, `b_centers`, `snr` (the old
`peak_freq` field is gone). `summary()` renders the whole read — headline,
per-tone table with flags, untracked reasons — for a notebook cell.

### `SdhTone` (dataclass)
One tone's track: `freq`, `contrast`, `onset_b`, flags `censored` /
`revived` (above-threshold windows exist below the gap-walk stop) /
`marginal` (peak SNR < `marginal_mult`×threshold; excluded from the headline) /
`near_residual` (filter passband overlaps the detrend-residual band; excluded
from the headline unless a tracked harmonic corroborates it), `n_periods` /
`win_invB` (actual filter geometry), `harmonic_of` (freq of the stronger tone
this sits at ~k× of, else `None`), curves `b_centers` / `snr` / `amp`, and
`delta_f(b_max)` — the per-tone FFT resolution `1/(1/onset_b − 1/b_max)`.

---

## Gate calibration

> **Units — SI.** `GateCalibration` and `luttinger_frequency` work entirely in
> SI: density **n in m⁻²**, displacement field **D in V/m**, frequency in
> Tesla. (For the conventional ×10¹² cm⁻² display unit, scale n by `1e-16`.)
> The separate `sharpelab_nb.gates` conversion helpers (`calc_nD`,
> `calc_gate_voltages`, …) use **n in 10¹² cm⁻²** — do not feed an SI density
> from here into those, or vice versa.

### `GateCalibration` (frozen dataclass)
`GateCalibration(c_tg, c_bg, n_offset=0.0, D_offset=0.0)` — areal capacitances
(F/m²), `n_offset` (m⁻²), `D_offset` (V/m). Construct once per session, then:

```
n = (c_tg·V_tg + c_bg·V_bg) / e   + n_offset      [m⁻²]
D = (c_tg·V_tg − c_bg·V_bg) / (2·ε₀) + D_offset   [V/m]
```

- `density(V_tg, V_bg)` → n `(m⁻²)`.
- `displacement_field(V_tg, V_bg)` → D `(V/m)`.
- `n_D(V_tg, V_bg)` → `(n, D)`.
- `from_thicknesses(t_tg, t_bg, t_bgSiO2=0.0, *, n_offset=0.0, D_offset=0.0, kappa_hBN=3.0, kappa_SiO2=3.9)` — build from gate-stack geometry (metres) instead of areal capacitances; `t_bgSiO2=0` for a metal/graphite back gate.

All accept scalars or arrays. Physical constants come from `scipy.constants`.

### `luttinger_frequency(n)` → `np.ndarray`
Full-density Onsager (SdH) frequency `F = |n|·h / (4·e)`, in Tesla, for a
single Fermi surface carrying the full density. **`n` is in SI m⁻²** — feed
`GateCalibration.density` output directly. The 4 is the spin×valley Landau
degeneracy; returns the `|n|` form (positive for either carrier sign).
