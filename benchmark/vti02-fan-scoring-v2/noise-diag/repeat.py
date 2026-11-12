"""Repeatability: 0825 r7 (tau 0.1) vs r8 (tau 0.3) at matched (Vtg, B), and 0824 r5 vs r4. Deterministic quadrature vs noise."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.interpolate import RegularGridInterpolator
def lk(day, run):
    d = loadrun(day, run); X, Y = d['sr1X'], d['sr1Y']
    R = X / d['I']; m = np.abs(R) < 400
    a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2)
    return d, X / d['I'], (Y - a * X) / d['I'], a
for (dA, rA), (dB, rB) in (((25, 7), (25, 8)), ((24, 5), (24, 4))):
    A, XA, YA, aA = lk(dA, rA); Bd, XB, YB, aB = lk(dB, rB)
    vB = Bd['Vtg'][0]; bB = Bd['B'][:, 0]
    o = np.argsort(bB); ov = np.argsort(vB)
    fX = RegularGridInterpolator((bB[o], vB[ov]), XB[o][:, ov], bounds_error=False)
    fY = RegularGridInterpolator((bB[o], vB[ov]), YB[o][:, ov], bounds_error=False)
    print(f'== {dA}-r{rA} (tau {A["tau"]}) vs {dB}-r{rB} (tau {Bd["tau"]}); B-col grid Vtg {vB.min():.3f}..{vB.max():.3f} step {np.median(np.abs(np.diff(vB))):.4f}')
    for j in range(A['nfast']):
        v = A['Vtg'][:, j]; b = A['B'][:, 0]
        pts = np.c_[b, v]
        xi = fX(pts); yi = fY(pts)
        ok = np.isfinite(xi)
        if ok.sum() < 20: print(f'  col {j} Vtg {v.mean():.3f}: no overlap'); continue
        xa, ya = XA[ok, j], YA[ok, j]; xi, yi = xi[ok], yi[ok]; bb = b[ok]
        cx = np.corrcoef(xa, xi)[0, 1]
        # detrend Y along B with a smooth poly then correlate the structure
        def hp(y): return y - np.polyval(np.polyfit(bb, y, 5), bb)
        cy = np.corrcoef(hp(ya), hp(yi))[0, 1]
        # d2 along B of each and of the difference, ohm
        s = lambda y: rob(d2(y, 0)) / np.sqrt(6)
        for lo, hi in ((1.5, 2.5), (2.5, 4), (4, 6.1)):
            m = (bb >= lo) & (bb < hi)
            if m.sum() < 15: continue
            print(f'  col {j} Vtg {v.mean():.3f} B[{lo},{hi}) n{m.sum()}: corr X {np.corrcoef(xa[m], xi[m])[0,1]:+.3f}  corr Y(hp) {np.corrcoef(hp(ya)[m], hp(yi)[m])[0,1]:+.2f} | '
                  f'd2-sigma ohm: Y_A {s(ya[m]):.2f} Y_B(interp) {s(yi[m]):.2f} Y_A-Y_B {s(ya[m]-yi[m]):.2f} | X_A {s(xa[m]):.2f} X_A-X_B {s(xa[m]-xi[m]):.2f}')
