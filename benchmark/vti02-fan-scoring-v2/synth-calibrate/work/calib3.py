"""Stage-3: match per-window, per-density-tertile FFT tone amplitudes and floors (log ratios) on 0825 + 0822."""
import sys, json, copy, time
import numpy as np
from scipy.optimize import least_squares
import stats
p0 = json.load(open(sys.argv[1]))['params'] if 'params' in json.load(open(sys.argv[1])) else json.load(open(sys.argv[1]))
FREE = [('res_dos', 0.4, 0.0, 3.0), ('g_l', p0['g_l'], 0.02, 1.0), ('g_h', p0['g_h'], 0.01, 1.0), ('T_K', p0['T_K'], 1.0, 15.0),
        ('G', p0['G'], 0.02, 2.0), ('mob_ratio_lh', p0['mob_ratio_lh'], 0.05, 20.0), ('delta_n', p0['delta_n'], 0.0, 0.06),
        ('hq_a', p0['hq_a'], 0.0, 10.0), ('g_l_pow', 0.0, -2, 2), ('g_h_pow', 0.0, -2, 2)]
def unpack(x):
    p = copy.deepcopy(p0)
    for (k, *_), v in zip(FREE, x): p[k] = float(v)
    return p
def resid(x):
    r, _ = stats.moments(unpack(x))
    return np.clip(r, -2, 2)
x0 = np.array([f[1] for f in FREE])
t = time.time(); r0 = resid(x0); print('eval', round(time.time() - t, 1), 's; rms0', np.sqrt(np.mean(r0 ** 2)), flush=True)
sol = least_squares(resid, x0, bounds=([f[2] for f in FREE], [f[3] for f in FREE]), diff_step=0.03, max_nfev=60, verbose=2)
p = unpack(sol.x)
print(json.dumps({k: p[k] for k, *_ in FREE}, indent=1), 'rms', np.sqrt(np.mean(sol.fun ** 2)))
json.dump(dict(params=p, rms=float(np.sqrt(np.mean(sol.fun ** 2)))), open(sys.argv[2], 'w'), indent=1)
