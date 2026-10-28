"""Sweep-run analysis primitives for HERA.

A 'run' is a directory written by `sweep` containing:
    data.tsv.gz (or data.tsv)   headerless TSV, one row per setpoint
    metadata.json               column names, sweep config, recipe comments

Open + summarize (`open_run` / `summarize_run`), the lock-in channel/gain
model (`resolve_channels` / `current_channel` — shared with `hera.watch`),
the raw view (`plot_raw` — the first plot of any run, before derived reads),
fan-analysis helpers (`field_invB`, `fan_grids`, `resistance_grids`, `sdh_fft`,
`sdh_onset`),
and the per-session gate calibration (`GateCalibration` / `luttinger_frequency`).
"""

from __future__ import annotations

import gzip
import io
import json
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants


# --------------------------------------------------------------------------
# Lock-in channel / gain model
#
# Shared with hera.watch. The mandatory transform on lock-in data is gain
# division: the physical value of an `srN_X` column is `X / srN_gain`, with
# the gain read from `measurement_config`. Never hardcode a gain (the −1e6
# transimpedance constant is a per-channel mc value, not a universal).
# --------------------------------------------------------------------------

# A lock-in measurement column is the in-phase X reading; its companion
# `_P` (phase) column is not part of the gain model.
_X_COL_RE = re.compile(r"_X$")
# Trailing integer of a channel id keys the mc gain/label: 'sr0' -> 0,
# 'sr830_1' -> 1 (so columns sr0_X and sr830_1_X both map correctly).
_TRAILING_INT_RE = re.compile(r"(\d+)(?!.*\d)")
# A channel is treated as a (transimpedance) current channel — reported in
# amps rather than converted to resistance — if its gain is negative, large
# in magnitude, or its mc label mentions current.
_CURRENT_GAIN_MAG = 1e4


@dataclass
class Channel:
    """One lock-in channel resolved from metadata."""

    col: str          # column name in the TSV, e.g. 'sr0_X'
    idx: int          # column index into the data matrix
    cid: str          # channel id without _X, e.g. 'sr0' / 'sr830_1'
    n: int            # trailing-integer channel index (mc key 'sr{n}')
    gain: float       # measurement_config gain (1.0 if absent)
    label: str        # mc role string, e.g. 'drain current on 42' / '09-01'
    is_current: bool  # report as current (else resistance/voltage)


def _as_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _channel_index(cid: str) -> int | None:
    m = _TRAILING_INT_RE.search(cid)
    return int(m.group(1)) if m else None


def resolve_channels(meta: dict[str, Any], include: list[str] | None = None) -> list[Channel]:
    """Resolve the lock-in `_X` columns of a run into `Channel`s.

    Gains and role labels come from `meta['measurement_config']`. `include`,
    if given, restricts to those channel ids (e.g. ['sr1','sr2']) or column
    names. Handles both rig namings (`sr0_X`↔`sr0_gain`, `sr830_1_X`↔`sr1_gain`).
    """
    cols = list(meta.get("columns") or [])
    mc = meta.get("measurement_config") or {}
    want = set(include) if include else None
    channels: list[Channel] = []
    for idx, col in enumerate(cols):
        if not _X_COL_RE.search(col):
            continue
        cid = _X_COL_RE.sub("", col)
        if want is not None and cid not in want and col not in want:
            continue
        n = _channel_index(cid)
        gain = None
        if f"{cid}_gain" in mc:
            gain = _as_float(mc[f"{cid}_gain"])
        elif n is not None and f"sr{n}_gain" in mc:
            gain = _as_float(mc[f"sr{n}_gain"])
        if gain is None or gain == 0.0:
            gain = 1.0
        label = ""
        if n is not None and isinstance(mc.get(f"sr{n}"), str):
            label = mc[f"sr{n}"]
        elif isinstance(mc.get(cid), str):
            label = mc[cid]
        is_current = gain < 0 or abs(gain) >= _CURRENT_GAIN_MAG or "current" in label.lower()
        channels.append(
            Channel(col=col, idx=idx, cid=cid, n=n if n is not None else -1,
                    gain=gain, label=label, is_current=is_current)
        )
    return channels


def current_channel(channels: list[Channel]) -> Channel | None:
    """The single transimpedance current channel, or None if not exactly one.

    The measured drain current (gain-divided) is the denominator of the
    four-probe resistance R = V / I — see `resistance_grids`.
    """
    currents = [c for c in channels if c.is_current]
    return currents[0] if len(currents) == 1 else None


@dataclass
class Run:
    """A loaded sweep run."""

    path: Path
    meta: dict[str, Any]
    cols: list[str]
    data: np.ndarray  # (rows, ncols), float

    def col(self, name: str) -> np.ndarray:
        """Column named `name` as a 1-D array.

        A duplicated name (a swept param that is also followed writes the
        planned setpoint AND the readback under one name) resolves to the
        first occurrence — the planned/setpoint instance, matching
        `summarize_run` and `FanGrids.grid` — with a warning naming every
        index; `col_at(idx)` selects the others. Raises KeyError if absent.
        """
        idxs = self.col_indices(name)
        if not idxs:
            raise KeyError(f"no column named {name!r}; cols: {self.cols}")
        if len(idxs) > 1:
            warnings.warn(
                f"column {name!r} appears at indices {idxs}; returning index "
                f"{idxs[0]} (the planned/setpoint instance) — col_at(idx) "
                "selects the others",
                stacklevel=2,
            )
        return self.data[:, idxs[0]]

    def col_at(self, idx: int) -> np.ndarray:
        return self.data[:, idx]

    def col_indices(self, name: str) -> list[int]:
        return [i for i, c in enumerate(self.cols) if c == name]

    @property
    def metadata(self) -> dict[str, Any]:
        """Alias for `meta` (the parsed `metadata.json`). The on-disk file,
        the docstrings, and the sweep ecosystem (`w.metadata`,
        `sweep_load.load_meta`) all use 'metadata' — both names resolve here."""
        return self.meta

    @property
    def recipe(self) -> str | None:
        """The recipe slug, conventionally the first metadata comment."""
        comments = self.meta.get("comments") or []
        return comments[0] if comments else None

    @property
    def tags(self) -> list[str]:
        """Comments after the recipe slug (e.g. 'gate: tg')."""
        comments = self.meta.get("comments") or []
        return list(comments[1:])

    @property
    def swept_axis(self) -> str | None:
        """For 1D sweeps, metadata['param']."""
        return self.meta.get("param")

    @property
    def setpoints(self) -> list[float] | None:
        sp = self.meta.get("setpoints")
        return list(sp) if sp is not None else None

    @property
    def interrupted(self) -> bool:
        return bool(self.meta.get("interrupted", False))

    @property
    def complete(self) -> bool:
        """True once sweep has finalized the run (`end_time` lands in
        metadata at close; the interrupt flag also finalizes). An in-flight
        run has neither."""
        return self.meta.get("end_time") is not None or self.interrupted

    @property
    def kind(self) -> str | None:
        return self.meta.get("type")

    @property
    def rows(self) -> int:
        return int(self.data.shape[0])


