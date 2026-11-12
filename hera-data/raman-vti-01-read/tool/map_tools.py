#!/usr/bin/env python3
"""
Hyperspectral-map tools: per-pixel 2D metrics + two-population segmentation.

Segmentation is *relative* (two populations within one map), never an
absolute FWHM threshold: absolute thresholds fold in instrument resolution
and excitation wavelength and do not transfer between setups. Layer-number
steps also shift 2D FWHM, so a two-population split on a multi-thickness
flake is a first pass, not a verdict -- interpret clusters against the
flake's thickness map.

No external deps beyond numpy/scipy (matplotlib only for save_maps).
"""
import numpy as np

from metrics import metrics_2d

METRIC_KEYS = ("center", "fwhm", "amp", "r2", "skew", "ratio_lh")


def per_pixel_metrics(wn, ii, min_amp_snr=8.0):
    """Metric arrays over map columns; NaN where no credible 2D band.

    min_amp_snr: peak amplitude must exceed this multiple of the per-pixel
    noise floor (median |diff|) -- excludes substrate / dead pixels.
    """
    n = ii.shape[1]
    out = {k: np.full(n, np.nan) for k in METRIC_KEYS}
    for j in range(n):
        y = ii[:, j]
        noise = np.median(np.abs(np.diff(y))) + 1e-12
        m = metrics_2d(wn, y)
        if m is None or m["amp"] < min_amp_snr * noise:
            continue
        if not (15.0 < m["fwhm"] < 200.0) or m["r2"] < 0.4:
            continue  # spike/junk fit, not a graphene 2D band
        for k in METRIC_KEYS:
            out[k][j] = m[k]
    return out


def two_population_split(values, n_iter=50):
    """1-D 2-means. Returns (labels 0/1 with 1 = higher-mean cluster, centers).

    NaNs stay unlabeled (-1).
    """
    v = np.asarray(values, float)
    ok = np.isfinite(v)
    labels = np.full(v.shape, -1, int)
    if ok.sum() < 4:
        return labels, (np.nan, np.nan)
    lo, hi = np.percentile(v[ok], [10, 90])
    c = np.array([lo, hi], float)
    for _ in range(n_iter):
        d = np.abs(v[ok, None] - c[None, :])
        lab = d.argmin(axis=1)
        new = np.array([v[ok][lab == k].mean() if (lab == k).any() else c[k]
                        for k in (0, 1)])
        if np.allclose(new, c):
            break
        c = new
    if c[0] > c[1]:
        c = c[::-1]
        lab = 1 - lab
    labels[ok] = lab
    return labels, tuple(c)


def to_image(vec, size_x, size_y):
    """Map-column vector -> (size_y, size_x) image (row-major x-fastest)."""
    return np.asarray(vec).reshape(size_y, size_x)


def cluster_mean_spectrum(ii, labels, k):
    """Mean spectrum over map columns with label k."""
    sel = labels == k
    return ii[:, sel].mean(axis=1) if sel.any() else None
