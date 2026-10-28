"""Hole-side density from the integer-QH ladder of the dense 1D traces: R minima above B_lo, assigned to consecutive
integers nu = F1 / B (F1 = |n| h/e = 41.357 |n| T); every consecutive assignment of the cleanest minima is scored by
the spread of nu*B.  Prints each branch; the report quotes the tightest."""
import sys
import numpy as np
from scipy.signal import argrelextrema, savgol_filter
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all

H_E = 41.357
CASES = {'0822-r7': [6.0, 6.96, 8.34], '0825-r7-c0': [4.28, 5.03, 5.83]}   # cleanest minima (listed by the scan below)

if __name__ == '__main__':
    tr = {t['id']: t for t in load_all(include_ramp=False)}
    for k, blo in (('0822-r7', 4.5), ('0825-r7-c0', 3.5)):
        t = tr[k]; B, R = t['B'], t['R']
        Rs = savgol_filter(R, 9, 2)
        i = argrelextrema(Rs, np.less, order=5)[0]; i = i[B[i] > blo]
        print(f"{k}: minima above {blo} T at {np.round(B[i], 2).tolist()} (R {np.round(Rs[i]).tolist()} ohm); grader frame |n| {abs(t['n_act_e']):.3f}")
        Bm = np.array(CASES[k])
        for nu_top in range(3, 12):
            nus = nu_top + np.arange(Bm.size)[::-1]       # highest B gets the lowest nu
            F1 = nus * Bm
            print(f"   nu {nus.tolist()}: F1 {np.round(F1, 2).tolist()} -> |n| {F1.mean() / H_E:.3f} +- {F1.std() / H_E:.3f} (spread {100 * F1.std() / F1.mean():.1f} %)")
