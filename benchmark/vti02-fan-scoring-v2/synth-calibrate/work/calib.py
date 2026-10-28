"""Stage-1 calibration: pointwise weighted least squares of the LL model on 0825 r8 + 0822 r8."""
import sys, json, time, copy
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/synth-calibrate')
from load import load
import vti02_sim as vs

CAL = {'0825-r8': dict(delay=2.1, tau=0.3), '0822-r8': dict(delay=1.2, tau=0.3)}
BASE = dict(
    T_K=8.0, g_l=0.25, g_h=0.25, g_l_pow=0.0, g_h_pow=0.0, mass_scale_l=1.0, mass_scale_h=1.0,
    G=0.3, G_pow=0.0, mob_h=10.0, mob_ratio_lh=1.0, c_xy=0.0, delta_n=0.01,
    R0_n=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
    R0_ohm=[164.4, 152.7, 119.1, 95.7, 84.3, 77.6, 70.9, 66.5, 61.9, 58.0, 55.3, 53.2],
    B_w=0.15, e_n_V_rtHz=40e-9, gain_jitter=0.0, field_jitter_T=0.0, r0=0.2065, r1=0.0415,
)
# free parameters: name, initial, lower, upper
FREE = [('s825', 0.95, 0.85, 1.05), ('s822', 1.02, 0.9, 1.12), ('r0', 0.2065, 0.1, 0.35), ('r1', 0.0415, -0.1, 0.2),
        ('T_K', 8.0, 1.0, 20.0), ('g_l', 0.25, 0.02, 1.5), ('g_h', 0.25, 0.02, 1.5),
        ('G', 0.3, 0.01, 3.0), ('G_pow', 0.0, -3, 3), ('mob_ratio_lh', 1.0, 0.05, 20.0), ('c_xy', 0.0, -0.2, 0.2),
        ('delta_n', 0.01, 0.0, 0.08)]

DATA = {}
for nm in CAL:
    d = load(nm)
    cols = np.arange(0, d['nfast'], int(sys.argv[1]) if len(sys.argv) > 1 else 2)
    R = d['R']
    med = np.median(np.abs(R), axis=1)
    w = 3.0 + 0.25 * med
    DATA[nm] = dict(B=d['B'], n=d['n'], R=R, w=w, cols=cols)


def unpack(x):
    p = copy.deepcopy(BASE)
    for (k, *_), v in zip(FREE, x):
        p[k] = float(v)
    return p


def model_fan(p, nm, cols=None):
    D = DATA[nm]; s = p['s825'] if nm == '0825-r8' else p['s822']
    n = D['n'] * s
    tf = lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])
    Rc = vs.clean_R(D['B'], n, p, tone_fn=tf)          # all columns: blur needs neighbours
    c = CAL[nm]
    Rb = vs._blur_rows(Rc, vs.step_weights(c['delay'], c['tau']))
    return Rb if cols is None else Rb[:, cols]


def resid(x):
    p = unpack(x); out = []
    for nm, D in DATA.items():
        Rm = model_fan(p, nm)
        out.append(((Rm - D['R']) / D['w'][:, None])[:, D['cols']].ravel())
    return np.concatenate(out)


if __name__ == '__main__':
    x0 = np.array([f[1] for f in FREE]); lb = [f[2] for f in FREE]; ub = [f[3] for f in FREE]
    t = time.time(); r = resid(x0); print('eval s', time.time() - t, 'cost0', 0.5 * (r ** 2).sum(), flush=True)
    sol = least_squares(resid, x0, bounds=(lb, ub), x_scale='jac', diff_step=1e-3, max_nfev=int(sys.argv[2]) if len(sys.argv) > 2 else 60, verbose=2)
    p = unpack(sol.x)
    print(json.dumps({k: p[k] for k, *_ in FREE}, indent=1))
    json.dump(dict(x=sol.x.tolist(), names=[f[0] for f in FREE], cost=sol.cost, params=p), open('fit1.json', 'w'), indent=1)
