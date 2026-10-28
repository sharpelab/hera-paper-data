"""Decompose the quadrature excess into (a) the 14.99 Hz line, using the drain-current channel sr0 as the in-situ reference
(the same interference current, measured with high SNR), and (b) everything else.
Per row: Yc and sr0 residual (z0 = sr0 - its run median) are both detrended (linear in column index); per B band,
Yc = a*Re(z0) + b*Im(z0) + e. Line share = var(fit)/var(Yc). Reported as nV/rtHz-equivalent (sigma / sqrt(ENBW))."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (25, 5), (25, 6), (25, 7), (24, 5), (23, 6), (23, 7), (21, 4), (22, 5), (23, 3), (24, 3), (25, 4),
        (21, 5), (21, 10), (21, 11), (21, 12), (21, 13), (21, 14), (21, 15), (22, 6), (22, 7), (22, 9), (22, 10)]
BANDS = [(-0.1, 0.2), (0.2, 1.5), (1.5, 2.5), (2.5, 4), (4, 6), (6, 8), (8, 11)]
out = {}
for day, run in RUNS:
    d = loadrun(day, run); gain = abs(d['meta']['measurement_config']['sr0_gain'])
    X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    z0 = (d['sr0X'] + 1j * d['sr0Y']); z0 = z0 - np.median(z0.real) - 1j * np.median(z0.imag)
    B = d['B'] if d['B'] is not None else np.zeros_like(X)
    e = np.sqrt(5 / 64 / d['tau'])
    if d['nrows'] == 1:
        # 1D: detrend with a running median along the sweep (static quadrature pattern varies with B)
        from scipy.ndimage import median_filter
        det = lambda v: v - median_filter(v, 7, mode='nearest')
        o = np.argsort(d['t'][0])
        Yd = det(Yc[0][o]); Rd = det(z0[0][o].real); Id = det(z0[0][o].imag); Bb = B[0][o]; Rr = R[0][o]
    else:
        k = np.arange(d['nfast']); V = np.c_[np.ones_like(k), k].astype(float); P = V @ np.linalg.pinv(V)
        det = lambda M: M - M @ P.T
        Yd, Rd, Id, Bb, Rr = det(Yc).ravel(), det(z0.real).ravel(), det(z0.imag).ravel(), B.ravel(), R.ravel()
    res = {}
    s = f"{day}-r{run:<2d} tau {d['tau']} f0dt%1 {(1.21628*np.nanmedian(np.diff(d['t'],axis=1)) )%1 if d['nfast']>1 else np.nan:.2f}: "
    for lo, hi in BANDS:
        mm = (Bb >= lo) & (Bb < hi) & (np.abs(Rr) < 1500)
        if mm.sum() < 40: continue
        A = np.c_[Rd[mm], Id[mm]]; y = Yd[mm]
        c, *_ = np.linalg.lstsq(A, y, rcond=None); fit = A @ c
        vt = np.var(y); vf = np.var(fit); vr = np.var(y - fit)
        # bias of var(fit) under no line: ~ 2/N * vt
        vf_c = max(vf - 2 * vt / mm.sum(), 0)
        dof = 1.0  # detrending removes 2 of nfast dof per row: correct variance scale
        if d['nrows'] > 1: dof = d['nfast'] / (d['nfast'] - 2)
        Zt = np.hypot(*c) * gain   # V per (A of current in sr0) ~ ohm
        res[lo] = dict(tot=float(np.sqrt(vt * dof) / e * 1e9), line=float(np.sqrt(vf_c * dof) / e * 1e9), rest=float(np.sqrt(vr * dof) / e * 1e9), Zt=float(Zt), n=int(mm.sum()))
        s += f"B[{lo},{hi}) tot {res[lo]['tot']:4.0f} line {res[lo]['line']:4.0f} rest {res[lo]['rest']:4.0f} Zt {Zt:5.0f} ; "
    out[f'{day}-r{run}'] = dict(tau=d['tau'], bands=res)
    print(s)
json.dump(out, open('linedecomp.json', 'w'), indent=1)