def open_run(path: str | Path) -> Run:
    """Open a sweep run directory — completed or in flight.

    `path` is the run dir (e.g. `<notebook>/data/119`). Must contain
    `metadata.json` and either `data.tsv.gz` or `data.tsv`. Column names
    come from metadata — TSVs are headerless, and sweep writes `columns`
    to `metadata.json` at sweep start, so names resolve mid-run too. An
    in-flight run's TSV may end mid-row; only newline-terminated rows are
    trusted (sweep writes row-at-a-time, so interior lines are whole).
    """
    path = Path(path).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"not a directory: {path}")

    meta_path = path / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"missing metadata.json in {path}")
    meta = json.loads(meta_path.read_text())

    cols = list(meta.get("columns") or [])
    if not cols:
        raise ValueError(f"metadata.json has no 'columns' entry in {path}")

    tsv_gz = path / "data.tsv.gz"
    tsv = path / "data.tsv"
    if tsv_gz.exists():
        raw = gzip.decompress(tsv_gz.read_bytes())
    elif tsv.exists():
        raw = tsv.read_bytes()
    else:
        raise FileNotFoundError(f"no data.tsv(.gz) in {path}")

    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text and not text.endswith("\n"):
        text = text[: text.rfind("\n") + 1]  # drop the row still being written

    if text.strip():
        data = np.loadtxt(io.StringIO(text), delimiter="\t", ndmin=2)
    else:
        data = np.empty((0, len(cols)), dtype=float)

    if data.shape[1] != len(cols):
        raise ValueError(
            f"column count mismatch in {path}: data has {data.shape[1]} "
            f"cols, metadata declares {len(cols)}"
        )

    return Run(path=path, meta=meta, cols=cols, data=data)


def summarize_run(run: Run) -> str:
    """Multi-line summary: recipe, sweep range, completeness, T.

    Lines with no data are omitted (e.g. no T column → no T line).
    """
    lines: list[str] = [f"run {run.path.name}"]

    kind = run.kind
    lines.append(f"  type:    {kind} sweep" if kind else "  type:    unknown")

    if run.recipe:
        lines.append(f"  recipe:  {run.recipe}")
    if run.tags:
        lines.append(f"  tags:    {', '.join(run.tags)}")

    sp = run.setpoints
    if sp is not None:
        if run.interrupted:
            status = f"interrupted at {run.rows}/{len(sp)}"
        elif run.rows == len(sp):
            status = "complete"
        elif not run.complete:
            status = "in flight"
        else:
            status = f"{run.rows}/{len(sp)} (no interrupt flag, row count differs)"
        lines.append(f"  rows:    {run.rows} of {len(sp)} ({status})")
    else:
        if run.interrupted:
            suffix = " (interrupted)"
        elif not run.complete:
            suffix = " (in flight)"
        else:
            suffix = ""
        lines.append(f"  rows:    {run.rows}{suffix}")

    swept = run.swept_axis
    if swept:
        idxs = run.col_indices(swept)
        if idxs:
            # Duplicate names (planned + readback): first occurrence is the
            # planned setpoint column written by sweep.
            arr = run.data[:, idxs[0]]
            if arr.size:
                lines.append(
                    f"  swept:   {swept} {arr[0]:.4g} → {arr[-1]:.4g} "
                    f"({_monotonic(arr)})"
                )

    # col_indices, not col(): a duplicate 'T' shouldn't warn from a summary.
    t_idxs = run.col_indices("T")
    T = run.data[:, t_idxs[0]] if t_idxs else None
    if T is not None and T.size:
        lines.append(
            f"  T:       mean {T.mean():.3f} K (range {T.min():.3f} – {T.max():.3f})"
        )

    return "\n".join(lines)


def _monotonic(arr: np.ndarray) -> str:
    if arr.size < 2:
        return "single point"
    d = np.diff(arr)
    if np.all(d >= 0) or np.all(d <= 0):
        return "monotonic"
    return "non-monotonic"


# --------------------------------------------------------------------------
# Fan-analysis helpers
#
# Extracted from the 2026-06-10 QC0426 session scratch scripts, where the
# partial-fan grid re-form, the gain-applied resistance grids, and the
# per-column SdH FFT were each hand-rolled across 6+ scripts. The n-axis
# lever-arm *conversion* now lives below in `GateCalibration`; what stays out
# of the helpers are the device's calibration *numbers* (capacitances, CNP
# offset), which the session passes in — these grid helpers are device-agnostic.
# --------------------------------------------------------------------------


def _fast_count(meta: dict[str, Any]) -> int:
    """Points per slow row = length of the (co-swept) fast setpoint vector."""
    fs = meta.get("fast_setpoints")
    if isinstance(fs, list) and fs:
        first = fs[0]
        if isinstance(first, list):
            return len(first)
        if isinstance(first, (int, float)):
            return len(fs)
    raise ValueError("metadata has no usable 'fast_setpoints'; not a 2D fan?")


def _slow_param(meta: dict[str, Any]) -> str | None:
    sp = meta.get("slow_params") or meta.get("slow_param")
    if isinstance(sp, list):
        return sp[0] if sp else None
    return sp if isinstance(sp, str) else None


@dataclass
class FanGrids:
    """Complete-rows-only 2D reform of a (possibly partial) fan."""

    nrows: int                 # complete slow rows landed
    nfast: int                 # points per slow row
    cols: list[str]
    data: np.ndarray           # (nrows*nfast, ncols), truncated to whole rows
    meta: dict[str, Any]
    slow_param: str | None

    def grid(self, name: str) -> np.ndarray:
        """Column `name` as a (nrows, nfast) grid. Duplicate names resolve to
        the first occurrence (the planned setpoint, not the readback)."""
        return self.data[:, self.cols.index(name)].reshape(self.nrows, self.nfast)

    @property
    def metadata(self) -> dict[str, Any]:
        """Alias for `meta` — matches `Run.metadata` (see there)."""
        return self.meta

    @property
    def slow(self) -> np.ndarray:
        """Slow-axis value per row, (nrows,)."""
        if self.slow_param and self.slow_param in self.cols:
            return self.grid(self.slow_param)[:, 0]
        raise KeyError("slow param not in columns; pass the axis explicitly")


