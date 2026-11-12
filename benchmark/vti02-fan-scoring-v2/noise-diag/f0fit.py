"""Refine the interference line frequency on sr0 with a coherent complex-sinusoid fit using raw timestamps (no detrend beyond per-segment linear)."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
for day, run in ((23, 4), (23, 1), (23, 3), (21, 3), (21, 1), (23, 9), (25, 2), (24, 0), (22, 3), (21, 12)):
    d = loadrun(day, run)
    t = d['t'].ravel(); z = (d['sr0X'] + 1j * d['sr0Y']).ravel()
    o = np.argsort(t); t = t[o]; z = z[o]
    # remove slow trend with a running median over ~20 s
    from scipy.ndimage import median_filter
    w = max(5, int(20 / np.median(np.diff(t))) | 1)
    zr = z - (median_filter(z.real, w, mode='nearest') + 1j * median_filter(z.imag, w, mode='nearest'))
    tt = t - t[0]
    f = np.arange(1.19, 1.25, 0.00002)
    P = np.abs(np.exp(-2j * np.pi * f[:, None] * tt[None, :]) @ zr) / zr.size
    k = np.argmax(P); fm = np.arange(-1.25, -1.19, 0.00002); Pm = np.abs(np.exp(-2j * np.pi * fm[:, None] * tt[None, :]) @ zr) / zr.size
    tau = d['tau']; H = 1 / (1 + (2 * np.pi * f[k] * tau) ** 2) ** 2
    print(f"{day}-r{run:<2d} tau {tau} dt {np.median(np.diff(tt)):.3f} T_span {tt[-1]:.0f}s  f0 {f[k]:.5f} Hz  amp {P[k]*1e6:.2f} uV(sr0 V)= {P[k]*1e6/1e6*1e12:.1f} pA  mirror max {Pm.max()*1e6:.2f}  | amp/H(f0,tau) {P[k]/H*1e12/1e6:.0f} pA at input")
