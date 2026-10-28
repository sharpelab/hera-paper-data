"""Point-level cross-correlation of noise residuals (d2 along the time-ordered axis): sr1 X/Y vs sr0 X/Y. Common source?"""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
def rc(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    # robust: correlation of sign-preserving clipped values
    ca = np.clip(a / rob(a), -4, 4); cb = np.clip(b / rob(b), -4, 4)
    return np.corrcoef(ca, cb)[0, 1], ok.sum()
for day, run in ((21, 5), (21, 10), (21, 8), (22, 6), (22, 8), (24, 4), (25, 8), (25, 7), (23, 6), (21, 4), (25, 4), (23, 0)):
    d = loadrun(day, run)
    X1, Y1, X0, Y0 = d['sr1X'], d['sr1Y'], d['sr0X'], d['sr0Y']
    I = d['I']; m = np.abs(X1 / I) < 400; a = np.sum(X1[m] * Y1[m]) / np.sum(X1[m] ** 2); Y1c = Y1 - a * X1
    ph0 = np.median(np.arctan2(Y0, X0)); c0, s0 = np.cos(ph0), np.sin(ph0)
    I_par = X0 * c0 + Y0 * s0; I_perp = -X0 * s0 + Y0 * c0     # current along / across its own mean phase
    B = d['B'] if d['B'] is not None else np.zeros_like(X1)
    ax = 1 if d['nfast'] > 6 else 0
    if d['nrows'] == 1: ax = 1
    D = lambda z: d2(z, ax)
    Bm = B[:, 1:-1] if ax == 1 else B[1:-1]
    s = f'{day}-r{run:<2d} tau {d["tau"]}: '
    for lab, sel in (('B<1', Bm < 1), ('B>=3', Bm >= 3)):
        if sel.sum() < 30: continue
        r = [rc(D(u)[sel], D(v)[sel])[0] for u, v in ((Y1c, I_perp), (Y1c, I_par), (X1, I_par), (X1, I_perp), (Y1c, X1))]
        s += f"[{lab}] Y1-I⊥ {r[0]:+.2f} Y1-I∥ {r[1]:+.2f} X1-I∥ {r[2]:+.2f} X1-I⊥ {r[3]:+.2f} Y1-X1 {r[4]:+.2f} | "
    # sr0 noise level (pA/rtHz) and sr1 levels
    e = np.sqrt(5 / 64 / d['tau'])
    gi = 1e12 / 1e6 / e
    s += f"sr0 noise ∥/⊥ {rob(D(I_par))/np.sqrt(6)*gi:.1f}/{rob(D(I_perp))/np.sqrt(6)*gi:.1f} pA/rtHz"
    print(s)