def fan_grids(run: "str | Path | Run", columns: list[str] | None = None) -> FanGrids:
    """Re-form a 2D fan into per-column grids, keeping only complete slow rows.

    `run` is a run directory or an already-loaded `Run`. `nfast` comes from
    metadata (never hardcoded); trailing rows of an in-progress sweep are
    dropped via `nrows = total // nfast`. `columns` restricts which columns
    are retained in `.data`/`.cols` (the reshape is unaffected).
    """
    r = run if isinstance(run, Run) else open_run(run)
    nfast = _fast_count(r.meta)
    nrows = r.data.shape[0] // nfast
    data = r.data[: nrows * nfast]
    cols = r.cols
    if columns is not None:
        keep = [r.cols.index(c) for c in columns]
        data = data[:, keep]
        cols = list(columns)
    return FanGrids(nrows=nrows, nfast=nfast, cols=cols, data=data,
                    meta=r.meta, slow_param=_slow_param(r.meta))


@dataclass
class ResistanceGrids:
    """Gain-applied four-probe resistances, using the measured current."""

    current: np.ndarray            # I grid (nrows, nfast), amps
    current_channel: str           # cid of the transimpedance channel
    R: dict[str, np.ndarray]       # voltage cid -> signed R grid (Ω)


def resistance_grids(fan: FanGrids, channels: list[str] | None = None) -> ResistanceGrids:
    """Per-channel resistance grids `R = (V/gain_V) / I` from a `FanGrids`.

    The denominator is the *measured* drain current `I = X_cur / gain_cur`
    (a grid — it sags where the device is resistive), not a nominal bias
    current. Gains come from `measurement_config` (shared `resolve_channels`);
    nothing is hardcoded. Returned R is **signed** (X/I) — take `np.abs` for
    Rxx magnitude, keep the sign for Rxy/Hall. `channels` restricts the
    voltage channels returned (the current channel is always resolved).
    """
    all_chans = resolve_channels(fan.meta)
    cur = current_channel(all_chans)
    if cur is None:
        n_cur = sum(c.is_current for c in all_chans)
        raise ValueError(
            f"need exactly one current channel to form resistance; found {n_cur}. "
            "Pass it via measurement_config gains (transimpedance gain is negative "
            "or |gain| >= 1e4)."
        )
    want = set(channels) if channels else None
    I = fan.grid(cur.col) / cur.gain
    with np.errstate(divide="ignore", invalid="ignore"):
        R = {
            v.cid: (fan.grid(v.col) / v.gain) / I
            for v in all_chans
            if not v.is_current and (want is None or v.cid in want or v.col in want)
        }
    return ResistanceGrids(current=I, current_channel=cur.cid, R=R)


def plot_raw(run: "str | Path | Run", channels: list[str] | None = None):
    """Canonical raw view of a run — the first plot, before any derived read.

    Every lock-in channel, gain-divided, on the run's own axes: 1D as traces
    vs the swept axis; 2D (fan/megasweep) as one pcolormesh per channel over
    (fast index, slow value), complete rows only. Voltage channels plot as
    signed R = (V/gain)/I against the measured current when a transimpedance
    channel resolves, else as V/gain; the current channel plots as I. No log,
    no clipping, no background removal — rails, dead/flat channels, streaks,
    and drift are visible here and hidden by derived views. Returns the Figure.
    """
    r = run if isinstance(run, Run) else open_run(run)
    all_chans = resolve_channels(r.meta)
    chans = all_chans
    if channels is not None:
        want = set(channels)
        chans = [c for c in all_chans if c.cid in want or c.col in want]
    if not chans:
        raise ValueError("no lock-in channels resolved from measurement_config")
    cur = current_channel(all_chans)

    try:
        _fast_count(r.meta)
        is_2d = True
    except ValueError:
        is_2d = False

    def _series(values: np.ndarray, c: Channel, I: np.ndarray | None):
        if c.is_current:
            return values, f"{c.cid or c.col} I (A)"
        if I is not None:
            with np.errstate(divide="ignore", invalid="ignore"):
                return values / I, f"{c.cid or c.col} R (Ω)"
        return values, f"{c.cid or c.col} V (V)"

    if is_2d:
        fan = fan_grids(r)
        if fan.nrows == 0:
            raise ValueError(f"run {r.path.name}: no complete slow rows yet")
        try:
            y, ylabel = fan.slow, fan.slow_param
        except KeyError:
            y, ylabel = np.arange(fan.nrows), "slow row"
        x = np.arange(fan.nfast)
        I = fan.grid(cur.col) / cur.gain if cur is not None else None
        fig, axes = plt.subplots(1, len(chans), figsize=(4.6 * len(chans), 4.2),
                                 sharey=True, squeeze=False)
        for ax, c in zip(axes[0], chans):
            z, zlabel = _series(fan.grid(c.col) / c.gain, c, I)
            pm = ax.pcolormesh(x, y, z, shading="auto")
            fig.colorbar(pm, ax=ax, label=zlabel)
            ax.set_title(c.cid or c.col)
            ax.set_xlabel("fast idx")
        axes[0][0].set_ylabel(ylabel or "slow")
    else:
        x, xlabel = np.arange(r.rows), "row"
        if r.swept_axis:
            idxs = r.col_indices(r.swept_axis)
            if idxs:
                x, xlabel = r.data[:, idxs[0]], r.swept_axis
        I = r.data[:, cur.idx] / cur.gain if cur is not None else None
        fig, axes = plt.subplots(len(chans), 1, figsize=(9, 2.4 * len(chans)),
                                 sharex=True, squeeze=False)
        for ax, c in zip(axes[:, 0], chans):
            yv, ylab = _series(r.data[:, c.idx] / c.gain, c, I)
            ax.plot(x, yv, lw=0.7)
            ax.set_ylabel(ylab)
        axes[-1][0].set_xlabel(xlabel)

    fig.suptitle(f"run {r.path.name} — raw ({r.recipe or 'no recipe tag'})")
    fig.tight_layout()
    return fig


def field_invB(B_start: float, B_end: float, N: int) -> np.ndarray:
    """Field axis of `N` points from `B_start` to `B_end`, uniform in 1/B.

    SdH oscillations are periodic in 1/B, so an FFT-bound field sweep samples
    evenly in 1/B (not in B). This is the measurement-side companion to
    `sdh_fft`'s uniform-1/B path: sweeping `field_invB` hands `sdh_fft` an
    already-even 1/B record (no resample). Argument order sets the sweep
    direction — high `B_start` descends, low `B_start` ascends.

    Both endpoints must be > 0 (1/B is taken). Returns `(N,)` Tesla.
    """
    if B_start <= 0 or B_end <= 0:
        raise ValueError(f"field_invB endpoints must be > 0; got {B_start}, {B_end}")
    return 1.0 / np.linspace(1.0 / B_start, 1.0 / B_end, N)


def _window(name: str | None, n: int) -> np.ndarray:
    if name is None or name == "none":
        return np.ones(n)
    if name in ("hann", "hanning"):
        return np.hanning(n)
    if name == "hamming":
        return np.hamming(n)
    if name in ("blackman",):
        return np.blackman(n)
    raise ValueError(f"unknown window {name!r}")


