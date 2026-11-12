#!/usr/bin/env python3
"""s3_metrics.py — per-pixel band metrics + 2D-lineshape clustering for maps
003 and 005 (the two maps with real signal).

Per pixel: despike, linear baseline, then
  G (1500-1650): area, center, FWHM (Lorentzian fit)
  D (1300-1400): area
  2D (2550-2850): area, single-Lorentzian center/FWHM, centroid, skew
  Si 520: area (thickness proxy via attenuation)
Then k-means clustering of baseline-subtracted, area-normalized 2D lineshapes
over all graphene pixels of both maps.

Run: uv run --with numpy --with scipy --with matplotlib python s3_metrics.py
Outputs: metrics.npz, cluster_shapes.png, metric_maps.png, scatter.png
"""
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import medfilt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
EXC = float(d["exc_nm"])
KEYS = ["003", "005"]

def despike(spec):
    med = medfilt(spec, 5)
    bad = spec - med > 6 * np.sqrt(np.maximum(med, 1))
    out = spec.copy()
    out[bad] = med[bad]
    return out

def lorentz(x, a, x0, w, c):
    return a / (1 + ((x - x0) / (w / 2)) ** 2) + c

def fit_lorentz(x, y, x0g):
    a0 = max(y.max() - np.median(y), 1)
    p0 = [a0, x0g, 30.0, np.median(y)]
    try:
        r = least_squares(lambda p: lorentz(x, *p) - y, p0,
                          bounds=([0, x.min(), 5, -np.inf],
                                  [np.inf, x.max(), 400, np.inf]))
        return r.x, np.sqrt(np.mean(r.fun ** 2))
    except Exception:
        return [np.nan] * 4, np.nan

def band_metrics(rs, spec, lo, hi, blo, bhi, fit=False, x0g=None):
    """Linear baseline from flank medians; area, centroid; optional fit."""
    selb1 = (rs >= blo) & (rs < lo)
    selb2 = (rs > hi) & (rs <= bhi)
    sel = (rs >= lo) & (rs <= hi)
    x1, y1 = rs[selb1].mean(), np.median(spec[selb1])
    x2, y2 = rs[selb2].mean(), np.median(spec[selb2])
    slope = (y2 - y1) / (x2 - x1)
    base = y1 + slope * (rs - x1)
    y = spec - base
    x = rs[sel]; yb = y[sel]
    dx = np.abs(np.gradient(x))
    area = np.sum(yb * dx)
    centroid = np.sum(x * yb * dx) / area if area > 0 else np.nan
    out = dict(area=area, centroid=centroid)
    if fit:
        (a, x0, w, c), resid = fit_lorentz(x, yb, x0g or x[np.argmax(yb)])
        out.update(amp=a, center=x0, fwhm=w, resid=resid)
        # skew: third moment of positive part
        yp = np.clip(yb, 0, None)
        if yp.sum() > 0:
            mu = np.sum(x * yp * dx) / np.sum(yp * dx)
            var = np.sum((x - mu) ** 2 * yp * dx) / np.sum(yp * dx)
            out["skew"] = np.sum((x - mu) ** 3 * yp * dx) / np.sum(yp * dx) / var ** 1.5
        else:
            out["skew"] = np.nan
    return out, (x, yb)

results = {}
shapes_all, shape_meta = [], []
SHAPE_LO, SHAPE_HI = 2570, 2830

for k in KEYS:
    cube, lam = d[f"cube_{k}"], d[f"lam_{k}"]
    rs = 1e7 * (1 / EXC - 1 / lam)
    ny, nx, _ = cube.shape
    M = {m: np.full((ny, nx), np.nan) for m in
         ["G_area", "G_center", "G_fwhm", "D_area", "Si_area",
          "TD_area", "TD_center", "TD_fwhm", "TD_centroid", "TD_skew", "TD_resid"]}
    sel_shape = (rs >= SHAPE_LO) & (rs <= SHAPE_HI)
    for j in range(ny):
        for i in range(nx):
            spec = despike(cube[j, i])
            g, _ = band_metrics(rs, spec, 1500, 1650, 1420, 1720, fit=True, x0g=1582)
            dband, _ = band_metrics(rs, spec, 1300, 1400, 1220, 1470)
            si, _ = band_metrics(rs, spec, 495, 545, 420, 620)
            td, (xw, yw) = band_metrics(rs, spec, 2550, 2850, 2450, 2950,
                                        fit=True, x0g=2700)
            M["G_area"][j, i] = g["area"]; M["G_center"][j, i] = g["center"]
            M["G_fwhm"][j, i] = g["fwhm"]; M["D_area"][j, i] = dband["area"]
            M["Si_area"][j, i] = si["area"]
            M["TD_area"][j, i] = td["area"]; M["TD_center"][j, i] = td["center"]
            M["TD_fwhm"][j, i] = td["fwhm"]; M["TD_centroid"][j, i] = td["centroid"]
            M["TD_skew"][j, i] = td["skew"]; M["TD_resid"][j, i] = td["resid"]
    results[k] = M
    # collect normalized 2D shapes for clustering (graphene pixels only, chosen later)
    for j in range(ny):
        for i in range(nx):
            spec = despike(cube[j, i])
            # baseline for the shape window
            b1 = (rs >= 2450) & (rs < 2550); b2 = (rs > 2850) & (rs <= 2950)
            x1, y1 = rs[b1].mean(), np.median(spec[b1])
            x2, y2 = rs[b2].mean(), np.median(spec[b2])
            base = y1 + (y2 - y1) / (x2 - x1) * (rs - x1)
            y = (spec - base)[sel_shape]
            shapes_all.append(y)
            shape_meta.append((k, j, i))
    print(f"map {k}: metrics done")

rs003 = 1e7 * (1 / EXC - 1 / d["lam_003"])
shape_x = rs003[(rs003 >= SHAPE_LO) & (rs003 <= SHAPE_HI)]
shapes_all = np.array(shapes_all)
meta_k = np.array([m[0] for m in shape_meta])
meta_j = np.array([m[1] for m in shape_meta])
meta_i = np.array([m[2] for m in shape_meta])

np.savez_compressed(
    "metrics.npz",
    shape_x=shape_x, shapes=shapes_all.astype(np.float32),
    meta_k=meta_k, meta_j=meta_j, meta_i=meta_i,
    **{f"{k}_{m}": results[k][m] for k in KEYS for m in results[k]})
print("wrote metrics.npz")
