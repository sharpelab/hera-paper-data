"""Quadrature noise vs B for every run with B != 0 (2D: fast+slow d2 of leak-removed Y; 1D B sweeps: d2 along the sweep), |R| < 300 ohm stencils."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.ndimage import maximum_filter
inv = json.load(open('inventory_raw.json'))
Be = [0, 0.1, 1, 1.6, 2.5, 4, 6, 8, 11]
out = {}
for r in inv:
    rng = r.get('rng_magnet_field')
    if not rng or rng[1] < 1 or (r.get('npts') or 0) < 60: continue
    day, run = r['day'], r['run']
    d = loadrun(day, run); X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    t = d['t']; B = d['B']
    if d['nrows'] == 1:   # 1D: along the sweep
        Bv = B[0]; y = Yc[0]; dtp = np.nanmedian(np.diff(t[0]))
        v = np.full(y.size, np.nan); v[1:-1] = d2(y) / np.sqrt(6) * corr_d2(dtp, d['tau'])
        Rm = maximum_filter(np.abs(R[0]), 3, mode='nearest'); V = [(Bv, v, Rm)]
    else:
        dtp = np.nanmedian(np.diff(t, axis=1))
        F = np.full(X.shape, np.nan); S = np.full(X.shape, np.nan)
        if d['nfast'] > 6: F[:, 1:-1] = d2(Yc, 1) / np.sqrt(6) * corr_d2(dtp, d['tau'])
        S[1:-1] = d2(Yc, 0) / np.sqrt(6)
        Rf = maximum_filter(np.abs(R), size=(1, 3), mode='nearest'); Rs = maximum_filter(np.abs(R), size=(3, 1), mode='nearest')
        V = [(B, F, Rf), (B, S, Rs)]
    res = []
    for lo, hi in zip(Be[:-1], Be[1:]):
        vv = np.concatenate([v[(b >= lo) & (b < hi) & (rm < 300)] for b, v, rm in V]); vv = vv[np.isfinite(vv)]
        res.append(round(float(to_density(rob(vv), d['tau'], d['slope']) * 1e9), 1) if vv.size >= 15 else None)
    Tm = np.nanmedian(d['T']) if d['T'] is not None else np.nan
    key = f'{day}-r{run}'
    out[key] = dict(tau=d['tau'], I=I, T=float(Tm), dt=float(dtp), res=res, type=r['type'], start=r['start'])
    print(f"{key:7s} tau {d['tau']:.2f} T {Tm:6.2f}K dt {dtp:5.2f}s {r['type']}: " + ' '.join(f"[{lo},{hi}):{'-' if x is None else f'{x:.0f}'}" for (lo, hi), x in zip(zip(Be[:-1], Be[1:]), res)))
json.dump(dict(edges=Be, runs=out), open('bdep.json', 'w'), indent=1)
