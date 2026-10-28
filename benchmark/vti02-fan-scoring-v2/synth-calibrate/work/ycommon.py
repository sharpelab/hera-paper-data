import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
for nm in ('0825-r8', '0822-r8', '0821-r8', '0824-r4'):
    d = load(nm); B = d['B']; X = d['g']('sr1_X')
    Y = X * np.tan(np.deg2rad(d['g']('sr1_P'))) if 'sr1_P' in d['cols'] else d['g']('sr1_Y')
    sel = d['n'] > 0.5
    X = X[:, sel]; Y = Y[:, sel]
    a = np.sum(X * Y) / np.sum(X * X); Yc = Y - a * X
    o = np.argsort(d['t'][:, 0]); Yc = Yc[o]; Bo = B[o]
    lowB = Bo <= np.percentile(Bo, 60)
    Z = Yc[lowB]
    Z = Z - np.median(Z, axis=0)          # remove per-column offset
    rowmean = Z.mean(1); w = Z - rowmean[:, None]
    s_pt = 1.4826 * np.median(np.abs(np.diff(Z, axis=1))) / np.sqrt(2)     # within-row point noise
    s_row = rowmean.std(); exp_row = s_pt / np.sqrt(Z.shape[1])
    s_along = 1.4826 * np.median(np.abs(np.diff(w, axis=0))) / np.sqrt(2)   # along-B after removing row common mode
    rc = np.corrcoef(rowmean[:-1], rowmean[1:])[0, 1]
    print(f'{nm}: Y within-row sigma {s_pt*1e9:5.1f} nV | row-common rms {s_row*1e9:6.1f} nV (indep exp {exp_row*1e9:4.1f}), lag-1 corr {rc:+.2f} | along-B sigma after removing row-common {s_along*1e9:5.1f} nV')