def _is_uniform(x: np.ndarray, rtol: float) -> bool:
    """True if ascending `x` is evenly spaced to within `rtol`.

    Decided from the spacing *distribution* (coefficient of variation of the
    diffs), never from an assumed step. Uniform-in-1/B runs land near 0; a
    uniform-in-B sweep, viewed in 1/B, has a CoV of order 1.
    """
    if x.size < 3:
        return True
    d = np.diff(x)
    md = d.mean()
    if md == 0:
        return False
    return float(d.std() / abs(md)) <= rtol


def _bg_subtract_B(B: np.ndarray, y: np.ndarray, degree: int) -> np.ndarray:
    """Degree-`degree` polynomial background removal in **B-space**, then
    mean-subtract.

    The magnetoresistance background is smooth in B, not in 1/B, so it must be
    removed on the raw B axis before the 1/B resample — a 1/B-space detrend
    leaves background residual that piles into the low-frequency FFT bins and
    inflates low-frequency tones. NaN-aware (skips non-finite samples in the
    fit). Mirrors `sharpelab_nb.qo.remove_polynomial_background`, inlined to
    keep `hera.analysis` free of the `sweep`-importing `sharpelab_nb` package.
    """
    idx = np.isfinite(B) & np.isfinite(y)
    coeff = np.polyfit(B[idx], y[idx], degree)
    cleaned = y - np.polyval(coeff, B)
    cleaned -= np.nanmean(cleaned)
    return cleaned


def sdh_fft(
    R_grid: np.ndarray,
    B: np.ndarray,
    *,
    b_range: tuple[float, float] | None = None,
    nfft: int = 512,
    bg_degree: int | None = 5,
    window: str | None = "hann",
    log: bool = True,
    floor: float = 1.0,
    uniform_rtol: float = 0.1,
) -> tuple[np.ndarray, np.ndarray]:
    """Per-column Shubnikov–de Haas FFT in 1/B.

    `R_grid` is `(n_B, n_fast)` (rows = field, the `FanGrids` row axis); `B`
    is the per-row field `(n_B,)` — arbitrarily spaced. For each column:
    select `b_range`, optionally `log10(max(R, floor))`, remove a degree-
    `bg_degree` polynomial background in **B-space** (`None` skips), then take
    the FFT in 1/B. The background subtraction happens on the raw B axis
    *before* the 1/B step because the MR background is smooth in B, not 1/B.

    The 1/B resample is **conditional**. The field may be swept uniformly in
    1/B (then the samples are already evenly spaced in 1/B and are FFT'd
    directly, zero-padded to `nfft`) or uniformly in B (then the 1/B samples
    are resampled onto a regular `nfft`-point grid by interpolation against
    **sorted** 1/B). Which path is taken is decided from the actual 1/B
    spacing distribution (`uniform_rtol`), not an assumed step.

    Returns `(freqs, spec)` — `freqs` in Tesla `(n_freq,)`, `spec` the FFT
    magnitude `(n_fast, n_freq)`.
    """
    B = np.asarray(B, dtype=float)
    R_grid = np.asarray(R_grid, dtype=float)
    if R_grid.shape[0] != B.shape[0]:
        raise ValueError(f"R_grid rows {R_grid.shape[0]} != len(B) {B.shape[0]}")
    sel = np.ones(B.shape, dtype=bool) if b_range is None else (B >= b_range[0]) & (B <= b_range[1])
    if sel.sum() < 4:
        raise ValueError(f"need >=4 field rows in b_range; got {int(sel.sum())}")
    Bsel = B[sel]
    invB = 1.0 / Bsel
    order = np.argsort(invB)
    invB_sorted = invB[order]

    uniform = _is_uniform(invB_sorted, uniform_rtol)
    if uniform:
        m = invB_sorted.size
        du = (invB_sorted[-1] - invB_sorted[0]) / (m - 1)
        nout = max(nfft, m)
        win = _window(window, m)
    else:
        u = np.linspace(invB_sorted[0], invB_sorted[-1], nfft)
        du = u[1] - u[0]
        nout = nfft
        win = _window(window, nfft)
    freqs = np.fft.rfftfreq(nout, du)  # Tesla

    spec = np.zeros((R_grid.shape[1], freqs.size))
    for j in range(R_grid.shape[1]):
        y = R_grid[sel, j]
        if log:
            y = np.log10(np.maximum(y, floor))
        if bg_degree is not None:
            y = _bg_subtract_B(Bsel, y, bg_degree)
        ys = y[order]
        if uniform:
            spec[j] = np.abs(np.fft.rfft(ys * win, n=nout))
        else:
            yi = np.interp(u, invB_sorted, ys)
            spec[j] = np.abs(np.fft.rfft(yi * win))
    return freqs, spec


class SdhOnsetError(ValueError):
    """`sdh_onset` cannot produce a trustworthy onset.

    Raised instead of returning nan: an onset feeds fan design (`landau-fan`
    step 1 sets `B_lo` from it), so an uncomputable onset must stop the design
    cell loudly, with specifics, rather than flow into it as a bare number.
    The message names what failed (record too short / no tones above floor /
    no tone trackable) and why, per tone where applicable.
    """


@dataclass
class SdhTone:
    """One SdH tone's onset track from the matched-filter walk.

    `snr`/`amp` are per-window curves over `b_centers` (high-B → low-B). The
    filter is a Gaussian-windowed complex correlation at fixed `freq` whose
    FWHM spans `n_periods` periods of that tone (support `win_invB` in 1/B);
    SNR is amplitude over the record's white-noise floor, so a light tone and
    a heavy tone are each judged in their own natural window.
    """

    freq: float               # tone frequency, Tesla (record-resolution FFT)
    contrast: float           # tone-ID peak over the record spectral floor
    onset_b: float            # low-B onset, Tesla (record low edge if censored)
    censored: bool            # still above threshold in the lowest window
    revived: bool             # above-threshold windows exist below the walk stop
    marginal: bool            # peak SNR < marginal_mult x threshold everywhere
    near_residual: bool       # filter passband overlaps the detrend-residual band
    n_periods: float          # filter FWHM in periods (shrunk if record short)
    win_invB: float           # filter support width, 1/T
    harmonic_of: float | None  # freq of the lower tone this sits at ~k x of (fund.)
    harmonics: tuple[float, ...]  # freqs of tones that sit at ~k x of this one
    b_centers: np.ndarray     # per-window center field, descending (n_win,)
    snr: np.ndarray           # matched-filter SNR per window (n_win,)
    amp: np.ndarray           # matched-filter amplitude per window, Ohm-units

    def delta_f(self, b_max: float) -> float:
        """FFT resolution δF = 1/(1/onset_b − 1/b_max) over this tone's usable
        record — the per-tone version of the landau-fan design number."""
        return 1.0 / (1.0 / self.onset_b - 1.0 / b_max)


