"""Fine-B profile in 1D B sweeps: sr1 quadrature noise, sr1 signal phase, sr0 (drain current) phase, |I| and sr0 noise."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
Be = np.arange(2.5, 10.01, 0.5)
for day, run in ((21, 5), (21, 10), (21, 12), (21, 15), (22, 6), (22, 7)):
    d = loadrun(day, run); B = d['B'][0]; o = np.argsort(B); o = o[B[o] > 2.4]; B = B[o]
    X, Y = d['sr1X'][0][o], d['sr1Y'][0][o]; x0, y0 = d['sr0X'][0][o], d['sr0Y'][0][o]
    I = d['I']; m = np.abs(X / I) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    dtp = np.nanmedian(np.abs(np.diff(d['t'][0]))); cf = corr_d2(dtp, d['tau']); e = np.sqrt(5 / 64 / d['tau'])
    vY = np.r_[np.nan, d2(Yc), np.nan] / np.sqrt(6) * cf / e * 1e9
    ph1 = np.rad2deg(np.arctan2(Y, X)); ph0 = np.rad2deg(np.arctan2(y0, x0)); ph0 = (ph0 + 180) % 360 - 180; ph0 = np.where(ph0 > 90, ph0 - 180, np.where(ph0 < -90, ph0 + 180, ph0))
    I0 = np.hypot(x0, y0); v0 = np.r_[np.nan, d2(I0), np.nan] / np.sqrt(6) * cf / e * 1e9 / 1e6 * 1e3   # pA/rtHz... (x0 in V at 1e6 V/A) -> nA; *1e3 -> pA
    print(f'== {day}-r{run} tau {d["tau"]} T {np.nanmedian(d["T"]):.1f}  n~Vtg {np.median(d["Vtg"]):.2f}')
    print('  B    Ynoise  phase1   phase0   |I|nA   I-noise(pA/rtHz)  R(ohm)')
    for lo, hi in zip(Be[:-1], Be[1:]):
        w = (B >= lo) & (B < hi)
        if w.sum() < 8: continue
        vv = vY[w]; vv = vv[np.isfinite(vv)]; w0 = v0[w]; w0 = w0[np.isfinite(w0)]
        print(f'  {lo:4.1f} {rob(vv):6.0f} {np.median(ph1[w]):+7.2f} {np.median(ph0[w]):+8.3f} {np.median(I0[w])/1e6*1e9:7.3f} {rob(w0):8.2f}  {np.median(X[w]/I):6.0f}')
