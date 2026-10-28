"""Live run-dir digest engine for HERA.

Watches an in-progress (or completed) ``sweep`` run directory and emits a
compact one-line-per-landed-row digest to stdout — gain division applied,
progress/ETA included — so an agent can attach a background monitor instead
of hand-rolling watcher loops over the raw TSV.

A 'run' is a directory written by ``sweep`` containing:
    data.tsv(.gz)   headerless TSV, one row per setpoint
    metadata.json   column names, sweep config, recipe comments, gains

The mandatory transform is **gain division**: raw lock-in ``srN_X`` columns
are misleading on their own; the physical value is ``X / srN_gain`` with the
gain read from ``measurement_config``. Voltage channels are further turned
into resistance ``R = (X/gain) / I_bias`` (``I_bias = drive amplitude /
bias_resistor``, the drive amplitude read live from the ``bias_channel``
lock-in's station snapshot); the transimpedance current channel is reported
as current.

Two guards ride on top of the digest so an in-flight sweep can be
checkpointed for the failures a bare stats line hides:

* **Full-scale (soft-clip) headroom.** Each lock-in row carries
  ``fs <frac>`` = ``max|X| / sensitivity`` (raw volts, so gain-independent),
  and a row where any channel reaches ``fs_warn`` (default 0.90) gets a loud
  ``⚠ FS-HIGH``/``FS-CLIP`` suffix — ``CLIP`` reserved for the nominal rail
  (frac ≥ 1.0; SR830s soft-clip ~1.09× over). Sensitivity comes from the
  instrument snapshot; when it's absent the header says so and the check is
  skipped, never faked.
* **Gate leakage.** Non-lock-in ``_curr`` columns (Keithley gate currents)
  are surfaced as ``I`` stats per row, with a ``⚠ LEAK`` suffix when a
  channel's *excess over its own baseline* — ``max|I − I0|`` over the row
  slice — reaches ``leak_excess_warn`` (default 100 pA) on **two or more
  consecutive points**. The baseline ``I0`` is the median current over the
  least-biased rows (smallest ``|swept-param|``), so a clean leg parked on a
  Keithley offset floor (e.g. −100 pA) reads ~0 excess while a genuine
  super-linear onset shows through. This is a deliberately generous magnitude
  backstop for runaway leakage — not the pattern-based (dI/dV) onset detector
  the in-cell ``k2400_leakage_guard`` runs; the sustained requirement rejects
  isolated single-point Keithley spikes.
"""

from __future__ import annotations

import gzip
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from hera.analysis import Channel, resolve_channels


@dataclass
class RunModel:
    """Sweep geometry + channel/gain model parsed from metadata.json."""

    path: Path
    meta: dict[str, Any]
    cols: list[str]
    kind: str | None
    channels: list[Channel]
    i_bias: float | None
    # Geometry. For 2D: n_fast = points per slow row, n_slow = slow rows.
    # For 1D: n_fast = total expected points, n_slow = 1.
    n_fast: int
    n_slow: int
    slow_param: str | None
    fast_params: list[str]
    slow_setpoints: list[float] | None
    start_time: float | None = None
    # cid -> lock-in sensitivity (V) when recoverable from the instrument
    # snapshot; absent when the snapshot carries no usable value (None/0).
    full_scale: dict[str, float] = field(default_factory=dict)
    # (col idx, col name) for each non-lock-in `_curr` column (gate currents).
    current_cols: list[tuple[int, str]] = field(default_factory=list)
    fs_warn: float = 0.90    # warn when max|X|/sensitivity reaches this fraction
    # warn when a gate current's max|I - I0| (excess over its baseline) reaches
    # this (A) on 2+ consecutive points. NOT absolute |I|: the baseline defeats
    # a Keithley offset floor, the sustained requirement defeats single spikes.
    leak_excess_warn: float = 100e-12

    @property
    def is_2d(self) -> bool:
        return self.kind == "2D" and self.n_slow > 1

    @property
    def expected_rows(self) -> int:
        return self.n_fast * self.n_slow


# --------------------------------------------------------------------------
# Metadata / model
# --------------------------------------------------------------------------


def _snapshot_value(meta: dict[str, Any], inst: str, param: str) -> float | None:
    """Live value of ``inst.param`` from the station's instrument snapshot."""
    snap = ((meta.get("instruments") or {}).get(inst) or {}).get("snapshot") or {}
    p = (snap.get("parameters") or {}).get(param) or {}
    return _as_float(p.get("value"))


