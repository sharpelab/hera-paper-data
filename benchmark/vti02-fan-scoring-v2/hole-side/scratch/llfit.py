import numpy as np, sys
from scipy.signal import argrelextrema
from scipy.ndimage import uniform_filter1d
for s, bwin in (('0823', (1.0, 4.5)), ('0824', (0.9, 4.5))):
    d = np.load(f'scratch/fan{s}.npz'); n, R, B = d['n'], d['R'], d['B']
    mins = []
    for i in range(n.shape[0]):
        b = np.median(B[i])
        if not bwin[0] <= b <= bwin[1]: continue
        x = n[i]; y = np.log(np.clip(np.abs(R[i]), 5, None)); o = np.argsort(x); x, y = x[o], y[o]
        yb = y - uniform_filter1d(y, 9 if s == '0823' else 5, mode='nearest')
        j = argrelextrema(yb, np.less, order=2)[0]
        for jj in j:
            mins.append((x[jj], B[i][o][jj], -yb[jj]))
    mins = np.array(mins)
    for side, sel in (('h', mins[:, 0] < -0.25), ('e', mins[:, 0] > 0.25)):
        m = mins[sel]
        best = (-1e9,)
        grid = []
        for sc in np.arange(0.70, 1.10, 0.0025):
            for n0 in np.arange(-0.25, 0.25, 0.005):
                nu = sc * (m[:, 0] - n0) * 41.357 / m[:, 1]
                v = np.mean(np.cos(2 * np.pi * nu / 4))
                grid.append((v, sc, n0))
        grid.sort(reverse=True)
        print(s, side, 'minima', len(m), 'best (score, s, n0):', [tuple(np.round(g, 3)) for g in grid[:5]])
