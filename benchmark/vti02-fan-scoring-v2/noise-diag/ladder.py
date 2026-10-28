"""LK ladders (1D B sweeps at fixed n, T varied): quadrature noise vs local SdH amplitude of X, per B window."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.ndimage import uniform_filter1d
for day, runs in ((21, [5, 10, 11, 12, 13, 14, 15]), (22, [9, 10, 11, 12, 13, 14]), (22, [6, 7])):
    print(f'== 08-{day} ladder')
    for run in runs:
        d = loadrun(day, run); X, Y = d['sr1X'][0], d['sr1Y'][0]; I = d['I']; B = d['B'][0]; T = np.nanmedian(d['T'])
        o = np.argsort(B); o = o[B[o] >= 1.0]; X, Y, B = X[o], Y[o], B[o]
        R = X / I; m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = (Y - a * X)
        dtp = np.nanmedian(np.abs(np.diff(d['t'][0])))
        v = np.full(Y.size, np.nan); v[1:-1] = d2(Yc) / np.sqrt(6) * corr_d2(dtp, d['tau'])
        # SdH amplitude: X minus a running mean over ~0.4 T (in 1/B), rms over window
        u = 1 / B; Xs = np.polyval(np.polyfit(u, R, 6), u); osc = R - Xs
        s = f'  r{run:2d} T {T:5.1f}K tau {d["tau"]} Vtg {np.median(d["Vtg"]):.3f}: '
        for lo, hi in ((2, 3), (3, 4.5), (4.5, 6.5), (6.5, 10.1)):
            w = (B >= lo) & (B < hi)
            if w.sum() < 15: continue
            s += f"[{lo},{hi}) Y {to_density(rob(v[w]), d['tau'])*1e9:4.0f} nV/rtHz  oscRMS {np.std(osc[w]):6.1f} ohm  |dR/dB| {np.median(np.abs(np.gradient(R[w], B[w]))):6.0f} ohm/T ; "
        print(s)
