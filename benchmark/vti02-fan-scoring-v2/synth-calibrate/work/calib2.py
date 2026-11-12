"""Stage-2: add the low-filling enhancement h(nu); start from fit1."""
import sys, json, numpy as np
from scipy.optimize import least_squares
import calib
f1 = json.load(open('fit1.json'))['params']
calib.BASE.update({k: v for k, v in f1.items() if k in calib.BASE})
calib.FREE = [(k, f1.get(k, lo_), lo, hi) for k, lo_, lo, hi in calib.FREE] + [('hq_a', 3.0, 0.0, 20.0), ('hq_nu', 3.0, 1.5, 6.0), ('hq_w', 0.25, 0.05, 1.5)]
x0 = np.array([f[1] for f in calib.FREE]); lb = [f[2] for f in calib.FREE]; ub = [f[3] for f in calib.FREE]
print('cost0', 0.5 * (calib.resid(x0) ** 2).sum(), flush=True)
sol = least_squares(calib.resid, x0, bounds=(lb, ub), x_scale='jac', diff_step=1e-3, max_nfev=40, verbose=2)
p = calib.unpack(sol.x)
print(json.dumps({k: p[k] for k, *_ in calib.FREE}, indent=1))
json.dump(dict(x=sol.x.tolist(), names=[f[0] for f in calib.FREE], cost=sol.cost, params=p), open('fit2.json', 'w'), indent=1)
