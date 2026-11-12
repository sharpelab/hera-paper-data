"""Shared spectral tools for the hole-side analysis (read-only on data).

spec(): Hann-windowed Fourier transform of R(1/B) over a B window, evaluated directly on the (possibly
non-uniform) 1/B samples with trapezoid weights, after a degree-`deg` polynomial-in-B background.  For a
uniform 1/B grid it equals the zero-padded FFT of fft_q1.col_fft.  Returns F, |S|, the white-noise
median |S| (from the record's first-difference noise), the resolution dF = 1/span and the worst-row Nyquist."""
import sys
import numpy as np

sys.path.insert(0, '/home/zack/sharpelab/measurement-env/hera/graders/fan-design')
FLN = 10.3392
_T = np.genfromtxt('/home/zack/sharpelab/measurement-env/hera/graders/fan-design/tones.csv', delimiter=',', names=True)


def model(n_abs, side='h', m='Halder_ABAB'):
    """(F_light, F_heavy, F_L) at |n| (actual, 1e12 cm^-2) for the given side; NaN off the table."""
    sel = _T['n'] < 0 if side == 'h' else _T['n'] > 0
    na = np.abs(_T['n'][sel]); fl = _T['F_light_' + m.replace('.', '')][sel]
    o = np.argsort(na); na, fl = na[o], fl[o]
    n_abs = np.asarray(n_abs, float)
    f = np.interp(n_abs, na, fl, left=np.nan, right=np.nan)
    return f, FLN * n_abs - f, FLN * n_abs


def noise_sigma(B, y):
    """Per-point white noise of a detrended record: MAD of first differences, min of low-B third and global."""
    d = np.diff(y[np.argsort(B)])
    mads = [1.4826 * np.median(np.abs(a - np.median(a))) for a in (d[: max(8, d.size // 3)], d) if a.size >= 8]
    return min(mads) / np.sqrt(2) if mads else np.nan


def detrend(B, R, lo, hi, deg):
    s = (B >= lo - 1e-9) & (B <= hi + 1e-9) & np.isfinite(R)
    b, y = B[s], R[s]
    if b.size < max(8, deg + 3):
        return None, None
    y = y - np.polyval(np.polyfit(b, y, deg), b)
    return b, y - y.mean()


def spec(B, R, lo, hi, deg=5, F=None, Fmax=40.0, dFgrid=0.01):
    b, y = detrend(B, R, lo, hi, deg)
    if b is None:
        return None
    u = 1 / b; o = np.argsort(u); u, y = u[o], y[o]
    u, iu = np.unique(u, return_index=True); y = y[iu]
    span = u[-1] - u[0]
    x = (u - u[0]) / span
    w = 0.5 - 0.5 * np.cos(2 * np.pi * x)                       # Hann in 1/B
    du = np.gradient(u)                                            # trapezoid-ish weights
    F = np.arange(0.0, Fmax + dFgrid, dFgrid) if F is None else F
    E = np.exp(-2j * np.pi * np.outer(F, u))
    S = np.abs(E @ (y * w * du))
    sig = noise_sigma(b, y[np.argsort(o)] if False else y)       # y is sorted by u; differences are neighbours either way
    sc = sig * np.sqrt(np.sum((w * du) ** 2) / 2)                 # complex-Gaussian scale of |S| for white noise
    med_noise = sc * np.sqrt(2 * np.log(2))                       # Rayleigh median
    nyq = 0.5 / np.max(np.diff(u))                                # worst row interval
    amp = 2 * S / np.sum(w * du)                                  # sinusoid amplitude estimate, ohm
    return dict(F=F, S=S, amp=amp, med_noise=med_noise, sigma=sig, dF=1 / span, nyq=nyq, rows=u.size,
                lo=float(1 / u[-1]), hi=float(1 / u[0]), span=span)


def peaks(F, Z, fmin=0.0, fmax=np.inf, thr=0.0, top=12):
    k = np.where((F >= fmin) & (F <= fmax))[0]
    k = k[(k > 0) & (k < F.size - 1)]
    k = [i for i in k if Z[i] >= Z[i - 1] and Z[i] >= Z[i + 1] and Z[i] >= thr]
    k = sorted(k, key=lambda i: -Z[i])[:top]
    return sorted((float(F[i]), float(Z[i])) for i in k)


def band_peak(F, Z, a, b):
    p = peaks(F, Z, a, b, top=1)
    return p[0] if p else (np.nan, 0.0)
