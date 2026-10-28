import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
for nm in ['0825-r8', '0822-r8', '0821-r8', '0824-r4']:
    d = load(nm); cols = d['cols']
    print(nm, [c for c in cols if c.startswith('sr1')])
    X = d['g']('sr1_X')
    if 'sr1_P' in cols:
        P = d['g']('sr1_P'); Y = X * np.tan(np.deg2rad(P))
    else:
        Y = d['g']('sr1_Y')
    sigv = {'0825-r8': 25e-9, '0822-r8': 22e-9, '0821-r8': 34e-9, '0824-r4': 37e-9}[nm]
    big = np.abs(X) > 30 * sigv
    ph = np.rad2deg(np.arctan2(Y, X))[big]
    ph = np.where(ph > 90, ph - 180, np.where(ph < -90, ph + 180, ph))
    print(f'  points |X|>30 sigma: {big.sum()}  phase median {np.median(ph):.2f} deg  robust std {1.4826*np.median(np.abs(ph-np.median(ph))):.2f} deg  (noise-only expectation ~{np.rad2deg(np.median(sigv/np.abs(X[big]))):.2f} deg)')
    # Y/X ratio at big points: row-to-row
    r = np.where(big, Y / X, np.nan)
    rm = np.nanmedian(r, 1)
    print('  row median Y/X: std over rows', np.nanstd(rm).round(4), ' first rows', np.round(rm[:6], 4))
