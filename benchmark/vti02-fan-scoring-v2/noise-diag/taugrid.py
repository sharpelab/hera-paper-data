"""Predicted quadrature noise vs acquisition settings from the fitted model (usage: taugrid.py fit2.json).
Design: 57-point rows, dt = delay + 0.11 s overhead (measured on all four fans), 21 s row turnaround + ramp, i_n = 95 pA, 10 nA drive.
Per-point noise = robust sd of fast-axis 2nd differences / sqrt(6) (what a within-row estimator sees);
row-to-row = same along B at fixed column; 'rms' = true per-point rms. Also the 24 dB step residual at the chosen delay."""
import sys, json, numpy as np
sys.path.insert(0, '.')
import model2 as M
from nd import rob, d2
cfg = json.load(open(sys.argv[1])); prm = cfg['prm']; prm['g'] = np.array(prm['g'])
I = 10e-9; i_n = 95e-12
def settle(k): return np.exp(-k) * (1 + k + k ** 2 / 2 + k ** 3 / 6)
rows = []
print('B(T) tau(s) delay/tau dt(s) | point-rms nV (white/line/band/total) | fast-d2 sd nV | row-to-row sd nV | total ohm@10nA | step residual')
for Bv in (1.0, 3.0, 5.0, 8.0):
    for tau in (0.001, 0.01, 0.03, 0.1, 0.3, 1.0):
        for k in (1, 3, 7):
            dt = k * tau + 0.11; nf, nr = 57, 60
            row_T = nf * dt + 21.0 + 5.0
            t = (np.arange(nr)[:, None] * row_T + np.arange(nf)[None, :] * dt)
            t = t + np.random.default_rng(1).normal(0, 0.007, t.shape)
            Bg = np.full(t.shape, Bv)
            comp = {}
            for parts in (('white',), ('line',), ('band',), ('white', 'line', 'band')):
                Z = M.simulate(t, Bg, tau, i_n, prm, np.random.default_rng(5), parts=parts)
                comp['+'.join(parts)] = (np.std(Z), rob(d2(Z, 1)) / np.sqrt(6), rob(d2(Z, 0)) / np.sqrt(6))
            w, l, b, tot = comp['white'], comp['line'], comp['band'], comp['white+line+band']
            r = dict(B=Bv, tau=tau, k=k, dt=dt, rms_white=w[0], rms_line=l[0], rms_band=b[0], rms_tot=tot[0], fast=tot[1], row=tot[2], settle=settle(k))
            rows.append(r)
            print(f"{Bv:4.1f} {tau:6.3f} {k:2d} {dt:5.2f} | {w[0]*1e9:6.0f} {l[0]*1e9:5.0f} {b[0]*1e9:5.0f} {tot[0]*1e9:6.0f} | {tot[1]*1e9:6.0f} | {tot[2]*1e9:6.0f} | {tot[0]/I:6.2f} | {settle(k):.3f}")
json.dump(rows, open('taugrid.json', 'w'), indent=1)
