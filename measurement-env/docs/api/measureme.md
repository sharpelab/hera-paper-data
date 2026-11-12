# `sweep` (measureme) API Reference

The measurement layer: `lib/measureme`, imported as `import sweep`. A
`Station` collects QCoDeS parameters to follow, runs 0D–2D sweeps, and writes
each run to a directory (`data.tsv.gz` + `metadata.json`) via a `Writer`.

Source: `sweep/sweep.py`, `sweep/db.py`. `import sweep` re-exports the
`sweep.sweep` surface (`from .sweep import *`); `sweep.db`, `sweep.raster`,
`sweep.sweep_load` are submodules.

---

## Station

### `Station(measurement_config=None, basedir=None, verbose=True)`
A collection of followed parameters with sweep methods. `measurement_config`
is an arbitrary dict stamped into every run's `metadata.json` (channel→contact,
gains, bias, …). `basedir` is the run-directory root; falls back to the module
`BASEDIR` (see `set_basedir`) then `os.getcwd()`. The station writes `log.log`
into `basedir`, so the directory must exist before construction.

### `AsyncStation(measurement_config=None, basedir=None, verbose=True)`
Subclass of `Station`, same constructor and identical I/O / data layout. Reads
are parallelized per-instrument (one thread per distinct instrument, one
executor reused across a sweep), and same-instrument parameters are
batch-read when supported — SR830 `snap` (`SnapReadable`, ≤6 params) or
SR86x `get_values` (`BatchReadable`, ≤3 params), else sequential. Use this by
default; it produces byte-identical output to `Station`.

### `follow_param(param, gain=1.0)` → `Station` · alias **`fp`**
Append a QCoDeS parameter to the followed list. The stored column value is
**`param() / gain`** (gain division happens at read time). Returns the station,
so calls chain: `s.fp(sr0.X, gain).fp(sr0.P)`. For a true-current channel
follow it with `gain=1`. Column name is `param.full_name`.

### `add_comment(comment)`
Append a comment to `metadata['comments']`. **Comments are station-lifetime**:
every comment added since construction lands in every subsequent run's
metadata — rebuild (or otherwise reset) the station between runs of different
intent. `metadata['comments'][0]` is conventionally the recipe slug.

### `ramp(param, setpoint)`
Logged direct set — calls `param(setpoint)`. It does **not** sub-step; smooth
ramping is the driver's own `step`/`inter_delay` (or a driver `ramp_*` method).

### `register_run_before(fn, args)` / `register_run_after(fn, args)`
Register a hook called at each measured point. `args` must be a tuple. The hook
is called `fn(*args, **context)` where **context is injected by parameter
name** (via `inspect.signature` — the hook receives only the context keys it
declares):

| context key | available in | value |
|---|---|---|
| `station` | before & after | the `Station` |
| `writer` | before & after | the active `sweep.db.Writer` |
| `data` | after only | the most recent data row (list) |

A hook whose parameter is named `station` gets it from context — passing it in
`args` too double-binds (`TypeError: multiple values for 'station'`). Order any
`args`-supplied params before the context ones. Keyword-only hook params can't
be set positionally via `args`; bind them with `functools.partial` (signature
is seen through the partial, so injection still works).

### Other methods
- `measure()` → `SweepResult` — single 0D point.
- `watch(delay=0.0, max_duration=None)` → `SweepResult` — repeat-measure over
  time until `max_duration` (or interrupt).
- `read(param, gain=1.0)` / `read_all()` — log a one-off read, no run written.
- `plot(x, y, z=None)` / `reset_plots()` — live monitor only, not the data.
- `reset()` — clear the interrupted flag so the station can sweep again.

---

## Sweeps

Each sweep method returns a `SweepResult` and writes one run directory. The
**data-row column layout** is fixed per method (and matches `metadata['columns']`).
`*followed` is the followed-parameter values in `fp` order, each already
gain-divided.

| method | signature | row layout |
|---|---|---|
| `measure` | `()` | `[time, *followed]` |
| `watch` | `(delay=0.0, max_duration=None)` | `[time, *followed]` |
| `sweep` | `(param, setpoints, delay=0.0)` | `[time, setpoint, *followed]` |
| `multisweep` | `(params, setpointslist, delay=0.0)` | `[time, *setpoints, *followed]` |
| `megasweep` | `(slow_param, slow_v, fast_param, fast_v, slow_delay=0.0, fast_delay=0.0, init_delay=True)` | `[time, slow, fast, *followed]` |
| `multimegasweep` | `(slow_params, slow_v_list, fast_params, fast_v_list, slow_delay=0.0, fast_delay=0.0, init_delay=True)` | `[time, *slow, *fast, *followed]` |

- **`sweep`** — 1D. Sets `param` to each setpoint, waits `delay`, measures.
- **`multisweep`** — 1D, several parameters **co-swept**. `params` and
  `setpointslist` are parallel lists; `setpointslist[i]` is the vector for
  `params[i]`, and **all vectors must be equal length** (raises otherwise). At
  point j every `params[i]` is set to `setpointslist[i][j]` — one path through
  N-space, not a grid (e.g. a fixed-D (Vtg, Vbg) line).
- **`megasweep`** — 2D grid: outer `slow_param` over `slow_v`, inner
  `fast_param` over `fast_v`. `slow_delay` waits once per slow row (at the first
  fast point), `fast_delay` waits at every point.