@dataclass
class SdhOnset:
    """Per-tone SdH onsets over the usable field window.

    `onset_b` is the headline: the lowest onset over non-marginal tracked
    tones — the low-B edge of usable oscillation content, which is the
    `landau-fan` step-1 `B_lo` contract (a light tone alive below the dominant
    tone's edge carries it). Everything behind it is in `tones` (per-tone
    onsets, SNR curves, censored/revived/marginal flags) and `untracked`
    (tones seen in the record-wide FFT but not trackable, with reasons).
    `summary()` renders the whole read for a notebook cell.
    """

    onset_b: float                       # min onset over robust tones, Tesla
    onset_freq: float                    # freq of the tone carrying onset_b
    clip_high_b: float                   # high edge of the analyzed window
    b_lo_record: float                   # low-B edge of the analyzed record
    noise_sigma: float                   # per-sample white-noise sigma used
    tones: list[SdhTone]                 # tracked tones, by contrast desc
    untracked: list[tuple[float, str]]   # (freq, reason) for untrackable tones

    @property
    def consensus_freq(self) -> float:
        """Dominant (highest-contrast) tone frequency, Tesla."""
        return self.tones[0].freq

    @property
    def b_centers(self) -> np.ndarray:
        """Dominant tone's window centers (see `tones` for the rest)."""
        return self.tones[0].b_centers

    @property
    def snr(self) -> np.ndarray:
        """Dominant tone's SNR curve (see `tones` for the rest)."""
        return self.tones[0].snr

    def summary(self) -> str:
        """Multi-line read for a notebook cell: headline, per-tone table,
        untracked tones with reasons."""
        carrier = f"tone {self.onset_freq:.1f} T"
        lines = [
            f"sdh_onset: onset_b = {self.onset_b:.2f} T ({carrier}) over "
            f"B [{self.b_lo_record:.2f}, {self.clip_high_b:.2f}] T"
        ]
        for t in self.tones:
            flags = [f for f, on in (("censored@edge", t.censored),
                                     ("revives-below-gap", t.revived),
                                     ("marginal", t.marginal),
                                     ("near-residual", t.near_residual)) if on]
            if t.harmonic_of is not None:
                k = t.freq / t.harmonic_of
                flags.append(f"~{k:.0f}x{t.harmonic_of:.1f}T")
            for fh in t.harmonics:
                flags.append(f"{round(fh / t.freq):.0f}x->{fh:.1f}T")
            tag = f"  [{', '.join(flags)}]" if flags else ""
            lines.append(
                f"  tone {t.freq:6.1f} T: onset {t.onset_b:5.2f} T  "
                f"dF {t.delta_f(self.clip_high_b):5.2f} T  "
                f"snr_max {np.nanmax(t.snr):6.1f}{tag}"
            )
        for f_t, reason in self.untracked:
            lines.append(f"  tone {f_t:6.1f} T: UNTRACKED — {reason}")
        return "\n".join(lines)


def _win_fft(
    invB: np.ndarray, y: np.ndarray, lo: float, hi: float,
    min_pts: int, pad: int = 8,
) -> tuple[np.ndarray, np.ndarray, float] | None:
    """Hann + zero-padded FFT of the 1/B slice [lo, hi], resampled uniform.

    Returns `(freqs, |spec|, dF)` with `dF = 1/(hi-lo)` the true (unpadded)
    frequency resolution, or None if fewer than `min_pts` samples land in the
    slice. Padding interpolates bins so band/peak positions are not quantized
    to dF — the no-padding 5.6 T bin grid was the root of the empty/leakage
    noise-band failures this module had.
    """
    m = (invB >= lo) & (invB <= hi)
    npt = int(m.sum())
    if npt < min_pts:
        return None
    iw, yw = invB[m], y[m]
    u = np.linspace(iw[0], iw[-1], npt)
    yi = np.interp(u, iw, yw)
    nfft = int(2 ** np.ceil(np.log2(pad * npt)))
    spec = np.abs(np.fft.rfft(yi * np.hanning(npt), n=nfft))
    freqs = np.fft.rfftfreq(nfft, (iw[-1] - iw[0]) / (npt - 1))
    return freqs, spec, 1.0 / (iw[-1] - iw[0])


