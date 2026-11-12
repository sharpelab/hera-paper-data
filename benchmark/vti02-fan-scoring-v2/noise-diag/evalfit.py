"""Evaluate the fitted model2 (start f_b=0.3 result of fit2.py; Powell, 13 params) on fit and held-out runs; write fit2.json."""
import sys, json, numpy as np
sys.path.insert(0, '.')
import fit2 as F
import model2 as M
prm = dict(e_w=46.46, z0=9.79, z1=470.4, f_b=0.7122, w_b=0.2899, g=np.array([6.79, 42.45, 110.20, 56.97, 158.91, 124.18, 102.94, 54.36]))
alt = dict(e_w=43.35, z0=46.0, z1=487.2, f_b=0.7329, w_b=0.3002, g=np.array([24.48, 51.37, 85.65, 93.55, 139.14, 160.08, 78.69, 128.56]))
F.load_all(F.FIT + F.HOLD)
P = F.predict(prm, F.FIT + F.HOLD, seed=11, nrep=3)
def L(keys):
    v = [np.log(P[k][kk] / F.RUNS[k]['live'][kk]) for k in keys for kk in F.RUNS[k]['live'] if kk in P[k]]
    return float(np.mean(np.square(v))), float(np.mean(v)), len(v)
lf, lh = L(F.FIT), L(F.HOLD)
print('fit: msle %.3f bias %+.3f n %d | hold: msle %.3f bias %+.3f n %d' % (*lf, *lh))
json.dump(dict(prm={k: (v.tolist() if hasattr(v, 'tolist') else v) for k, v in prm.items()}, alt_start=alt and {k: (v.tolist() if hasattr(v, 'tolist') else v) for k, v in alt.items()},
               knots=M.KNOTS.tolist(), fit_msle=lf, hold_msle=lh, fit=F.FIT, hold=F.HOLD), open('fit2.json', 'w'), indent=1)
for k in F.FIT + F.HOLD:
    tag = 'FIT ' if k in F.FIT else 'HOLD'
    s = f"{tag} {k:7s} tau {F.RUNS[k]['d']['tau']}: "
    for kk in sorted(F.RUNS[k]['live']):
        if kk in P[k]: s += f"{kk[0][0]}{kk[1]:g}: {F.RUNS[k]['live'][kk]:.0f}/{P[k][kk]:.0f}  "
    print(s)
