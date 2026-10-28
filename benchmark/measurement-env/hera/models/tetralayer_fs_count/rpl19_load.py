#!/usr/bin/env python3
"""
Loader for the RPL_19 (rmg19) lab measurement format — the mirror's `data/<id>/`
folders (`metadata.json` + `data.tsv(.gz)`), which are byte-for-byte what the
paper repo's `sweep.sweep_load.pload` expects. This is a faithful, numpy-only
reimplementation of that loader plus the paper's `Lf_analysis.__init__`
Rxx / (n, D) construction, so `real_eval.py` does not depend on importing the
paper repo (which pins a hardcoded `../data/raw_sweeps` path).

Gate → (n, D) conversion is verbatim from the paper repo's `utils/utils.py`
`calculate_n_D`, using the `rmg19.json` calibration constants. Rxx per contact
is `sr830_{contact}_X / sr830_4_X` (sr830_4 is the current channel), exactly as
`Lf_analysis` does.
"""
import gzip
import json
from pathlib import Path

import numpy as np

# --- rmg19.json calibration (paper repo root) ---------------------------------
# The paper repo's Lf_analysis uses the "default" set; "experimental" (dtg=17.25)
# is what was used during acquisition and matches the RPL_19 device card exactly.
RMG19 = {
    "default":      dict(dtg=17.406, dbg=25.5, ep=3),
    "experimental": dict(dtg=17.25,  dbg=25.5, ep=3),
    "older_fit":    dict(dtg=17.15,  dbg=25.266, ep=3),
    "fft_fit":      dict(dtg=17.674504922712416, dbg=25.9, ep=3),
}
CAL = RMG19["default"]              # match Lf_analysis

MIRROR = Path("/home/zack/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/data")


def calculate_n_D(vtg, vbg, dtg=None, dbg=None, ep=None):
    """Verbatim from the paper repo utils.calculate_n_D. Returns
    (n [1e12 cm^-2], D [V/nm])."""
    dtg = CAL["dtg"] if dtg is None else dtg
    dbg = CAL["dbg"] if dbg is None else dbg
    ep = CAL["ep"] if ep is None else ep
    n = (np.asarray(vbg) / dbg + np.asarray(vtg) / dtg) * ep * 5.52634936
    D = 0.5 * ep * (np.asarray(vtg) / dtg - np.asarray(vbg) / dbg)
    return n, D


def _load_meta(fileid, root=MIRROR):
    return json.loads((Path(root) / str(fileid) / "metadata.json").read_text())


def _load_tsv(fileid, root=MIRROR):
    d = Path(root) / str(fileid)
    gz = d / "data.tsv.gz"
    if gz.exists():
        with gzip.open(gz, "rt") as f:
            return np.loadtxt(f)
    return np.loadtxt(d / "data.tsv")


def _col(meta, name):
    """Index of the first column named `name`."""
    return meta["columns"].index(name)


def load_fan(fileid, contact=2, root=MIRROR):
    """Load a 2D Landau fan (slow = magnet_field, fast = [k_tg_volt, k_bg_volt]).

    Returns a dict:
      B      : (nB,) field axis [T]
      Rxx    : (nB, ncol) resistance-proportional signal (V_x / I) per gate column
      n      : (ncol,) density per column [1e12 cm^-2]
      D      : (ncol,) displacement field per column [V/nm]
      contact, fileid, meta
    """
    meta = _load_meta(fileid, root)
    assert meta["type"] == "2D", f"{fileid} is not a 2D fan"
    dat = _load_tsv(fileid, root)

    field_axis = np.asarray(meta["slow_setpoints"][0], dtype=float)
    fast = np.asarray(meta["fast_setpoints"], dtype=float)      # (2, ncol)
    nB, ncol = field_axis.size, fast.shape[1]

    # row-major: for each slow (field) step, all fast (gate) points
    def reshape(colname):
        v = dat[:, _col(meta, colname)]
        # pad/truncate for interrupted sweeps
        full = nB * ncol
        if v.size < full:
            v = np.concatenate([v, np.full(full - v.size, np.nan)])
        return v[:full].reshape(nB, ncol)

    vx = reshape(f"sr830_{contact}_X")
    ii = reshape("sr830_4_X")
    with np.errstate(divide="ignore", invalid="ignore"):
        Rxx = vx / ii

    vtg, vbg = fast[0], fast[1]
    n, D = calculate_n_D(vtg, vbg)

    # true field from the data column (the setpoint axis is the request; the
    # measured magnet_field can differ slightly) — use the per-row mean.
    Bmeas = reshape("magnet_field")
    B = np.nanmean(Bmeas, axis=1)

    return dict(B=B, Rxx=Rxx, n=n, D=D, contact=contact, fileid=fileid, meta=meta)


def load_field_sweep(fileid, contact=2, root=MIRROR):
    """Load a 1D field sweep at fixed (n, D) (function 'sweep', param = field).

    Returns dict: B, Rxx (V_x/I), T [K] (mean of the sample-temperature column),
    T_all, fileid, meta.
    """
    meta = _load_meta(fileid, root)
    dat = _load_tsv(fileid, root)
    B = dat[:, _col(meta, "magnet_field")]
    vx = dat[:, _col(meta, f"sr830_{contact}_X")]
    ii = dat[:, _col(meta, "sr830_4_X")]
    with np.errstate(divide="ignore", invalid="ignore"):
        Rxx = vx / ii
    # temperature columns (some sweeps log two 'T' columns: probe + fridge)
    tcols = [k for k, c in enumerate(meta["columns"]) if c in ("T", "T_fridge", "T_probe")]
    T_all = {meta["columns"][k] + f"[{k}]": float(np.nanmean(dat[:, k])) for k in tcols}
    # the sample temperature is the one that tracks the heater — take the max-mean
    Tval = max(np.nanmean(dat[:, k]) for k in tcols) if tcols else np.nan
    return dict(B=B, Rxx=Rxx, T=float(Tval), T_all=T_all, fileid=fileid, meta=meta)


if __name__ == "__main__":
    f = load_fan(1840, contact=2)
    print(f"1840: B {f['B'].min():.2f}-{f['B'].max():.2f} T, "
          f"{f['B'].size} field pts x {f['n'].size} gate cols; "
          f"n {f['n'].min():.2f}..{f['n'].max():.2f}, D≈{np.median(f['D']):.2f}")
    s = load_field_sweep(1639, contact=2)
    print(f"1639: B {s['B'].min():.2f}-{s['B'].max():.2f} T, T={s['T']*1e3:.0f} mK, {s['T_all']}")
