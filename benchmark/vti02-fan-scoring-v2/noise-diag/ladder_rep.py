"""Ladder runs share the B grid: is the quadrature 'noise' reproducible between adjacent-T runs (deterministic) or not (noise)?
Also regress Yc d2 on X d2 (signal-leak test) and on |dR/dB| (field-noise test)."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
def get(day, run):
    d = loadrun(day, run); X, Y = d['sr1X'][0], d['sr1Y'][0]; B = d['B'][0]; o = np.argsort(B); o = o[B[o] >= 2.3]
    X, Y, B = X[o], Y[o], B[o]; I = d['I']
    m = np.abs(X / I) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2)
    return d, B, X, Y - a * X, Y
for day, pairs in ((21, [(10, 11), (11, 12), (12, 13), (5, 10)]), (22, [(9, 10), (10, 11), (11, 12)])):
    for ra, rb in pairs:
        da, Ba, Xa, Ya, _ = get(day, ra); db, Bb, Xb, Yb, _ = get(day, rb)
        n = min(Ba.size, Bb.size)
        if np.abs(Ba[:n] - Bb[:n]).max() > 0.01:
            yb = np.interp(Ba, Bb, Yb); xb = np.interp(Ba, Bb, Xb)
        else:
            Ba, Xa, Ya = Ba[:n], Xa[:n], Ya[:n]; yb, xb = Yb[:n], Xb[:n]
        for lo, hi in ((2.4, 4.5), (4.5, 6.5), (6.5, 10.1)):
            w = (Ba >= lo) & (Ba < hi)
            if w.sum() < 20: continue
            ca = d2(Ya[w]); cb = d2(yb[w]); cx = d2(Xa[w]); cxb = d2(xb[w])
            print(f'08-{day} r{ra} vs r{rb} B[{lo},{hi}): corr d2Yc {np.corrcoef(ca, cb)[0,1]:+.2f}  corr d2X {np.corrcoef(cx, cxb)[0,1]:+.2f}  '
                  f'corr(d2Yc_a, d2X_a) {np.corrcoef(ca, cx)[0,1]:+.2f}  sigma d2Yc a/b {rob(ca)/np.sqrt(6)*1e9:.0f}/{rob(cb)/np.sqrt(6)*1e9:.0f} nV  sd(d2Yc_a - d2Yc_b)/sqrt2 {rob(ca-cb)/np.sqrt(12)*1e9:.0f}')