def _drive_voltage(meta: dict[str, Any], mc: dict[str, Any]) -> float | None:
    """AC drive amplitude (V). Prefer the live station snapshot of the
    ``bias_channel`` lock-in (captured at sweep time, never stale); fall back
    to a legacy flat ``bias_voltage*`` key for runs predating bias_channel."""
    ch = mc.get("bias_channel")
    if ch:
        amp = _snapshot_value(meta, ch, "amplitude")
        if amp is not None:
            return amp
    if "bias_voltage" in mc:
        return _as_float(mc["bias_voltage"])
    for k, v in mc.items():
        if k.startswith("bias_voltage"):
            return _as_float(v)
    return None


def _as_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def build_model(
    path: str | Path,
    channels: list[str] | None = None,
    bias_current: float | None = None,
    fs_warn: float = 0.90,
    leak_excess_warn: float = 100e-12,
) -> RunModel:
    """Parse metadata.json into a RunModel (geometry + gain/channel map)."""
    path = Path(path).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"not a directory: {path}")
    meta_path = path / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"missing metadata.json in {path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    cols = list(meta.get("columns") or [])
    if not cols:
        raise ValueError(f"metadata.json has no 'columns' entry in {path}")

    mc = meta.get("measurement_config") or {}
    chans = resolve_channels(meta, include=channels)

    # Full-scale (soft-clip) monitoring: raw X-column full scale is the lock-in
    # sensitivity (V), read from the instrument snapshot. The fraction
    # max|X|/sensitivity is gain- and I_bias-independent. Absent when the
    # snapshot value is None/0 (some archives leave it unpopulated, like
    # time_constant/filter_slope) — then the check is skipped, not faked.
    full_scale: dict[str, float] = {}
    for ch in chans:
        sens = _snapshot_value(meta, ch.cid, "sensitivity")
        if sens is not None and sens > 0:
            full_scale[ch.cid] = sens

    # Non-lock-in current columns (Keithley gate leakage): every rig names them
    # with a `_curr` suffix. First occurrence of each unique name.
    current_cols: list[tuple[int, str]] = []
    seen_curr: set[str] = set()
    for idx, c in enumerate(cols):
        if c.endswith("_curr") and c not in seen_curr:
            seen_curr.add(c)
            current_cols.append((idx, c))

    i_bias = bias_current
    if i_bias is None:
        bv = _drive_voltage(meta, mc)
        br = _as_float(mc.get("bias_resistor"))
        if bv is not None and br:
            i_bias = bv / br

    kind = meta.get("type")
    # Geometry — handle all metadata schemas: singular param/setpoints on
    # older 1D runs, plural fast_/slow_ params on multimegasweep, singular
    # slow_/fast_param on megasweep.
    fast_params = _str_list(meta.get("fast_params") or meta.get("fast_param"))
    slow_params = _str_list(meta.get("slow_params") or meta.get("slow_param"))
    fast_sp = _first_setpoints(meta.get("fast_setpoints"))
    slow_sp = _first_setpoints(meta.get("slow_setpoints"))

    if kind == "2D" and slow_sp:
        n_fast = len(fast_sp) if fast_sp else 0
        n_slow = len(slow_sp)
        slow_param = slow_params[0] if slow_params else None
        slow_vals = list(slow_sp)
    else:
        # 1D (or degenerate). setpoints may be plural fast_setpoints or the
        # legacy singular 'setpoints'.
        sp = fast_sp
        if not sp:
            sp = _flat_setpoints(meta.get("setpoints"))
        n_fast = len(sp) if sp else 0
        n_slow = 1
        slow_param = None
        slow_vals = None
        if not fast_params:
            fp = meta.get("param")
            fast_params = [fp] if isinstance(fp, str) else []

    return RunModel(
        path=path, meta=meta, cols=cols, kind=kind, channels=chans,
        i_bias=i_bias, n_fast=n_fast, n_slow=n_slow, slow_param=slow_param,
        fast_params=fast_params, slow_setpoints=slow_vals,
        start_time=_as_float(meta.get("start_time")),
        full_scale=full_scale, current_cols=current_cols,
        fs_warn=fs_warn, leak_excess_warn=leak_excess_warn,
    )


def run_dir_ready(path: str | Path) -> bool:
    """True once ``path`` is a run dir sweep has populated enough to model:
    the directory exists and holds a ``metadata.json``. Sweep creates the
    dir (and opens ``data.tsv``) before writing metadata, so this is the
    earliest point ``build_model`` can succeed."""
    path = Path(path).expanduser()
    return path.is_dir() and (path / "metadata.json").exists()