def _tone_id(
    invB: np.ndarray, bg: np.ndarray, f_min: float, floor_mult: float,
    max_tones: int, min_pts: int, n_periods: float, resid_bins: float = 5.0,
) -> tuple[list[tuple[float, float, float | None, tuple[float, ...]]], list[str]]:
    """Identify SdH tones over nested high-B subwindows of the record.

    FFTs the full 1/B span, then the high-B half, quarter, ... (a tone confined
    to a narrow high-B band — e.g. a heavy tone above its own onset — is
    diluted below the floor in the full-span FFT but stands out in a subwindow
    that matches its support; this replaces the old per-window argmax-median
    "consensus", which multi-tone records defeated). Peaks must clear
    `floor_mult` x the median floor and sit above `resid_bins` resolution bins
    (below that they are indistinguishable from detrend residual). Candidates
    within one resolution bin merge, best contrast wins. The final trim to
    `max_tones` prefers tones that are NOT ~k x an already-kept tone, so a
    strong tone's harmonic comb cannot crowd out a weak independent
    fundamental (the multi-band / tetralayer case).

    Candidates within the *tracking* filter bandwidth (2σ_f = 0.75·f/n_periods)
    of a stronger kept tone also merge into it: sub-bandwidth splits are not
    independently trackable — their filters mirror each other — so they are
    one tone here (a close pair shows up as beating, disclosed by the
    revived/gap flags downstream).

    Harmonic relationships are annotated bidirectionally over the final kept
    set (a strong tone that is k*x of a weaker one is marked from both ends —
    see the post-pass), so amplitude ordering can never hide a comb member.

    Returns `([(freq, contrast, harmonic_of, harmonics), ...], scan_diagnostics)`.
    """
    span = invB[-1] - invB[0]
    cands: list[tuple[float, float, float]] = []  # (freq, contrast, dF)
    diags: list[str] = []
    frac = 1.0
    while True:
        out = _win_fft(invB, bg, invB[0], invB[0] + span * frac, min_pts)
        if out is None:
            break
        fr, spec, dF = out
        npt = int(((invB >= invB[0]) & (invB <= invB[0] + span * frac)).sum())
        f_lo = max(f_min, resid_bins * dF)
        sel = fr >= f_lo
        floor = float(np.median(spec[sel]))
        s = np.where(sel, spec, 0.0)
        pk = np.where((s[1:-1] > s[:-2]) & (s[1:-1] >= s[2:]) &
                      (s[1:-1] > floor_mult * max(floor, 1e-300)))[0] + 1
        pk = pk[np.argsort(spec[pk])[::-1]][: 2 * max_tones]
        diags.append(
            f"span x{frac:.3g} (dF {dF:.2f} T): "
            + (", ".join(f"{fr[i]:.1f} T" for i in pk) if pk.size else "no peaks")
        )
        for i in pk:
            cands.append((float(fr[i]), float(spec[i] / max(floor, 1e-300)), dF))
        if npt // 2 < 4 * min_pts or frac < 0.1:
            break
        frac /= 2.0

    cands.sort(key=lambda t: -t[1])
    clusters: list[list[float]] = []  # [freq, contrast, dF] per tone
    for f_new, a_new, dF in cands:
        for entry in clusters:
            if abs(f_new - entry[0]) < max(dF, entry[2], 0.75 * entry[0] / n_periods):
                if dF < entry[2]:  # finer scan localizes the tone better
                    entry[0], entry[2] = f_new, dF
                entry[1] = max(entry[1], a_new)
                break
        else:
            clusters.append([f_new, a_new, dF])
    merged = [(f, a, dF) for f, a, dF in clusters]

    def _harmonic_of(f: float, dF: float, kept: list[list[float]]) -> float | None:
        for f_k, _, _ in kept:
            if f > 1.5 * f_k:
                k = round(f / f_k)
                if k >= 2 and abs(f - k * f_k) < max(dF, 0.05 * f):
                    return f_k
        return None

    kept: list[list[float]] = []          # [freq, contrast, dF]
    deferred: list[tuple[float, float, float]] = []
    for f_new, a_new, dF in merged:               # non-harmonics first
        if _harmonic_of(f_new, dF, kept) is None:
            kept.append([f_new, a_new, dF])
        else:
            deferred.append((f_new, a_new, dF))
        if len(kept) >= max_tones:
            break
    for f_new, a_new, dF in deferred:             # harmonics fill leftover slots
        if len(kept) >= max_tones:
            break
        kept.append([f_new, a_new, dF])

    # Bidirectional harmonic annotation over the final kept set, independent of
    # amplitude order: for every ordered pair with f_j ~ k*f_i (k>=2, same
    # tolerance as the trim), f_j points at its fundamental f_i (harmonic_of)
    # and f_i lists f_j (harmonics). A tone that is k*x of a *weaker* tone is
    # annotated too, so a dominant harmonic can never hide its fundamental;
    # harmonic_of picks the strongest matching fundamental when several fit.
    n = len(kept)
    freqs = [entry[0] for entry in kept]
    hof: list[float | None] = [None] * n
    harms: list[list[float]] = [[] for _ in range(n)]
    for j in range(n):
        f_j, _, dF_j = kept[j]
        best_i, best_c = -1, -1.0
        for i in range(n):
            if i == j:
                continue
            f_i, c_i, _ = kept[i]
            if f_j > 1.5 * f_i and round(f_j / f_i) >= 2 \
                    and abs(f_j - round(f_j / f_i) * f_i) < max(dF_j, 0.05 * f_j) \
                    and c_i > best_c:
                best_i, best_c = i, c_i
        if best_i >= 0:
            hof[j] = freqs[best_i]
            harms[best_i].append(f_j)
    return (
        [(freqs[i], kept[i][1], hof[i], tuple(sorted(harms[i]))) for i in range(n)],
        diags,
    )


