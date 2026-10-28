"""0825 run 7 (tau 0.1) vs run 8 (tau 0.3), same 50 nA / sens 100 uV: quadrature (Y) and X noise along B."""
import numpy as np, sys
sys.path.insert(0, '.')
from load import load
from noise_q import sigma_d2, acf4
for run in (7, 8):
    d = load('0825-r8', run=run)
    X = d['g']('sr1_X'); Y = X * np.tan(np.deg2rad(d['g']('sr1_P'))); B = d['B']; tau = d['lk']['sr1']['time_constant']
    t = d['t']; dts = np.median(np.abs(np.diff(t[:, 0])))
    sel = (B >= 1.5) & (B <= 2.5)
    sy = np.median(sigma_d2(Y[sel].T)); sx = np.median(sigma_d2(X[sel].T))
    # fast-axis estimate too (run 8 only meaningful)
    fy = np.median(sigma_d2(Y[sel])) if X.shape[1] > 10 else np.nan
    print(f"run {run}: tau {tau} I {np.median(d['I'])*1e9:.1f} nA  rows in 1.5-2.5T {sel.sum()}  row dt {dts:.1f}s  sigma_Y(along B) {sy*1e9:.1f} nV  sigma_X(along B) {sx*1e9:.1f} nV  sigma_Y(fast) {fy*1e9:.1f} nV")