def resolve_next_run(data_dir: str | Path) -> Path:
    """Predict the next integer file_id dir for a sweep under ``data_dir``.

    Returns ``max(existing integer dirs) + 1`` (or ``0`` if none). Sweep
    actually allocates the *lowest free* id, so this can differ from what
    sweep picks when there are gaps (a deleted run) — but it fails
    predictably (always the high end), which is what we want for an
    arm-before-run gate. Pair with ``wait_for_run`` to block on the dir."""
    data_dir = Path(data_dir).expanduser()
    highest = -1
    if data_dir.is_dir():
        for child in data_dir.iterdir():
            if child.is_dir() and child.name.isdigit():
                highest = max(highest, int(child.name))
    return data_dir / str(highest + 1)


def ready_run_ids(data_dir: str | Path) -> set[int]:
    """The set of integer file_ids under ``data_dir`` that are modellable now
    (their dir holds a ``metadata.json`` — see ``run_dir_ready``). Non-integer
    children and not-yet-populated dirs are ignored."""
    data_dir = Path(data_dir).expanduser()
    ids: set[int] = set()
    if data_dir.is_dir():
        for child in data_dir.iterdir():
            if child.is_dir() and child.name.isdigit() and run_dir_ready(child):
                ids.add(int(child.name))
    return ids


def run_dir_started(path: str | Path) -> bool:
    """Earliest filesystem evidence a sweep cell has begun: the run dir exists.
    Sweep ``mkdir``s it at ``Writer`` init — before ``metadata.json`` (written
    ~ms later in ``_init_metadata``) and before the first setpoint move. Latch a
    watch on this to attach the instant the run starts; pair with
    ``run_dir_ready`` (which also requires ``metadata.json``) for the moment
    ``build_model`` can parse it."""
    return Path(path).expanduser().is_dir()


def existing_run_ids(data_dir: str | Path) -> set[int]:
    """Integer file_ids whose dir EXISTS under ``data_dir`` — the dir-existence
    analogue of ``ready_run_ids`` (which additionally requires
    ``metadata.json``). ``--next`` latches on this so it catches a new run the
    instant its dir is created, not ~ms later when metadata lands."""
    data_dir = Path(data_dir).expanduser()
    ids: set[int] = set()
    if data_dir.is_dir():
        for child in data_dir.iterdir():
            if child.is_dir() and child.name.isdigit():
                ids.add(int(child.name))
    return ids


# A run dir appears (mkdir) a hair before its metadata.json is written. Once the
# dir is seen the human-wait is satisfied; this short settle only guards that
# race so build_model has metadata to parse. NOT the --wait-start budget.
_METADATA_SETTLE_S = 30.0


def wait_for_metadata(
    run_dir: str | Path,
    *,
    settle: float = _METADATA_SETTLE_S,
    poll: float = 5.0,
    now_fn=time.time,
    sleep_fn=time.sleep,
    emit=None,
) -> bool:
    """A run dir has appeared; block until its ``metadata.json`` lands so
    ``build_model`` can parse it. Sweep writes metadata within ~ms of creating
    the dir, so this only guards that race — it is a short settle, NOT the
    human-wait budget (``--wait-start``). Returns True once metadata is present,
    False if it hasn't appeared within ``settle`` seconds (``settle <= 0`` waits
    indefinitely)."""
    run_dir = Path(run_dir).expanduser()
    if run_dir_ready(run_dir):
        return True
    deadline = now_fn() + settle if settle > 0 else None
    while True:
        sleep_fn(poll)
        if run_dir_ready(run_dir):
            return True
        if deadline is not None and now_fn() >= deadline:
            if emit is not None:
                emit(f"# warning: run dir {run_dir.name} appeared but "
                     f"metadata.json did not within {settle:.0f}s")
            return False


def wait_for_next_run(
    data_dir: str | Path,
    *,
    baseline: set[int] | None = None,
    timeout: float = 1800.0,
    poll: float = 5.0,
    now_fn=time.time,
    sleep_fn=time.sleep,
    emit=None,
) -> Path | None:
    """Latch onto the *next* run dir to appear under ``data_dir``.

    This is the robust ``--next`` primitive: instead of predicting an exact
    file_id once (``resolve_next_run``) and then waiting for that specific
    path, it snapshots the set of already-present run ids and returns the
    lowest *new* dir to appear (then settles briefly for its metadata so
    ``build_model`` can parse it). That makes it correct in cases the
    predict-once form gets wrong:

    * **2nd+ run of a session** — a prior run dir already exists; we wait for
      the genuinely new one rather than a frozen ``max+1`` guess.
    * **lowest-free-id allocation / gaps** — sweep fills the lowest free id
      (``data/2`` when ``{0,1,3}`` exist), which ``max+1`` would miss.

    ``baseline`` defaults to the ids present at call time (the arm moment);
    pass it explicitly only to snapshot earlier. Returns the run-dir ``Path``,
    or ``None`` if ``timeout`` seconds elapse with no new run (``timeout <= 0``
    waits indefinitely). The one case it can't disambiguate: if the target
    run's dir *already* exists at the arm moment (the watch was armed after the
    cell started), it is in the baseline and the waiter latches the run *after*
    it — so arm before you trigger the cell.
    """
    data_dir = Path(data_dir).expanduser()
    if baseline is None:
        baseline = existing_run_ids(data_dir)
    if emit is not None:
        known = ", ".join(str(i) for i in sorted(baseline)) or "none"
        emit(f"# armed on {data_dir} — waiting for the next run to start "
             f"(known runs: {known}) …")
    deadline = now_fn() + timeout if timeout > 0 else None
    while True:
        new = sorted(i for i in existing_run_ids(data_dir) if i not in baseline)
        if new:
            run_dir = data_dir / str(new[0])
            wait_for_metadata(run_dir, poll=poll, now_fn=now_fn,
                              sleep_fn=sleep_fn, emit=emit)
            return run_dir
        if deadline is not None and now_fn() >= deadline:
            return None
        sleep_fn(poll)