def _noise_sigma(bg: np.ndarray) -> float:
    """Per-sample white-noise sigma of the detrended record.

    MAD of the first difference over the low-B (high-1/B) third, where SdH is
    weakest, cross-checked against the global MAD (take the min — oscillation
    content only inflates the estimate, so the smaller is the cleaner read).
    Floored relative to the record so a noiseless synthetic cannot divide by
    zero.
    """
    d = np.diff(bg)
    mads = []
    for arr in (d[2 * d.size // 3:], d):
        if arr.size >= 8:
            mads.append(1.4826 * float(np.median(np.abs(arr - np.median(arr)))))
    sigma = min(mads) / np.sqrt(2.0) if mads else 0.0
    floor = 1e-9 * float(np.max(np.abs(bg))) if bg.size else 0.0
    return max(sigma, floor, 1e-300)


def _track_tone(
    invB: np.ndarray, bg: np.ndarray, f_t: float, sigma: float, *,
    n_periods: float, min_periods: float, step_frac: float, min_pts: int,
    snr_threshold: float, gap_widths: float, marginal_mult: float,
) -> tuple[dict[str, Any] | None, str | None]:
    """Walk one tone's Gaussian matched filter from high B down to its onset.

    At each center the filter is a Gaussian envelope (FWHM = `n_periods`
    periods of `f_t`, shrunk toward `min_periods` if the record is short)
    times a complex exponential at `f_t`; SNR is the analytic amplitude-over-
    white-noise ratio, so the floor can never be empty, zero, or contaminated
    by another tone's leakage (Gaussian frequency rejection is ~e^-30 one
    octave away — the annulus/median floors this replaces failed both ways).

    The onset is the lowest-B window still connected to the high-B track,
    riding sub-threshold gaps up to `gap_widths` filter widths — wider gaps
    disconnect (an isolated low-B feature within one filter width lights
    ~1/step_frac consecutive windows by self-correlation, so gap width, not
    run length, is the spike discriminator). Above-threshold windows below a
    disconnection set `revived`. Returns `(track, None)` or `(None, reason)`.
    """
    span = invB[-1] - invB[0]
    n_fit = span * f_t * 2.355 / 5.0
    n_eff = min(n_periods, n_fit)
    if n_eff < min_periods:
        return None, (
            f"needs {5.0 * min_periods / 2.355 / f_t:.2f}/T of record for "
            f"{min_periods:g} periods at {f_t:.1f} T; record spans {span:.2f}/T"
        )
    sigma_u = n_eff / f_t / 2.355
    w = 5.0 * sigma_u
    step = w * step_frac
    # Anchor the grid at the low-B end: the last window's support must touch
    # the record edge exactly, so a censored track's "persists to the edge"
    # claim never extends beyond measured data (any grid shortfall from the
    # step quantization lands at the high-B end instead, where it is inert).
    centers_u = np.arange(invB[-1] - w / 2, invB[0] + w / 2 - 1e-12, -step)[::-1]
    Bc_l, snr_l, amp_l = [], [], []
    for u0 in centers_u:
        m = np.abs(invB - u0) <= 2.5 * sigma_u
        if int(m.sum()) < min_pts:
            continue
        iu, yv = invB[m], bg[m]
        g = np.exp(-0.5 * ((iu - u0) / sigma_u) ** 2)
        z = np.sum(yv * g * np.exp(-2j * np.pi * f_t * iu))
        norm = 0.5 * np.sum(g)          # cosine of amplitude a -> |z| ~ a*norm
        A = float(np.abs(z)) / norm
        sig_A = sigma * float(np.sqrt(np.sum(g ** 2) / 2.0)) / norm
        Bc_l.append(1.0 / u0)
        amp_l.append(A)
        snr_l.append(A / sig_A)
    if not Bc_l:
        return None, f"no {w:.2f}/T window holds >= {min_pts} points"
    Bc, snr, amp = np.array(Bc_l), np.array(snr_l), np.array(amp_l)
    good = snr >= snr_threshold
    if not good.any():
        return None, (f"never above threshold (max SNR {snr.max():.1f} vs "
                      f"{snr_threshold:g} across {Bc.size} windows)")
    max_gap = int(np.ceil(gap_widths / step_frac))
    onset_idx, gap, started = 0, 0, False
    for i in range(Bc.size):
        if good[i]:
            onset_idx, gap, started = i, 0, True
        elif started:
            gap += 1
            if gap > max_gap:
                break
    return {
        "freq": f_t,
        "onset_b": float(Bc[onset_idx]),
        "censored": bool(onset_idx == Bc.size - 1),
        "revived": bool(good[onset_idx + 1 + max_gap:].any()),
        "marginal": bool(float(snr.max()) < marginal_mult * snr_threshold),
        "n_periods": float(n_eff),
        "win_invB": float(w),
        "b_centers": Bc,
        "snr": snr,
        "amp": amp,
    }, None


def sdh_onset(
    R: np.ndarray,
    B: np.ndarray,
    *,
    b_hi: float | None = None,
    b_lo: float = 0.3,
    r_full_scale: float | None = None,
    headroom: float = 0.95,
    bg_degree: int = 5,
    f_min: float = 3.0,
    snr_threshold: float = 5.0,
    n_periods: float = 3.0,
    min_periods: float = 2.0,
    step_frac: float = 0.25,
    gap_widths: float = 0.5,
    min_pts: int = 8,
    max_tones: int = 8,
    tone_floor_mult: float = 4.0,
    marginal_mult: float = 2.0,
) -> SdhOnset:
    """Per-tone low-B onsets of the SdH oscillations in a single Rxx trace.

    `R` is one longitudinal-resistance trace `(n_B,)`, `B` the matching field
    `(n_B,)` (arbitrary spacing). Removes a degree-`bg_degree` B-space
    polynomial background, identifies every SdH tone via nested high-B FFT
    scans (`_tone_id`), then walks each tone's Gaussian matched filter from
    high B down to where it sinks into the record's white-noise floor
    (`_track_tone` — a 5σ-style statistical onset, which legitimately sits
    below a by-eye read).

    Returns an `SdhOnset`; `onset_b` is the minimum onset over non-marginal
    tones — the `B_lo` a `landau-fan` design should use, correct even when a
    light tone outlives the dominant tone (per-dominant-tone semantics
    silently mis-served light-tone hunts). A tone still above threshold in
    its lowest window is *censored*: its onset is the record's low edge and a
    warning notes oscillations persist to the end of the record.

    If `r_full_scale` is given (sensitivity / I_bias, Ohms), samples at
    ≥ `headroom` x full scale soft-clip: the analysis window is truncated
    below the lowest clipped field, `clip_high_b` reports the truncation, and
    a warning fires. Without it no clip detection is attempted.

    Failure is never a nan: raises `SdhOnsetError` (record too short, no tones
    above the spectral floor, or no identified tone trackable), with the scan
    diagnostics in the message. Partial failures warn and land in
    `SdhOnset.untracked`.
    """
    B = np.asarray(B, dtype=float)
    R = np.asarray(R, dtype=float)
    if R.shape != B.shape:
        raise ValueError(f"R shape {R.shape} != B shape {B.shape}")
    b_hi = float(np.nanmax(B)) if b_hi is None else float(b_hi)

    if r_full_scale is not None:
        clipped = np.abs(R) >= headroom * r_full_scale
        if clipped.any():
            b_clip = float(B[clipped].min())
            warnings.warn(
                f"sdh_onset: |R| reaches {float(np.abs(R).max()):.3g} Ω vs "
                f"full scale {r_full_scale:g} Ω (soft clip, ≥{headroom:g}x "
                f"from B = {b_clip:.2f} T); analysis window truncated to "
                f"{b_clip:.2f} T",
                stacklevel=2,
            )
            b_hi = min(b_hi, b_clip)

    sel = (B >= b_lo) & (B <= b_hi)
    Bs, Rs = B[sel], R[sel]
    if Bs.size < min_pts:
        raise SdhOnsetError(
            f"need >={min_pts} field rows in [{b_lo:g}, {b_hi:g}] T; got {Bs.size}"
        )
    bg = _bg_subtract_B(Bs, Rs, bg_degree)
    invB = 1.0 / Bs
    order = np.argsort(invB)
    invB, bg = invB[order], bg[order]
    b_lo_record = float(1.0 / invB[-1])

    tones, diags = _tone_id(invB, bg, f_min, tone_floor_mult, max_tones,
                            min_pts, n_periods)
    if not tones:
        raise SdhOnsetError(
            f"no SdH tones above {tone_floor_mult:g}x the spectral floor in "
            f"B [{b_lo_record:.2f}, {Bs.max():.2f}] T — nested scans: "
            + "; ".join(diags)
        )

    sigma = _noise_sigma(bg)
    f_resid = max(f_min, 5.0 / (invB[-1] - invB[0]))  # detrend-residual band edge
    tracks: list[SdhTone] = []
    untracked: list[tuple[float, str]] = []
    for f_t, contrast, harm, harms in tones:
        tr, reason = _track_tone(
            invB, bg, f_t, sigma, n_periods=n_periods, min_periods=min_periods,
            step_frac=step_frac, min_pts=min_pts, snr_threshold=snr_threshold,
            gap_widths=gap_widths, marginal_mult=marginal_mult,
        )
        if tr is None:
            untracked.append((f_t, reason or "untrackable"))
            continue
        onset_t = b_lo_record if tr["censored"] else tr["onset_b"]
        # Gaussian filter sigma_f = 0.375 f/n; a passband reaching below the
        # residual edge means the track can be background, not tone.
        sigma_f = 0.375 * f_t / tr["n_periods"]
        tracks.append(SdhTone(
            freq=f_t, contrast=contrast, onset_b=onset_t,
            censored=tr["censored"], revived=tr["revived"],
            marginal=tr["marginal"],
            near_residual=bool(f_t - 2.0 * sigma_f < f_resid),
            n_periods=tr["n_periods"],
            win_invB=tr["win_invB"], harmonic_of=harm, harmonics=harms,
            b_centers=tr["b_centers"], snr=tr["snr"], amp=tr["amp"],
        ))
    if not tracks:
        raise SdhOnsetError(
            "tones found but none trackable: "
            + "; ".join(f"{f:.1f} T — {r}" for f, r in untracked)
        )
    if untracked:
        warnings.warn(
            "sdh_onset: untracked tone(s): "
            + "; ".join(f"{f:.1f} T ({r})" for f, r in untracked),
            stacklevel=2,
        )

    # A near-residual tone corroborated by a *weaker* tracked harmonic pointing
    # at it rejoins the headline pool: demanding the light fundamental dominate
    # its own harmonic (o.contrast < t.contrast) is true of a real Dingle-damped
    # light pocket (capstone r5's 4 T tone, whose record-edge onset the fan
    # design used), false of a detrend-residual bump (session-3's wandering
    # ~5.8 T content has no harmonics). The strength test is explicit because
    # harmonic_of is now bidirectional and can point at a weaker tone too.
    corroborated = {
        t.freq for t in tracks
        if t.near_residual
        and any(o.harmonic_of == t.freq and o.contrast < t.contrast for o in tracks)
    }
    robust = [t for t in tracks if not t.marginal
              and (not t.near_residual or t.freq in corroborated)]
    pool = robust if robust else tracks
    carrier = min(pool, key=lambda t: t.onset_b)
    if robust:
        overall_min = min(tracks, key=lambda t: t.onset_b)
        if overall_min.onset_b < carrier.onset_b:
            why = "marginal" if overall_min.marginal else "near-residual"
            warnings.warn(
                f"sdh_onset: {why} tone {overall_min.freq:.1f} T would carry "
                f"the onset ({overall_min.onset_b:.2f} T) — excluded; "
                f"onset_b = {carrier.onset_b:.2f} T from the "
                f"{carrier.freq:.1f} T tone",
                stacklevel=2,
            )
    else:
        warnings.warn(
            "sdh_onset: every tracked tone is marginal or near-residual; "
            "onset_b is low-confidence",
            stacklevel=2,
        )
    if carrier.censored:
        warnings.warn(
            f"sdh_onset: tone {carrier.freq:.1f} T is above threshold through "
            f"the lowest window — oscillations persist to the record's low "
            f"edge; onset_b = {carrier.onset_b:.2f} T is the record edge, "
            "not a measured die-off",
            stacklevel=2,
        )

    return SdhOnset(
        onset_b=carrier.onset_b, onset_freq=carrier.freq, clip_high_b=b_hi,
        b_lo_record=b_lo_record, noise_sigma=sigma,
        tones=sorted(tracks, key=lambda t: -t.contrast), untracked=untracked,
    )


# --------------------------------------------------------------------------
# Session gate calibration
#
# A session sets its gate→(n, D) calibration once and references it, instead
# of re-typing `n = (c_tg V_tg + c_bg V_bg)/e + n_offset` and `F = |n| h/4e`
# with scattered magic constants per cell (the 2026-06-16 QC0426 session
# re-derived n ~18× and F ~11× inline). The physical constants come from
# scipy so 6.626e-34 / 1.602e-19 / 8.854e-12 live in one audited place; the
# per-session calibration numbers (capacitances, CNP offset) are inputs the
# session constructs — no device's CNP is baked into the library (blinded runs
# deliberately keep CNP out of the device card).
# --------------------------------------------------------------------------

_E = constants.e              # elementary charge, C
_H = constants.h             # Planck constant, J·s
_EPSILON_0 = constants.epsilon_0  # vacuum permittivity, F/m


@dataclass(frozen=True)
class GateCalibration:
    """Per-session gate→(n, D) calibration for a dual-gated device.

    Construct **once** per session from the live-calibrated values, then call
    `density` / `displacement_field` / `n_D` per cell. Conventions match the
    session ana notebooks (`calc_nD`) and the device card, all SI:

        n = (c_tg·V_tg + c_bg·V_bg) / e   + n_offset      [m^-2]
        D = (c_tg·V_tg − c_bg·V_bg) / (2·ε₀) + D_offset   [V/m]

    Capacitances are per-area (F/m²), voltages in V, `n_offset` in m^-2,
    `D_offset` in V/m. The capacitance ratio/scale and offsets are
    per-session and established live — that's why they're inputs, not library
    constants. (For the conventional ×10¹² cm^-2 display unit, scale n by
    1e-16.)
    """

    c_tg: float            # top-gate capacitance per area, F/m²
    c_bg: float            # back-gate capacitance per area, F/m²
    n_offset: float = 0.0  # charge-neutrality density offset, m^-2
    D_offset: float = 0.0  # displacement-field offset, V/m

    def density(self, V_tg: Any, V_bg: Any) -> np.ndarray:
        """Carrier density n(V_tg, V_bg) in m^-2 (SI). Scalars or arrays."""
        V_tg = np.asarray(V_tg, dtype=float)
        V_bg = np.asarray(V_bg, dtype=float)
        return (self.c_tg * V_tg + self.c_bg * V_bg) / _E + self.n_offset

    def displacement_field(self, V_tg: Any, V_bg: Any) -> np.ndarray:
        """Displacement field D(V_tg, V_bg) in V/m (SI). Scalars or arrays."""
        V_tg = np.asarray(V_tg, dtype=float)
        V_bg = np.asarray(V_bg, dtype=float)
        return (self.c_tg * V_tg - self.c_bg * V_bg) / (2.0 * _EPSILON_0) + self.D_offset

    def n_D(self, V_tg: Any, V_bg: Any) -> tuple[np.ndarray, np.ndarray]:
        """Both `(n, D)` at once — the per-cell pair. `(m^-2, V/m)`."""
        return self.density(V_tg, V_bg), self.displacement_field(V_tg, V_bg)

    @classmethod
    def from_thicknesses(
        cls,
        t_tg: float,
        t_bg: float,
        t_bgSiO2: float = 0.0,
        *,
        n_offset: float = 0.0,
        D_offset: float = 0.0,
        kappa_hBN: float = 3.0,
        kappa_SiO2: float = 3.9,
    ) -> "GateCalibration":
        """Build from the gate-stack geometry instead of areal capacitances.

        Areal capacitances from the dielectric thicknesses (all SI, metres):

            c_tg = ε₀·κ_hBN / t_tg
            c_bg = ε₀ / (t_bg/κ_hBN + t_bgSiO2/κ_SiO2)

        `t_bgSiO2 = 0` for a metal/graphite back gate (no SiO2 term). The
        thicknesses are a geometry *prior* — calibrate `n_offset`/`D_offset`
        (and re-check the lever arm) against `cnp-and-dline-calibration`
        before trusting derived scales.
        """
        c_tg = _EPSILON_0 * kappa_hBN / t_tg
        c_bg = _EPSILON_0 / (t_bg / kappa_hBN + t_bgSiO2 / kappa_SiO2)
        return cls(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset, D_offset=D_offset)


def luttinger_frequency(n: Any) -> np.ndarray:
    """Full-density Onsager (SdH) frequency `F = |n|·h / (4·e)`, in Tesla.

    A single Fermi surface carrying the full density `n` gives this SdH
    frequency; the 4 is the spin×valley (4-fold) Landau degeneracy. `n` is in
    m^-2 (SI — feed `GateCalibration.density` output directly). Returns `|n|`
    form: the SdH frequency is positive for either carrier sign.
    """
    return np.abs(np.asarray(n, dtype=float)) * _H / (4.0 * _E)
