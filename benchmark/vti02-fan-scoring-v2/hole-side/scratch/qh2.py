import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from scipy.signal import argrelextrema, savgol_filter
tr = {t['id']: t for t in load_all(include_ramp=False)}
for k, blo in [('0822-r7', 4.5), ('0825-r7-c0', 3.5)]:
    t = tr[k]; B, R = t['B'], t['R']
    Rs = savgol_filter(R, 9, 2)
    i = argrelextrema(Rs, np.less, order=5)[0]; i = i[B[i] > blo]
    print(k, 'minima', np.round(B[i], 2).tolist())
    for F1 in np.arange(25, 50, 0.05):
        nu = F1 / B[i]; r = nu - np.round(nu)
        if np.sqrt(np.mean(r ** 2)) < 0.1:
            print(f'   F1 {F1:.2f} |n| {F1/41.357:.3f} nu {np.round(nu, 2).tolist()} rms {np.sqrt(np.mean(r**2)):.3f}')