def wait_for_run(
    path: str | Path,
    *,
    timeout: float = 1800.0,
    poll: float = 5.0,
    now_fn=time.time,
    sleep_fn=time.sleep,
    emit=None,
) -> bool:
    """Block until ``path`` becomes a modellable run dir, or ``timeout``
    seconds elapse. Returns True once the dir and its ``metadata.json`` are
    both present (so ``build_model`` will succeed), False on timeout.
    ``timeout <= 0`` waits indefinitely.

    This is the "arm before the operator starts the cell" gate: poll for the
    data dir to appear instead of requiring it to exist up front. It latches on
    the dir appearing (the earliest sweep-start signal — see
    ``run_dir_started``) and then settles for the metadata. Its ``timeout`` is
    the *human-patience* budget (how long to wait for the operator to run the
    cell) — independent of the measurement watch's own ``--timeout``."""
    path = Path(path).expanduser()
    if run_dir_ready(path):
        return True
    if emit is not None:
        emit(f"# waiting for run dir {path} to appear …")
    deadline = now_fn() + timeout if timeout > 0 else None
    while True:
        sleep_fn(poll)
        if run_dir_started(path):
            return wait_for_metadata(path, poll=poll, now_fn=now_fn,
                                     sleep_fn=sleep_fn, emit=emit)
        if deadline is not None and now_fn() >= deadline:
            return False


def _str_list(v: Any) -> list[str]:
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str)]
    if isinstance(v, str):
        return [v]
    return []


def _first_setpoints(v: Any) -> list[float] | None:
    """fast/slow_setpoints is a list-of-lists (one per co-swept param)."""
    if isinstance(v, list) and v and isinstance(v[0], list):
        return [float(x) for x in v[0]]
    if isinstance(v, list) and v and isinstance(v[0], (int, float)):
        return [float(x) for x in v]
    return None


def _flat_setpoints(v: Any) -> list[float] | None:
    if isinstance(v, list) and v and isinstance(v[0], (int, float)):
        return [float(x) for x in v]
    if isinstance(v, list) and v and isinstance(v[0], list):
        return [float(x) for x in v[0]]
    return None


# --------------------------------------------------------------------------
# Incremental TSV reading
# --------------------------------------------------------------------------


def read_rows(path: Path, ncols: int) -> np.ndarray:
    """Read all *complete* rows from a (possibly growing) run dir's TSV.

    Prefers the plain ``data.tsv`` (present while a sweep is live); falls
    back to ``data.tsv.gz`` (written on completion). A trailing partial line
    — the row sweep is mid-write — is dropped: only newline-terminated lines
    with exactly ``ncols`` fields are parsed.
    """
    plain = path / "data.tsv"
    gz = path / "data.tsv.gz"
    if plain.exists():
        raw = plain.read_bytes()
    elif gz.exists():
        with gzip.open(gz, "rb") as f:
            raw = f.read()
    else:
        return np.empty((0, ncols), dtype=float)

    text = raw.decode("utf-8", errors="replace")
    if not text:
        return np.empty((0, ncols), dtype=float)
    ended_clean = text.endswith("\n")
    lines = text.splitlines()
    if lines and not ended_clean:
        lines = lines[:-1]  # drop the row still being written

    out: list[list[float]] = []
    for ln in lines:
        if not ln:
            continue
        parts = ln.split("\t")
        if len(parts) != ncols:
            continue
        try:
            out.append([float(p) for p in parts])
        except ValueError:
            continue
    if not out:
        return np.empty((0, ncols), dtype=float)
    return np.array(out, dtype=float)


