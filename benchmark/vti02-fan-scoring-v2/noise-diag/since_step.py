"""Quadrature noise vs time since the row's field step (column index = elapsed time in the row)."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from within import prep
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (23, 6), (23, 7), (21, 4), (25, 4), (22, 5), (24, 3)]
for day, run in RUNS:
    d, p = prep(day, run); t = d['t']
    el = t - t[:, :1]            # s since the first point of the row
    B = d['B'][:, 0] if d['B'] is not None else np.zeros(d['nrows'])
    ok = np.abs(p['R']) < 1500
    print(f"== {day}-r{run} tau {d['tau']} dt {np.nanmedian(np.diff(t,axis=1)):.2f}s row pts {d['nfast']} (dir n {'up' if d['Vtg'][0,-1]>d['Vtg'][0,0] else 'down'}); gap between rows (s) {np.nanmedian(t[1:,0]-t[:-1,-1]):.1f}")
    nb = 6; edges = np.quantile(el[0], np.linspace(0, 1, nb + 1))
    for lo, hi in ((0, 1.6), (1.6, 3), (3, 6), (6, 11)) if d['B'] is not None else ((-1, 1),):
        rows = (B >= lo) & (B < hi)
        if rows.sum() < 4: continue
        s = f'   B[{lo},{hi}) rows {rows.sum():3d}: '
        for a, b in zip(edges[:-1], edges[1:]):
            m = rows[:, None] & (el >= a) & (el <= b) & ok
            v = np.concatenate([p['S'][m], p['F'][m]]); v = v[np.isfinite(v)]
            vs = p['S'][m]; vs = vs[np.isfinite(vs)]
            s += f" t{a:4.0f}-{b:3.0f}s: {p['dens'](rob(vs)) if vs.size>=15 else np.nan:5.0f}" 
        print(s)