- **`multimegasweep`** — 2D grid where each axis is a **co-swept bundle**.
  `slow_params`/`slow_v_list` and `fast_params`/`fast_v_list` are parallel
  lists; per-axis all vectors must be equal length. The grid is
  `len(slow_v) × len(fast_v)`; at each grid point every slow param and every
  fast param is set together. Example — field-slow, (Vtg, Vbg)-line-fast:
  `s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=0.9)`.
- **`init_delay`** (2D only) — `True` applies `slow_delay` before the very
  first point; `False` skips it (the axis is already parked there).

All sweeps are SIGINT-interruptible: an interrupt finishes the current point,
sets `metadata['interrupted'] = True`, and marks the station interrupted (call
`reset()` or rebuild before the next sweep).

### `SweepResult` (dataclass)
`SweepResult(basedir, id, metadata, datapath)` — the run root, the integer run
id, the final `metadata` dict, and the on-disk `data.tsv.gz` path.

---

## Module-level helpers (`sweep.*`)

- `set_basedir(path)` — set the global `BASEDIR` used when a `Station` is built
  without an explicit `basedir`.
- `list_measurements(basedir=None)` — render a markdown table of runs in a
  basedir.
- `measurement_info(i, basedir=None)` — print one run's metadata.
- `set_shutdown_handler(fn)` / `request_shutdown()` — register a
  ramp-to-safe callback and trigger graceful shutdown (thread-safe; if a sweep
  is active it stops after the current point, then calls `fn`). Used by the UPS
  monitor.

---

## Data on disk (`sweep.db`)

Each run is a directory `<basedir>/<id>/` with `data.tsv(.gz)` (headerless TSV,
one row per point), `metadata.json`, and optional blobs (e.g. `plot.png`).

### `Writer(basedir, max_id=1_000_000, fsync_every=10)`
Creates the run directory at the lowest free integer id under `basedir`
(`.id`, `.dir`). `add_point(point)` / `add_points(points)` append rows
(fsynced every `fsync_every` points); `add_blob(name, bytes)` writes a sidecar
file (name may not be `data.tsv`/`data.tsv.gz`/`metadata.json`). `.metadata` is
a free dict saved to `metadata.json` on `close()`; on close the uncompressed
`data.tsv` is gzipped to `data.tsv.gz` (verified, then the plaintext removed).
Use as a context manager.

### `Reader(basedir, id)`
Reads a run back. `.metadata` (migrated to the current schema via
`migrate_metadata`), iteration yields rows of **strings** (no type conversion),
`all_data()` returns all rows, `blob(name)` reads a sidecar. `.datapath` is the
`data.tsv.gz` path. Use as a context manager. For numeric loads,
`np.loadtxt(reader.datapath, …)` or `hera.analysis.open_run`.

### Metadata keys written per sweep type
Common to all: `version`, `type` (`0D`/`1D`/`2D`), `function`, `columns`,
`comments`, `measurement_config`, `instruments`, `interrupted`, `start_time`,
`end_time`.

| function | additional keys |
|---|---|
| `sweep` | `param`, `setpoints`, `delay` |
| `multisweep` | `params`, `setpoints` (list of per-param vectors), `delay` |
| `megasweep` | `slow_param`, `fast_param`, `slow_setpoints`, `fast_setpoints`, `slow_delay`, `fast_delay` |
| `multimegasweep` | `slow_params`, `fast_params`, `slow_setpoints`, `fast_setpoints`, `slow_delay`, `fast_delay` |
| `watch` | `delay`, `max_duration` |

Two schemas coexist in older data — singular (`param`, `slow_param`) vs current
plural (`params`, `slow_params`). Read through `sweep.sweep_load` or
`hera.analysis.open_run`; don't hand-roll key access.

---

## Polygon rasters (`sweep.raster`)

Helpers for sweeping/plotting an arbitrary polygon region of a 2-D plane (e.g. a
bounded (Vtg, Vbg) window). A `multimegasweep` runs the rasterized point order;
these turn polygon vertices into that point list and back into a plot mesh.

### `rasterize(vertices, nx, ny, fast_axis, rev_x=False, rev_y=False)` → `(xs, ys)`
The x/y coordinates of the grid points **inside** the polygon. `vertices` is
`(N, 2)`; `nx`/`ny` are grid points per axis over the bounding box; `fast_axis`
is 0 if x is the inner (fast) axis, 1 if y; `rev_x`/`rev_y` reverse a sweep
direction. Returns two 1-D arrays in raster order — feed them as the co-swept
fast/slow vectors of a `multimegasweep`.

### `pcolorize_data(zs, vertices, nx, ny, fast_axis, rev_x=False, rev_y=False)` → `(xs_mat, ys_mat, zs_mat)`
Bin measured values `zs` (in rasterized point order) back onto the regular
bounding mesh for `plt.pcolormesh(xs_mat, ys_mat, zs_mat)`. Cells outside the
polygon are `NaN`. The `nx`/`ny`/`fast_axis`/`rev_*` arguments must match the
`rasterize` call that produced the sweep.

### `random_ngon_vertices(n)` → `(n, 2)` vertices
A random simple-ish n-gon, for tests/demos.
