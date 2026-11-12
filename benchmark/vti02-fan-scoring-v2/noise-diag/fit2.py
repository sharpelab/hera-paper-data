"""Fit model2 to per-run/axis/B-band robust d2 noise of the live quadrature channel (simulation on real timestamps)."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
import model2 as M
from scipy.optimize import minimize
I_N = {r['run']: r['i_n_pA'] * 1e-12 for r in json.load(open('i_n_series.json'))}
FIT = ['21-r5', '22-r6', '22-r7', '22-r9', '22-r8', '25-r8', '25-r7', '24-r5', '21-r4', '22-r5', '24-r3', '25-r4', '21-r10', '21-r11']
HOLD = ['21-r8', '24-r4', '23-r6', '23-r7', '25-r5', '25-r6']
BANDS = [(-0.1, 0.2), (0.2, 1.5), (1.5, 2.5), (2.5, 4), (4, 6), (6, 8), (8, 11)]
def stats(Z, d, R, B):
    tau = d['tau']; e = np.sqrt(5 / 64 / tau); out = {}; t = d['t']; ok = np.abs(R) < 1500
    if d['nrows'] == 1:
        o = np.argsort(t[0]); z = Z[0][o]; b = B[0][o]; okk = ok[0][o]
        dtp = np.nanmedian(np.abs(np.diff(t[0])))
        axes = [('seq', np.r_[np.nan, d2(z), np.nan] / np.sqrt(6) * corr_d2(dtp, tau), b, okk)]
    else:
        dtp = np.nanmedian(np.diff(t, axis=1)); axes = []
        if d['nfast'] > 6:
            v = np.full(Z.shape, np.nan); v[:, 1:-1] = d2(Z, 1) / np.sqrt(6) * corr_d2(dtp, tau); axes.append(('fast', v, B, ok))
        if d['nrows'] > 6:
            v = np.full(Z.shape, np.nan); v[1:-1] = d2(Z, 0) / np.sqrt(6); axes.append(('slow', v, B, ok))
    for ax, v, b, okk in axes:
        for lo, hi in BANDS:
            m = (b >= lo) & (b < hi) & okk & np.isfinite(v)
            if m.sum() >= 30: out[(ax, lo)] = rob(v[m]) / e * 1e9
    return out
RUNS = {}
def load_all(keys):
    for key in keys:
        if key in RUNS: continue
        day, run = int(key[:2]), int(key.split('-r')[1]); d = loadrun(day, run)
        X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
        m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
        B = d['B'] if d['B'] is not None else np.zeros_like(X)
        RUNS[key] = dict(d=d, R=R, B=B, live=stats(Yc, d, R, B), i_n=I_N.get(key, 95e-12))
def predict(prm, keys, seed=0, nrep=1):
    out = {}
    for k in keys:
        r = RUNS[k]; acc = {}
        for rep in range(nrep):
            rng = np.random.default_rng(seed + 1000 * rep + sum(map(ord, k)))
            Z = M.simulate(r['d']['t'], r['B'], r['d']['tau'], r['i_n'], prm, rng)
            for kk, v in stats(Z, r['d'], r['R'], r['B']).items(): acc.setdefault(kk, []).append(v)
        out[k] = {kk: float(np.sqrt(np.mean(np.square(v)))) for kk, v in acc.items()}
    return out
def unpack(x):
    return dict(e_w=x[0], z0=np.exp(x[1]), z1=np.exp(x[2]), f_b=np.exp(x[3]), w_b=np.exp(x[4]), g=np.exp(x[5:]))
def loss(x, keys):
    prm = unpack(x); P = predict(prm, keys); L = []
    for k in keys:
        for kk, v in RUNS[k]['live'].items():
            if kk in P[k]: L.append(np.log(P[k][kk] / v))
    return float(np.mean(np.square(L)))
if __name__ == '__main__':
    load_all(FIT + HOLD)
    x0 = np.r_[43, np.log(150), np.log(300), np.log(0.6), np.log(0.3), np.log([20, 40, 60, 90, 150, 150, 100, 80])]
    best = None
    for start_fb in (0.3, 0.7, 1.5):
        x0[3] = np.log(start_fb)
        r = minimize(loss, x0, args=(FIT,), method='Powell', options=dict(maxiter=4000, xtol=1e-3, ftol=1e-5))
        print('start f_b', start_fb, '->', unpack(r.x), r.fun, flush=True)
        if best is None or r.fun < best.fun: best = r
    prm = unpack(best.x)
    json.dump(dict(prm={k: (v.tolist() if hasattr(v, 'tolist') else v) for k, v in prm.items()}, knots=M.KNOTS.tolist(), loss_fit=best.fun,
                   loss_hold=loss(best.x, HOLD), fit=FIT, hold=HOLD), open('fit2.json', 'w'), indent=1)
    print('loss fit', best.fun, 'loss hold', loss(best.x, HOLD))
    P = predict(prm, FIT + HOLD, seed=11, nrep=3)
    for k in FIT + HOLD:
        tag = 'FIT ' if k in FIT else 'HOLD'
        s = f"{tag} {k:7s} tau {RUNS[k]['d']['tau']}: "
        for kk in sorted(RUNS[k]['live']):
            if kk in P[k]: s += f"{kk[0][0]}{kk[1]:g}: {RUNS[k]['live'][kk]:.0f}/{P[k][kk]:.0f}  "
        print(s)
