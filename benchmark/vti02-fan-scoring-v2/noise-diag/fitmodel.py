"""Fit the noise model (white + broadband(B) + 1.216 Hz line through Z_t(B)) to per-run, per-B-band, per-axis robust d2 noise of the live
leak-removed quadrature channel, by simulation on each run's real timestamps. Held-out runs are only predicted."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
import model as M
from scipy.optimize import minimize
I_N = {r['run']: r['i_n_pA'] * 1e-12 for r in json.load(open('i_n_series.json'))}
FIT = ['21-r5', '21-r10', '21-r11', '22-r6', '22-r7', '22-r8', '25-r8', '25-r5', '25-r6', '25-r7', '24-r5', '21-r4', '22-r5', '24-r3', '25-r4']
HOLD = ['21-r8', '24-r4', '23-r6', '23-r7']
BANDS = [(-0.1, 0.2), (0.2, 1.5), (1.5, 2.5), (2.5, 4), (4, 6), (6, 8), (8, 11)]
def stats(Z, d, R, B):
    tau = d['tau']; e = np.sqrt(5 / 64 / tau); out = {}
    t = d['t']
    ok = np.abs(R) < 1500
    if d['nrows'] == 1:
        o = np.argsort(B[0]); z = Z[0][o]; b = B[0][o]; okk = ok[0][o]
        dtp = np.nanmedian(np.abs(np.diff(t[0])))
        v = np.r_[np.nan, d2(z), np.nan] / np.sqrt(6) * corr_d2(dtp, tau)
        axes = [('seq', v, b, okk)]
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
for key in FIT + HOLD:
    day, run = int(key[:2]), int(key.split('-r')[1])
    d = loadrun(day, run)
    X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    B = d['B'] if d['B'] is not None else np.zeros_like(X)
    RUNS[key] = dict(d=d, R=R, B=B, live=stats(Yc, d, R, B), i_n=I_N.get(key, 95e-12))
def predict(prm, keys, seed=0):
    out = {}
    for k in keys:
        r = RUNS[k]; rng = np.random.default_rng(seed + hash(k) % 1000)
        Z = M.simulate_quadrature(r['d']['t'], r['B'], r['d']['tau'], r['i_n'], prm, rng)
        out[k] = stats(Z, r['d'], r['R'], r['B'])
    return out
NAMES = ['e_w', 'b1', 'p', 'z0', 'z1']
def unpack(x): return dict(zip(NAMES, [x[0], np.exp(x[1]), x[2], np.exp(x[3]), np.exp(x[4])]))
def loss(x, keys=FIT):
    prm = unpack(x); P = predict(prm, keys); L = []
    for k in keys:
        for kk, v in RUNS[k]['live'].items():
            if kk in P[k]: L.append(np.log(P[k][kk] / v))
    return np.mean(np.square(L))
if __name__ == '__main__':
    x0 = np.array([43, np.log(12), 1.0, np.log(300), np.log(800)])
    print('initial loss', loss(x0))
    r = minimize(loss, x0, method='Nelder-Mead', options=dict(maxiter=300, xatol=1e-3, fatol=1e-5))
    prm = unpack(r.x); print('fit', prm, 'loss', r.fun)
    json.dump(dict(prm=prm, loss_fit=r.fun), open('fit_model.json', 'w'), indent=1)
    P = predict(prm, FIT + HOLD, seed=7)
    for k in FIT + HOLD:
        tag = 'FIT ' if k in FIT else 'HOLD'
        s = f"{tag} {k:7s} tau {RUNS[k]['d']['tau']}: "
        for kk in sorted(RUNS[k]['live']):
            if kk in P[k]: s += f"{kk[0]}@{kk[1]}: {RUNS[k]['live'][kk]:.0f}/{P[k][kk]:.0f}  "
        print(s)
