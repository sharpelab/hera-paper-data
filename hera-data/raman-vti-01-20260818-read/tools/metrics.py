#!/usr/bin/env python3
"""
2D-band (and G-band) metrics for graphene stacking reads.

All 2D metrics are computed about the *fitted* 2D center, never absolute
wavenumber windows: the 2D band disperses ~100 cm^-1/eV with excitation
energy, so absolute windows calibrated at one wavelength do not transfer.

Metrics (per spectrum):
  fwhm      single-Lorentzian FWHM of the whole 2D band -- the workhorse
            map metric (Lui et al. 2011). ABC broader than ABA.
  skew      intensity-weighted third moment in center +/- HALF cm^-1.
            ABC's asymmetric shoulder gives it a sign; direction is
            established empirically by validate.py, not assumed.
  ratio_lh  integrated low-side / high-side intensity about the center
            (center-relative version of the Yang et al. 2019 window ratio).
  center    fitted 2D peak position (cm^-1).
  r2        Lorentzian fit quality; low r2 = structured band (multi-peak /
            mixed spectrum), itself information.

No external deps beyond numpy/scipy.
"""
import numpy as np
from scipy.optimize import curve_fit

TWO_D_SEARCH = (2550.0, 2850.0)  # 2D peak search window, generous across 1.9-2.8 eV
FIT_HALF = 150.0                 # Lorentzian fit half-window about the peak
HALF = 100.0                     # moment/ratio half-window
G_SEARCH = (1500.0, 1650.0)


def _lorentz(x, a, x0, w, c):
    return a * (w / 2) ** 2 / ((x - x0) ** 2 + (w / 2) ** 2) + c


def _clip(wn, ii, lo, hi):
    m = (wn >= lo) & (wn <= hi)
    return wn[m], ii[m]


def fit_band(wn, ii, search, fit_half=FIT_HALF):
    """Single Lorentzian + const in a window about the band maximum.

    Returns dict(center, fwhm, amp, offset, r2) or None if the band is
    absent / fit fails.
    """
    w, i = _clip(wn, ii, *search)
    f = np.isfinite(i)
    w, i = w[f], i[f]          # partial maps carry all-NaN columns
    if len(w) < 10:
        return None
    x0 = w[np.argmax(i)]
    w, i = _clip(wn, ii, x0 - fit_half, x0 + fit_half)
    if len(w) < 10:
        return None
    base = np.median(np.concatenate([i[:5], i[-5:]]))
    amp0 = i.max() - base
    if amp0 <= 0:
        return None
    try:
        p, _ = curve_fit(_lorentz, w, i, p0=[amp0, x0, 40.0, base],
                         maxfev=5000)
    except RuntimeError:
        return None
    a, x0f, fw, c = p
    fw = abs(fw)
    resid = i - _lorentz(w, *p)
    ss_tot = np.sum((i - i.mean()) ** 2)
    r2 = 1 - np.sum(resid ** 2) / ss_tot if ss_tot > 0 else 0.0
    if not (search[0] - 50 < x0f < search[1] + 50) or fw > 400:
        return None
    return dict(center=x0f, fwhm=fw, amp=a, offset=c, r2=r2)


def metrics_2d(wn, ii):
    """2D-band metric set for one spectrum, or None if no usable 2D band."""
    fit = fit_band(wn, ii, TWO_D_SEARCH)
    if fit is None or fit["amp"] <= 0:
        return None
    c = fit["center"]
    w, i = _clip(wn, ii, c - HALF, c + HALF)
    if len(w) < 10:
        return None
    i = i - fit["offset"]
    i = np.clip(i, 0, None)
    tot = np.trapezoid(i, w)
    if tot <= 0:
        return None
    mu = np.trapezoid(i * w, w) / tot
    var = np.trapezoid(i * (w - mu) ** 2, w) / tot
    skew = (np.trapezoid(i * (w - mu) ** 3, w) / tot) / var ** 1.5 if var > 0 else 0.0
    lo_m = (w >= c - HALF) & (w <= c - 10)
    hi_m = (w >= c + 10) & (w <= c + HALF)
    lo = np.trapezoid(i[lo_m], w[lo_m]) if lo_m.sum() > 1 else 0.0
    hi = np.trapezoid(i[hi_m], w[hi_m]) if hi_m.sum() > 1 else 0.0
    ratio = lo / hi if hi > 0 else np.inf
    return dict(center=fit["center"], fwhm=fit["fwhm"], amp=fit["amp"],
                r2=fit["r2"], skew=skew, ratio_lh=ratio)


def decompose_mixed(wn, spec, ref_a, ref_b, window=(2550.0, 2850.0)):
    """Fit spec ≈ α·ref_a + (1−α)·ref_b (all on the same wavenumber grid,
    area-normalized in `window`). The references should be same-instrument,
    same-wavelength population means (e.g. a map's own cluster means).

    Returns dict(alpha, r2): alpha = weight of ref_a, clipped to [0, 1];
    r2 = fit quality (low r2 → the spectrum is not a two-component mixture
    of these references). None if the window is empty or a ref is degenerate.
    """
    m = (wn >= window[0]) & (wn <= window[1])
    if m.sum() < 20:
        return None

    def norm(y):
        yy = np.clip(y[m], 0, None)
        a = np.trapezoid(yy, wn[m])
        return yy / a if a > 0 else None

    s, a, b = norm(spec), norm(ref_a), norm(ref_b)
    if s is None or a is None or b is None:
        return None
    d = a - b
    denom = float(d @ d)
    if denom <= 0:
        return None
    alpha = float(np.clip((s - b) @ d / denom, 0.0, 1.0))
    fit = alpha * a + (1 - alpha) * b
    ss_tot = float(((s - s.mean()) ** 2).sum())
    r2 = 1 - float(((s - fit) ** 2).sum()) / ss_tot if ss_tot > 0 else 0.0
    return dict(alpha=alpha, r2=r2)


def metrics_g(wn, ii):
    """G-band position/FWHM (needs the spectrum to cover ~1500-1650)."""
    if wn.min() > G_SEARCH[0]:
        return None
    fit = fit_band(wn, ii, G_SEARCH, fit_half=60.0)
    if fit is None:
        return None
    return dict(center=fit["center"], fwhm=fit["fwhm"], r2=fit["r2"])
