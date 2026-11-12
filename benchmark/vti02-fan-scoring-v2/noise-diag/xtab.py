"""Cross-tab: quadrature noise (nV/rtHz, pooled fast+slow d2, robust) by B bin x local-gradient bin."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from within import prep
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (23, 6), (23, 7)]
Be = [0, 1.5, 2.5, 4, 6, 11]; Ge = [0, 3, 10, 30, 1e9]
for day, run in RUNS:
    d, p = prep(day, run); dens = p['dens']; B = p['B']
    # local gradient: max of |dR/dcol|, |dR/drow| in ohm per step
    G = np.maximum(np.abs(p['dXn']), np.abs(p['dXB'])) / d['I']
    ok = np.abs(p['R']) < 1500
    print(f"== {day}-r{run} tau {d['tau']} I {d['I']*1e9:.0f} nA   rows=B bins {Be}, cols=|grad R| (ohm/step) bins {Ge}")
    for lo, hi in zip(Be[:-1], Be[1:]):
        s = f'  B[{lo},{hi})'
        for glo, ghi in zip(Ge[:-1], Ge[1:]):
            m = ok & (B >= lo) & (B < hi) & (G >= glo) & (G < ghi)
            v = np.concatenate([p['F'][m], p['S'][m]]); v = v[np.isfinite(v)]
            s += f"  {dens(rob(v)):5.0f}(n{v.size:4d})" if v.size >= 30 else '      -      '
        print(s)
