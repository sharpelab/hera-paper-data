"""Stage-4: Nelder-Mead on the moment objective (robust log ratios)."""
import sys, json, copy
import numpy as np
from scipy.optimize import minimize
import stats
p0 = json.load(open(sys.argv[1])); p0 = p0.get('params', p0)
FREE = ['c_xy', 'res_dos', 'g_l', 'g_h', 'T_K', 'G', 'mob_ratio_lh', 'delta_n', 'hq_a', 'g_l_pow', 'g_h_pow']
LOG = {'res_dos', 'g_l', 'g_h', 'T_K', 'G', 'mob_ratio_lh', 'hq_a'}
def unpack(z):
    p = copy.deepcopy(p0)
    for k, v in zip(FREE, z): p[k] = float(np.exp(v)) if k in LOG else float(v)
    p['delta_n'] = abs(p['delta_n'])
    return p
best = [1e9]
def obj(z):
    r, _ = stats.moments(unpack(z)); v = float(np.mean(np.clip(r, -2, 2) ** 2))
    if v < best[0]:
        best[0] = v; print(round(v, 4), {k: round(u, 4) for k, u in unpack(z).items() if k in FREE}, flush=True)
    return v
z0 = np.array([np.log(max(p0.get(k, 0.0), 1e-3)) if k in LOG else p0.get(k, 0.0) for k in FREE])
step = np.array([0.4 if k in LOG else (0.01 if k in ('delta_n', 'c_xy') else 0.5) for k in FREE])
sim = np.vstack([z0] + [z0 + np.eye(len(z0))[i] * step[i] for i in range(len(z0))])
sol = minimize(obj, z0, method='Nelder-Mead', options=dict(initial_simplex=sim, maxfev=int(sys.argv[3]), xatol=1e-3, fatol=1e-4))
p = unpack(sol.x); json.dump(dict(params=p, obj=float(sol.fun)), open(sys.argv[2], 'w'), indent=1)
print('final', sol.fun)
