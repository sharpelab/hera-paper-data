"""Shared helpers for the vti-01 read scripts: load a map npz into the tool's
column layout, and plot a per-pixel vector in the stage µm frame."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tool"))
INT, FIG = HERE / "intermediates", HERE / "figures"


def load_map(k):
    """-> dict(wn, ii[n_wn, npx], nx, ny, X, Y, extent, meta, caption).
    Column j = ix * ny + iy (y-fastest) -> img[iy, ix] via vec.reshape(nx, ny).T"""
    z = np.load(INT / f"map_{k}.npz")
    cube = z["cube"].astype(float)
    nx, ny, nsp = cube.shape
    X, Y = z["X"], z["Y"]
    ii = cube.reshape(nx * ny, nsp).T
    ext = [X.min() - 0.5, X.max() + 0.5, Y.min() - 0.5, Y.max() + 0.5]
    return dict(wn=z["wn"], ii=ii, nx=nx, ny=ny, X=X, Y=Y, extent=ext,
                meta=json.loads(str(z["meta"])), caption=str(z["caption"]),
                y_up=bool(Y[0, -1] > Y[0, 0]), x_right=bool(X[-1, 0] > X[0, 0]))


def to_img(vec, m):
    """column vector -> image indexed [iy, ix] oriented so that imshow(origin='lower',
    extent=m['extent']) puts stage +x right and +y up."""
    img = np.asarray(vec).reshape(m["nx"], m["ny"]).T
    if not m["y_up"]:
        img = img[::-1, :]
    if not m["x_right"]:
        img = img[:, ::-1]
    return img


def show(ax, vec, m, **kw):
    return ax.imshow(to_img(vec, m), origin="lower", extent=m["extent"], **kw)


def pixel_xy(m):
    """stage (x, y) of every column, same ordering as ii columns."""
    return m["X"].reshape(-1), m["Y"].reshape(-1)


def band_area(wn, ii, lo, hi, base_pad=6):
    """Integrated counts above a linear baseline drawn between the window edges
    (median of base_pad px on each side). Spike-robust compared with a peak read."""
    sel = (wn >= lo) & (wn <= hi)
    w = wn[sel]
    y = ii[sel]
    b0 = np.median(y[:base_pad], axis=0)
    b1 = np.median(y[-base_pad:], axis=0)
    base = b0[None, :] + (b1 - b0)[None, :] * ((w - w[0]) / (w[-1] - w[0]))[:, None]
    return np.trapezoid(np.clip(y - base, 0, None), w, axis=0)
