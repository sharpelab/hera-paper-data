"""Per-point table: quadrature d2 residual (V, filter-corrected, /sqrt6) with local predictors. Writes pts.npz for the regressions."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.ndimage import uniform_filter
inv = json.load(open('inventory_raw.json'))
DENS = {}   # density frame: n actual from load.FANS for fixtures; others only use B, Vtg
rows = []
for r in inv:
    rng = r.get('rng_magnet_field')
    if (r.get('npts') or 0) < 60: continue
    day, run = r['day'], r['run']
    d = loadrun(day, run)
    X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I; tau = d['tau']
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    t = d['t']; B = d['B'] if d['B'] is not None else np.zeros_like(X)
    T = d['T'] if d['T'] is not None else np.full_like(X, np.nan)
    Vtg = d['Vtg'] if d['Vtg'] is not None else np.zeros_like(X)
    ones = np.ones_like(X)
    recs = []
    if d['nrows'] == 1:
        o = np.argsort(B[0]); b = B[0][o]; x = R[0][o]; y = Yc[0][o]; dtp = np.nanmedian(np.abs(np.diff(t[0])))
        v = np.full(b.size, np.nan); v[1:-1] = d2(y) / np.sqrt(6) * corr_d2(dtp, tau)
        vx = np.full(b.size, np.nan); vx[1:-1] = d2(X[0][o]) / np.sqrt(6) * corr_d2(dtp, tau)
        gB = np.abs(np.gradient(uniform_filter(x, 5, mode='nearest'), b)) if np.ptp(b) > 0.5 else np.zeros_like(b)
        recs.append((v, vx, b, x, gB, np.zeros_like(b), T[0][o], Vtg[0][o], 0))
    else:
        dtp = np.nanmedian(np.diff(t, axis=1))
        ob = np.argsort(B[:, 0]); Bs = B[ob]; Rs = R[ob]
        if np.ptp(B) > 0.5 and d['nrows'] > 4:
            gB = np.abs(np.gradient(Rs, Bs[:, 0], axis=0))
            gBu = np.empty_like(gB); gBu[ob] = gB
        else: gBu = np.zeros_like(R)
        gn = np.abs(np.gradient(R, axis=1)) if d['nfast'] > 4 else np.zeros_like(R)   # ohm per column
        if d['nfast'] > 6:
            v = np.full(X.shape, np.nan); v[:, 1:-1] = d2(Yc, 1) / np.sqrt(6) * corr_d2(dtp, tau)
            vx = np.full(X.shape, np.nan); vx[:, 1:-1] = d2(X, 1) / np.sqrt(6) * corr_d2(dtp, tau)
            recs.append((v, vx, B, R, gBu, gn, T, Vtg, 0))
        if d['nrows'] > 6:
            v = np.full(X.shape, np.nan); v[1:-1] = d2(Yc, 0) / np.sqrt(6)
            vx = np.full(X.shape, np.nan); vx[1:-1] = d2(X, 0) / np.sqrt(6)
            recs.append((v, vx, B, R, gBu, gn, T, Vtg, 1))
    for v, vx, b, x, gb, gn, TT, vt, ax in recs:
        v = np.ravel(v); ok = np.isfinite(v)
        n = ok.sum()
        rows.append(np.c_[np.full(n, day), np.full(n, run), np.full(n, tau), np.full(n, I), np.full(n, d['sens']), np.full(n, ax),
                          v[ok], np.ravel(vx)[ok], np.ravel(b)[ok], np.ravel(x)[ok], np.ravel(gb)[ok], np.ravel(gn)[ok], np.ravel(TT)[ok], np.ravel(vt)[ok],
                          np.full(n, float(r['start']))])
A = np.vstack(rows)
cols = ['day', 'run', 'tau', 'I', 'sens', 'axis', 'dY', 'dX', 'B', 'R', 'gB', 'gn', 'T', 'Vtg', 'start']
np.savez_compressed('pts.npz', A=A, cols=np.array(cols))
print(A.shape)
