import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
for nm in ('0825-r8', '0822-r8', '0821-r8', '0824-r4'):
    d = load(nm); B = d['B']; X = d['g']('sr1_X')
    Y = X * np.tan(np.deg2rad(d['g']('sr1_P'))) if 'sr1_P' in d['cols'] else d['g']('sr1_Y')
    sel = d['n'] > 0.5; X = X[:, sel]; Y = Y[:, sel]
    a = np.sum(X * Y) / np.sum(X * X); Yc = Y - a * X
    o = np.argsort(B); Z = Yc[o]
    dz = np.diff(Z, axis=0) / np.sqrt(2)   # along B
    for lab, sl in (('lowB60%', slice(0, int(0.6 * len(B)))), ('all', slice(None))):
        v = dz[sl].ravel()
        rob = 1.4826 * np.median(np.abs(v - np.median(v))); rms = v.std()
        print(f'{nm} {lab}: along-B diff robust {rob*1e9:6.1f} nV  rms {rms*1e9:7.1f} nV  frac>5 robust {np.mean(np.abs(v) > 5 * rob):.4f}  kurt {np.mean(v**4)/np.mean(v**2)**2:.1f}')
    # X/|R| ratio: Y vs |X| relation: does Y noise grow with |X|?
    big = np.abs(X[o][1:]) ; q = np.quantile(big, [0, .5, .9, 1])
    for k in range(3):
        m = (big >= q[k]) & (big < q[k + 1])
        print(f'    |X| in [{q[k]*1e9:.0f},{q[k+1]*1e9:.0f}] nV: Y diff robust {1.4826*np.median(np.abs(dz[m]))*1e9:.1f} nV')
