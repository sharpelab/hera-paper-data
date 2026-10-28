"""Is the excess ∝ |X| (phase/multiplicative-quadrature noise) or ∝ B (additive)? Cross-tab B x |R| using local |X| averaged over the d2 stencil."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from within import prep
from scipy.ndimage import maximum_filter
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (25, 7), (23, 6), (23, 7), (24, 5)]
Be = [0, 1.6, 3, 5, 11]; Re = [0, 15, 40, 80, 150, 300, 1500]
for day, run in RUNS:
    d, p = prep(day, run); B = p['B']
    # max |R| over the 3-point stencils (fast and slow) so a d2 is labelled by its largest |R|
    Rf = maximum_filter(np.abs(p['R']), size=(1, 3), mode='nearest'); Rs = maximum_filter(np.abs(p['R']), size=(3, 1), mode='nearest')
    print(f"== {day}-r{run} tau {d['tau']} I {d['I']*1e9:.0f}nA: noise nV/rtHz; rows B, cols max|R| in stencil (ohm) {Re}")
    for lo, hi in zip(Be[:-1], Be[1:]):
        s = f'  B[{lo},{hi})'
        for a, b in zip(Re[:-1], Re[1:]):
            mf = (B >= lo) & (B < hi) & (Rf >= a) & (Rf < b); ms = (B >= lo) & (B < hi) & (Rs >= a) & (Rs < b)
            v = np.concatenate([p['F'][mf], p['S'][ms]]); v = v[np.isfinite(v)]
            s += f"  {p['dens'](rob(v)):5.0f}({v.size:4d})" if v.size >= 25 else '      -     '
        print(s)
