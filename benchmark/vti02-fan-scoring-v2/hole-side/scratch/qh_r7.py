import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from scipy.signal import argrelextrema, savgol_filter
tr = {t['id']: t for t in load_all(include_ramp=False)}
for k in ['0822-r7', '0824-r5-c0', '0825-r7-c0']:
    t = tr[k]; B, R = t['B'], t['R']
    Rs = savgol_filter(R, 7, 2) if B.size > 150 else R
    i = argrelextrema(Rs, np.less, order=4)[0]
    i = i[B[i] > 2.0]
    print(k, 'minima B:', np.round(B[i], 3).tolist(), 'R:', np.round(Rs[i], 0).tolist())
    u = 1 / B[i]
    # grid-search F1 (= n * 41.357 T) so that F1*u is closest to integers (weighted)
    best = []
    for F1 in np.arange(20, 60, 0.01):
        nu = F1 * u; r = nu - np.round(nu)
        best.append((np.sqrt(np.mean(r ** 2)), F1))
    best.sort()
    for rms, F1 in best[:1]:
        pass
    # local minima of rms vs F1
    arr = np.array(best); o = np.argsort(arr[:, 1]); arr = arr[o]
    loc = [j for j in range(1, len(arr) - 1) if arr[j, 0] < arr[j - 1, 0] and arr[j, 0] <= arr[j + 1, 0] and arr[j, 0] < 0.12]
    for j in sorted(loc, key=lambda j: arr[j, 0])[:6]:
        F1 = arr[j, 1]
        print(f'   F1 {F1:.2f} T -> |n| {F1 / 41.357:.3f}, F_L {F1 / 4:.2f}, rms frac {arr[j, 0]:.3f}, nu = {np.round(F1 * u, 2).tolist()}')