def run_complete(model: RunModel) -> bool:
    """Has the sweep finished? end_time / interrupt flag re-read from disk."""
    meta_path = model.path / "metadata.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = model.meta
    if meta.get("end_time") is not None:
        return True
    if meta.get("interrupted"):
        return True
    # The plain TSV is gzipped on completion; gz-only means done.
    if not (model.path / "data.tsv").exists() and (model.path / "data.tsv.gz").exists():
        return True
    return False


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------

_SI_PREFIXES = [
    (1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, ""),
    (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p"),
]


def fmt_eng(value: float, unit: str, sig: int = 3) -> str:
    """Engineering-notation format to `sig` significant figures.

    e.g. 1.6e-9,'A' -> '1.60nA'; 620.0,'Ω' -> '620Ω'; 95.37,'Ω' -> '95.4Ω'.
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "nan"
    if value == 0:
        return f"0{unit}"
    sign = "-" if value < 0 else ""
    a = abs(value)
    scale, pfx = _SI_PREFIXES[-1]
    for s, p in _SI_PREFIXES:
        if a >= s:
            scale, pfx = s, p
            break
    m = a / scale  # mantissa in [1, 1000)
    decimals = max(0, sig - 1 - int(math.floor(math.log10(m))))
    return f"{sign}{m:.{decimals}f}{pfx}{unit}"


def _physical(ch: Channel, x: np.ndarray, model: RunModel, raw: bool
              ) -> tuple[np.ndarray, str, str]:
    """Map a raw X-array to (values, kind_tag, base_unit) per conventions.

    kind_tag is one of 'raw' / 'I' / 'R' / 'V' — what the numbers mean.
    """
    if raw:
        return x, "X", "V"
    g = x / ch.gain
    if ch.is_current:
        return g, "I", "A"
    if model.i_bias:
        return g / model.i_bias, "R", "Ω"
    return g, "V", "V"


def _stats_token(ch: Channel, x: np.ndarray, model: RunModel, raw: bool) -> str:
    vals, tag, unit = _physical(ch, x, model, raw)
    finite = vals[np.isfinite(vals)]
    if finite.size == 0:
        return f"{ch.cid} {tag}[--]"
    med = float(np.median(finite))
    lo = float(np.min(finite))
    hi = float(np.max(finite))
    fs = ""
    frac = _fs_fraction(ch, x, model)
    if frac is not None:
        fs = f" fs {frac:.2f}"
    return (
        f"{ch.cid} {tag}[med {fmt_eng(med, unit)} "
        f"lo {fmt_eng(lo, unit)} hi {fmt_eng(hi, unit)}{fs}]"
    )


def _fs_fraction(ch: Channel, x: np.ndarray, model: RunModel) -> float | None:
    """max|X| over the raw slice, as a fraction of the channel's full-scale
    sensitivity. None when sensitivity isn't recoverable or the slice is empty.
    Computed on raw volts, so it's gain- and I_bias-independent."""
    sens = model.full_scale.get(ch.cid)
    if not sens:
        return None
    finite = x[np.isfinite(x)]
    if finite.size == 0:
        return None
    return float(np.max(np.abs(finite))) / sens


def _curr_name(col: str) -> str:
    """Display name for a `_curr` column: strip the suffix (k_2400_bg)."""
    return col[:-len("_curr")] if col.endswith("_curr") else col


def _current_token(col: str, x: np.ndarray) -> str:
    """Signed med/lo/hi of a non-lock-in current column (amps, no gain)."""
    finite = x[np.isfinite(x)]
    name = _curr_name(col)
    if finite.size == 0:
        return f"{name} I[--]"
    med = float(np.median(finite))
    lo = float(np.min(finite))
    hi = float(np.max(finite))
    return (
        f"{name} I[med {fmt_eng(med, 'A')} "
        f"lo {fmt_eng(lo, 'A')} hi {fmt_eng(hi, 'A')}]"
    )


_LEAK_BASELINE_ROWS = 15  # rows sampled for the per-channel baseline I0


def _leak_baselines(model: RunModel, data: np.ndarray) -> dict[int, float]:
    """Per-current-column baseline ``I0`` = median current over the
    least-biased rows: the ``_LEAK_BASELINE_ROWS`` rows with the smallest
    ``|swept-param|``. Anchoring to the least-biased region (rather than the
    first N rows) keeps the baseline clean for a leg that does *not* start
    parked — a bipolar or offset sweep anchors to its V≈0 region instead of a
    possibly-already-leaking start row. Falls back to the first N rows when the
    swept param isn't a readable column. Columns with no finite current in the
    sampled rows are omitted (their leak check is skipped, not faked)."""
    if data.shape[0] == 0:
        return {}
    swept = model.fast_params[0] if model.fast_params else None
    if swept and swept in model.cols:
        v = data[:, model.cols.index(swept)]
        order = np.argsort(np.abs(v), kind="stable")
        anchor = order[np.isfinite(v[order])][:_LEAK_BASELINE_ROWS]
    else:
        anchor = np.arange(min(_LEAK_BASELINE_ROWS, data.shape[0]))
    baselines: dict[int, float] = {}
    for idx, _col in model.current_cols:
        finite = data[anchor, idx][np.isfinite(data[anchor, idx])]
        if finite.size:
            baselines[idx] = float(np.median(finite))
    return baselines


def _row_warnings(model: RunModel, sl: np.ndarray,
                  baselines: dict[int, float]) -> str:
    """Loud, greppable warning suffix for a row slice — full-scale headroom
    (soft clip) and gate leakage — or '' when everything is nominal. 'CLIP'
    is reserved for the fixed nominal rail (fraction ≥ 1.0); 'HIGH' is the
    ``fs_warn`` headroom threshold below it.

    Gate leakage fires on *excess over baseline*: ``|I - I0|`` reaching
    ``leak_excess_warn`` on **two or more consecutive points** in the slice.
    The baseline defeats a Keithley offset floor; the sustained requirement
    defeats isolated single-point spikes. The reported value is the peak
    excess over the slice."""
    if sl.shape[0] == 0:
        return ""
    railed: list[str] = []
    high: list[str] = []
    for ch in model.channels:
        frac = _fs_fraction(ch, sl[:, ch.idx], model)
        if frac is None or frac < model.fs_warn:
            continue
        (railed if frac >= 1.0 else high).append(f"{ch.cid}={frac:.2f}")
    leaks: list[str] = []
    for idx, col in model.current_cols:
        i0 = baselines.get(idx)
        if i0 is None:
            continue
        exc = np.abs(sl[:, idx] - i0)
        over = np.isfinite(exc) & (exc >= model.leak_excess_warn)
        if not np.any(over[:-1] & over[1:]):
            continue
        peak = float(np.max(exc[np.isfinite(exc)]))
        leaks.append(f"{_curr_name(col)}=Δ{fmt_eng(peak, 'A')}")
    segs: list[str] = []
    if railed:
        segs.append("FS-CLIP " + " ".join(railed))
    if high:
        segs.append("FS-HIGH " + " ".join(high))
    if leaks:
        segs.append("LEAK " + " ".join(leaks))
    return "⚠ " + "  ".join(segs) if segs else ""


def _fmt_dt(seconds: float) -> str:
    seconds = max(0, int(seconds))
    if seconds < 90:
        return f"{seconds}s"
    m = seconds / 60
    if m < 90:
        return f"{m:.0f}m"
    return f"{m / 60:.1f}h"


def _clock(epoch: float) -> str:
    return time.strftime("%H:%M", time.localtime(epoch))


def fmt_sp(value: float) -> str:
    """Format a setpoint value, snapping float-noise near-zero to 0 (a
    descending field ramp ends at ~2e-14 T, not a meaningful number)."""
    if abs(value) < 1e-9:
        return "0"
    return f"{value:+.4g}"


# --------------------------------------------------------------------------
# Digest
# --------------------------------------------------------------------------


@dataclass
class _Progress:
    rows: int
    expected: int
    rate_per_min: float | None  # rows/min, None if unknown
    eta_epoch: float | None     # projected completion, None if unknown


def _progress(model: RunModel, rows: int, now: float) -> _Progress:
    exp = model.expected_rows
    rate = None
    eta = None
    if model.start_time and rows > 0:
        elapsed = now - model.start_time
        if elapsed > 0:
            rate = rows / (elapsed / 60.0)
            remaining = max(0, exp - rows)
            if rate > 0 and remaining > 0:
                eta = now + remaining / (rate / 60.0)
    return _Progress(rows=rows, expected=exp, rate_per_min=rate, eta_epoch=eta)


def _progress_token(p: _Progress, complete: bool) -> str:
    base = f"{p.rows}/{p.expected} rows"
    if p.rate_per_min is not None:
        base += f"  {p.rate_per_min:.1f} row/min"
    if complete:
        base += "  done"
    elif p.eta_epoch is not None:
        base += f"  ETA {_fmt_dt(p.eta_epoch - time.time())} (≈{_clock(p.eta_epoch)})"
    return base


def header_lines(model: RunModel, raw: bool = False) -> list[str]:
    """The header block printed once before per-row digests."""
    out: list[str] = []
    comments = model.meta.get("comments") or []
    recipe = comments[0] if comments else "?"
    geom = (f"{model.n_slow}×{model.n_fast}" if model.is_2d
            else f"{model.n_fast}")
    raw_tag = "  [RAW — no gain division]" if raw else ""
    out.append(f"# {model.path.name}  {model.kind or '?'}  {recipe}{raw_tag}")
    out.append(f"#   geometry: {geom}  ({model.expected_rows} rows expected)")
    if model.is_2d and model.slow_param:
        sp = model.slow_setpoints or []
        rng = f"{fmt_sp(sp[0])} → {fmt_sp(sp[-1])}" if sp else "?"
        out.append(f"#   slow:     {model.slow_param}  {rng}  ({model.n_slow} rows)")
    if model.fast_params:
        out.append(f"#   fast:     {', '.join(model.fast_params)}  ({model.n_fast} pts)")
    chan_descs = []
    for ch in model.channels:
        role = "I" if ch.is_current else ("R" if model.i_bias else "V")
        g = f"gain {fmt_eng(ch.gain, '')}" if ch.gain != 1.0 else "gain 1"
        lbl = f" {ch.label}" if ch.label else ""
        chan_descs.append(f"{ch.cid}[{role} {g}{lbl}]")
    if chan_descs:
        out.append(f"#   channels: {'  '.join(chan_descs)}")
    if model.channels:
        if model.full_scale:
            fs_descs = [
                f"{ch.cid} {fmt_eng(model.full_scale[ch.cid], 'V')}"
                if ch.cid in model.full_scale else f"{ch.cid} ?"
                for ch in model.channels
            ]
            out.append(
                f"#   full-scale: {'  '.join(fs_descs)}  "
                f"(warn ≥{model.fs_warn:.2f} of nominal; SR830 soft-clips ~1.09×)"
            )
        else:
            out.append("#   full-scale: unavailable (no sensitivity in "
                       "instrument snapshot) — soft-clip check off")
    if model.current_cols:
        names = " ".join(_curr_name(c) for _, c in model.current_cols)
        out.append(f"#   gate-current: {names}  "
                   f"(warn excess ≥{fmt_eng(model.leak_excess_warn, 'A')} "
                   f"over baseline, sustained ≥2 pts)")
    if model.i_bias:
        out.append(f"#   I_bias:   {fmt_eng(model.i_bias, 'A')} (R = V/I_bias)")
    if model.start_time:
        out.append(f"#   started:  {_clock(model.start_time)}")
    return out


def _slow_value(model: RunModel, data: np.ndarray, k: int) -> str:
    """Label for slow-row k: prefer the planned setpoint, else readback."""
    if model.slow_param is None:
        return ""
    if model.slow_setpoints and k < len(model.slow_setpoints):
        v = model.slow_setpoints[k]
    elif model.slow_param and model.slow_param in model.cols:
        col = model.cols.index(model.slow_param)
        start = k * model.n_fast
        v = float(data[start, col]) if start < data.shape[0] else float("nan")
    else:
        return ""
    return f"{model.slow_param}={fmt_sp(v)}"


def _fast_window(model: RunModel, sl: np.ndarray) -> str:
    """min->max of each fast (co-swept) param across the row slice. Truthful
    for partial rows — reflects only the points that actually landed."""
    if not model.fast_params or sl.shape[0] == 0:
        return ""
    toks = []
    for fp in model.fast_params:
        if fp not in model.cols:
            continue
        c = sl[:, model.cols.index(fp)]
        toks.append(f"{fp}[{c.min():+.3g}→{c.max():+.3g}]")
    return "  ".join(toks)


def _row_line(model: RunModel, data: np.ndarray, k: int, raw: bool,
              progress: _Progress, complete: bool, partial: bool) -> str:
    start = k * model.n_fast
    stop = min(start + model.n_fast, data.shape[0])
    sl = data[start:stop]
    n_in = sl.shape[0]
    tag = f"row {k:>3}/{model.n_slow}"
    if partial:
        tag += f" (partial {n_in}/{model.n_fast})"
    parts = [tag]
    sv = _slow_value(model, data, k)
    if sv:
        parts.append(sv)
    fw = _fast_window(model, sl)
    if fw:
        parts.append(fw)
    for ch in model.channels:
        parts.append(_stats_token(ch, sl[:, ch.idx], model, raw))
    for idx, col in model.current_cols:
        parts.append(_current_token(col, sl[:, idx]))
    warns = _row_warnings(model, sl, _leak_baselines(model, data))
    return _join_row(parts, progress, complete, warns)


def _chunk_line(model: RunModel, data: np.ndarray, lo: int, hi: int, raw: bool,
                progress: _Progress, complete: bool) -> str:
    """1D digest line covering rows [lo, hi)."""
    sl = data[lo:hi]
    parts = [f"rows {lo}–{hi - 1}"]
    fw = _fast_window(model, sl)
    if fw:
        parts.append(fw)
    for ch in model.channels:
        parts.append(_stats_token(ch, sl[:, ch.idx], model, raw))
    for idx, col in model.current_cols:
        parts.append(_current_token(col, sl[:, idx]))
    warns = _row_warnings(model, sl, _leak_baselines(model, data))
    return _join_row(parts, progress, complete, warns)


def _join_row(parts: list[str], progress: _Progress, complete: bool,
              warns: str) -> str:
    """Assemble a digest line: fields | progress, then any loud warning
    suffix last so it's the final thing an agent tailing the stream sees."""
    line = "  ".join(parts) + f"  | {_progress_token(progress, complete)}"
    if warns:
        line += f"  {warns}"
    return line


def digest_once(model: RunModel, raw: bool = False, every: int = 25,
                now: float | None = None) -> Iterator[str]:
    """Digest the rows currently on disk in one pass (header omitted).

    Used by --once and as the body of the completed-run path. Yields the
    per-row (2D) / per-chunk (1D) lines for everything landed so far.
    """
    now = now if now is not None else time.time()
    ncols = len(model.cols)
    data = read_rows(model.path, ncols)
    rows = data.shape[0]
    complete = run_complete(model)
    prog = _progress(model, rows, now)
    if model.is_2d:
        full = rows // model.n_fast
        for k in range(full):
            yield _row_line(model, data, k, raw, prog, complete, partial=False)
        if rows % model.n_fast and full < model.n_slow:
            yield _row_line(model, data, full, raw, prog, complete, partial=True)
    else:
        lo = 0
        while lo + every <= rows:
            yield _chunk_line(model, data, lo, lo + every, raw, prog, complete)
            lo += every
        if lo < rows:
            yield _chunk_line(model, data, lo, rows, raw, prog, complete)


def watch(model: RunModel, *, raw: bool = False, every: int = 25,
          poll: float = 5.0, timeout: float | None = 570.0, once: bool = False,
          emit=print, now_fn=time.time, sleep_fn=time.sleep) -> int:
    """Watch loop. Emits header, then per-landed-row lines until the run
    completes, the timeout elapses, or (``once``) a single pass finishes.

    ``timeout`` is a deadline in seconds; ``None`` (follow mode) watches
    until completion with no deadline — for backgrounded multi-hour sweeps
    that must not self-exit and force a re-arm.

    Returns an exit code: 0 normal completion / once, 2 timeout.
    """
    for ln in header_lines(model, raw=raw):
        emit(ln)

    ncols = len(model.cols)
    deadline = None
    timeout_label = None
    if timeout is not None:
        deadline = now_fn() + timeout
        timeout_label = _fmt_dt(timeout)

    if once:
        for ln in digest_once(model, raw=raw, every=every, now=now_fn()):
            emit(ln)
        emit(_footer(model))
        return 0

    emitted_rows = 0   # 2D: slow-rows emitted. 1D: data-rows consumed.
    while True:
        now = now_fn()
        data = read_rows(model.path, ncols)
        rows = data.shape[0]
        complete = run_complete(model)
        prog = _progress(model, rows, now)

        if model.is_2d:
            full = rows // model.n_fast
            while emitted_rows < full:
                emit(_row_line(model, data, emitted_rows, raw, prog,
                               complete, partial=False))
                emitted_rows += 1
            if complete and rows % model.n_fast and emitted_rows < model.n_slow:
                emit(_row_line(model, data, emitted_rows, raw, prog,
                               complete, partial=True))
                emitted_rows += 1
        else:
            while emitted_rows + every <= rows:
                emit(_chunk_line(model, data, emitted_rows,
                                 emitted_rows + every, raw, prog, complete))
                emitted_rows += every
            if complete and emitted_rows < rows:
                emit(_chunk_line(model, data, emitted_rows, rows, raw, prog,
                                 complete))
                emitted_rows = rows

        if complete:
            emit(_footer(model))
            return 0
        if deadline is not None and now >= deadline:
            emit(f"# timeout after {timeout_label} — {rows}/{model.expected_rows} rows")
            return 2
        sleep_fn(poll)


def _footer(model: RunModel) -> str:
    data_rows = read_rows(model.path, len(model.cols)).shape[0]
    meta_path = model.path / "metadata.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = model.meta
    end = _as_float(meta.get("end_time"))
    interrupted = bool(meta.get("interrupted"))
    state = "interrupted" if interrupted else (
        "complete" if data_rows >= model.expected_rows or end else "partial")
    wall = ""
    if model.start_time and end:
        wall = f"  wall {_fmt_dt(end - model.start_time)}"
    return f"# {state}: {data_rows}/{model.expected_rows} rows{wall}"
