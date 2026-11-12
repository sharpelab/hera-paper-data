"""Validation: live vs simulated FFT metrics, detections, floors, onsets. usage: validate.py params.json tones(observed|corpus) nseeds [excess=default|session]"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '..'); sys.path.insert(0, '.')
from load import load
from fft_q1 import SIGV, col_fft
import vti02_sim as vs
from compare import fan_settings, WINS, SCALE
from evalfan import analyse_arr
import onset_cmp
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

P = json.load(open(sys.argv[1])); P = P.get('params', P)
TONES = sys.argv[2]; NS = int(sys.argv[3]); EXC = sys.argv[4] if len(sys.argv) > 4 else 'default'
SESSION_EXC = {'0825-r8': 38e-9, '0822-r8': 87e-9, '0821-r8': 159e-9, '0824-r4': 142e-9}   # from quadrature floors (yfloor.py)
SC = dict(SCALE); SC['0825-r8'] = P['s825']; SC['0822-r8'] = P['s822']
FANS = ['0821-r8', '0824-r4', '0825-r8', '0822-r8']
WIN_MAIN = {'0821-r8': WINS['0821-r8'], '0824-r4': [(2.0, None, 'o2.0'), (1.53, None, 'o1.53'), (0.75, None, 'full0.75')],
            '0825-r8': WINS['0825-r8'], '0822-r8': WINS['0822-r8']}


def tonefn(p):
    return (lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])) if TONES == 'observed' else vs.corpus_tones


def floor_shape(R, B, n, lo, hi=None):
    """median over columns of |FFT|/floor in bins of F/F_L over the floor band"""
    lo = max(lo, B.min()); hi = min(hi or B.max(), B.max())
    edges = np.arange(1.12, 3.01, 0.12); acc = [[] for _ in edges[:-1]]
    for j in range(R.shape[1]):
        if n[j] < 0.5 or not np.all(np.isfinite(R[:, j])): continue
        F, S, m, du, wn = col_fft(R[:, j], B, lo, hi); fL = 10.3392 * n[j]
        hb = (F > 1.12 * fL) & (F < 0.95 * 0.5 / du)
        if hb.sum() <= 20: continue
        fl = np.median(S[hb]); x = F / fL
        for k in range(len(edges) - 1):
            mk = hb & (x >= edges[k]) & (x < edges[k + 1])
            if mk.any(): acc[k].append(np.median(S[mk]) / fl)
    return 0.5 * (edges[1:] + edges[:-1]), np.array([np.median(a) if len(a) > 3 else np.nan for a in acc])


rows = []; det = []; shapes = {}; onsets = []; specs = {}
for nm in FANS:
    d = load(nm); st = fan_settings(d); B = d['B']; n_true = d['n'] * SC[nm]
    ok = n_true > 0.25
    p = dict(P); p['e_excess_V_rtHz'] = SESSION_EXC[nm] if EXC == 'session' else P['e_excess_V_rtHz']
    Rc = vs.clean_R(B, n_true[ok], p, tonefn(p))
    L = pd.concat([analyse_arr(d['R'][:, ok], B, d['n'][ok], st['I'], SIGV[nm], lo, hi, tag) for lo, hi, tag in WIN_MAIN[nm]])
    L['src'] = 'live'; L['seed'] = -1
    Ss = []
    for seed in range(NS):
        R = vs.acquire(Rc, B, st['I'], st['tau'], st['sens'], np.random.default_rng(seed), p, st['slope'], st['delay'])
        S = pd.concat([analyse_arr(R, B, d['n'][ok], st['I'], SIGV[nm], lo, hi, tag) for lo, hi, tag in WIN_MAIN[nm]])
        S['src'] = 'sim'; S['seed'] = seed; Ss.append(S)
        if seed == 0:
            Rs0 = R
            lo_s = WIN_MAIN[nm][-1][0] if nm == '0824-r4' else 1.0
            shapes[nm] = (floor_shape(d['R'][:, ok], B, d['n'][ok], 2.0), floor_shape(R, B, d['n'][ok], 2.0))
            if nm != '0824-r4':
                onsets.append(onset_cmp.onsets(d['R'][:, ok], B, d['n'][ok], 2, 'live').assign(fan=nm))
                onsets.append(onset_cmp.onsets(R, B, d['n'][ok], 2, 'sim').assign(fan=nm))
            specs[nm] = (d['R'][:, ok], R, B, d['n'][ok])
    S = pd.concat(Ss)
    for tag in L.win.unique():
        a = L[L.win == tag]
        for seed in range(NS):
            b = S[(S.win == tag) & (S.seed == seed)]
            det.append(dict(fan=nm, win=tag, seed=seed, cols=len(a), live_light_true=int(a.light_true.sum()), sim_light_true=int(b.light_true.sum()),
                            live_split=int(a.split_true.sum()), sim_split=int(b.split_true.sum()), live_FL=int(a.det_FL.sum()), sim_FL=int(b.det_FL.sum()),
                            live_heavy=int(a.det_heavy.sum()), sim_heavy=int(b.det_heavy.sum()),
                            live_floor_over_white=float(np.nanmedian(a.floor / a.floor_noise)), sim_floor_over_white=float(np.nanmedian(b.floor / b.floor_noise)),
                            floor_ratio=float(np.nanmedian(b.floor.values / a.floor.values))))
            for q in ('snr_light', 'snr_heavy', 'snr_FL'):
                rr = b[q].values / np.maximum(a[q].values, 1e-9)
                for x in rr[np.isfinite(rr) & (a[q].values > 0)]:
                    rows.append(dict(fan=nm, win=tag, seed=seed, tone=q[4:], ratio=x))

D = pd.DataFrame(det); Rr = pd.DataFrame(rows); O = pd.concat(onsets) if onsets else pd.DataFrame()
tag = f'{TONES}_{EXC}'
D.to_csv(f'../validation_detections_{tag}.csv', index=False); Rr.to_csv(f'../validation_snr_ratios_{tag}.csv', index=False)
if len(O): O.to_csv(f'../validation_onsets_{tag}.csv', index=False)
pd.set_option('display.width', 250)
g = D.groupby(['fan', 'win'], sort=False)
T = g.agg(cols=('cols', 'first'), light_live=('live_light_true', 'first'), light_sim=('sim_light_true', 'mean'), light_sim_sd=('sim_light_true', 'std'),
          split_live=('live_split', 'first'), split_sim=('sim_split', 'mean'), split_sim_sd=('sim_split', 'std'),
          FL_live=('live_FL', 'first'), FL_sim=('sim_FL', 'mean'), heavy_live=('live_heavy', 'first'), heavy_sim=('sim_heavy', 'mean'),
          floorW_live=('live_floor_over_white', 'first'), floorW_sim=('sim_floor_over_white', 'mean'), floor_ratio=('floor_ratio', 'mean')).round(2)
print(T.to_string())
Q = Rr.groupby(['fan', 'tone'], sort=False).ratio.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])[['count', '10%', '25%', '50%', '75%', '90%']].round(2)
print('\nSNR ratio sim/live (all windows, seeds):'); print(Q.to_string())
if len(O):
    print('\nonsets (n tracked, median onset B):')
    for fan in O.fan.unique():
        for src in ('live', 'sim'):
            print(' ', fan, src, onset_cmp.summarize(O[(O.fan == fan) & (O.src == src)]))
# ---- plots
fig, axs = plt.subplots(2, 4, figsize=(22, 9))
for i, nm in enumerate(FANS):
    ax = axs[0, i]
    (x, yl), (_, ys) = shapes[nm]
    ax.plot(x, yl, 'k-o', ms=3, label='live'); ax.plot(x, ys, 'r-o', ms=3, label='sim (seed 0)')
    ax.set_title(f'{nm} floor shape [2,Bmax]: |FFT|/floor vs F/F_L'); ax.set_xlabel('F / F_L'); ax.legend(); ax.set_ylim(0, 3)
    ax = axs[1, i]
    for q, c in (('light', 'tab:blue'), ('heavy', 'tab:orange'), ('FL', 'tab:green')):
        v = Rr[(Rr.fan == nm) & (Rr.tone == q)].ratio
        if len(v): ax.hist(np.log10(v.clip(1e-2, 1e2)), bins=40, histtype='step', color=c, label=f'{q} med {np.median(v):.2f}')
    ax.axvline(0, color='k', lw=0.5); ax.set_xlabel('log10 SNR sim/live'); ax.legend(fontsize=8); ax.set_title(f'{nm} per-column SNR ratio')
fig.tight_layout(); fig.savefig(f'../validation_summary_{tag}.png', dpi=70)
for nm in FANS:
    Rl, Rs, B, n = specs[nm]
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    o = np.argsort(B); on = np.argsort(n); vmax = np.nanpercentile(Rl, 97)
    for ax, R, t in ((axs[0, 0], Rl, 'live'), (axs[0, 1], Rs, 'sim')):
        ax.pcolormesh(n[on], B[o], R[o][:, on], shading='nearest', vmin=0, vmax=vmax); ax.set_title(f'{nm} {t} R(n, B)'); ax.set_xlabel('n'); ax.set_ylabel('B (T)')
    lo = WIN_MAIN[nm][1][0] if nm != '0824-r4' else 0.75
    lo = 1.0 if nm in ('0822-r8', '0825-r8') else lo
    for ax, R, t in ((axs[1, 0], Rl, 'live'), (axs[1, 1], Rs, 'sim')):
        sel = n > 0.3
        Z = []; ns = n[sel]
        for j in np.where(sel)[0]:
            F, S, m, du, wn = col_fft(R[:, j], B, max(lo, B.min()), B.max())
            hb = (F > 1.12 * 10.3392 * n[j]) & (F < 0.95 * 0.5 / du)
            fl = np.median(S[hb]) if hb.sum() > 20 else np.median(S)
            Z.append(S / fl)
        Z = np.array(Z); oo = np.argsort(ns)
        ax.pcolormesh(F, ns[oo], np.log10(np.maximum(Z[oo], 0.3)), shading='nearest', cmap='magma', vmin=0, vmax=2)
        ax.plot(10.3392 * ns[oo], ns[oo], 'w:', lw=0.8)
        ax.set_xlim(0, 50); ax.set_title(f'{t} |FFT|/floor, window [{lo}, Bmax] (dotted: 10.34 n)'); ax.set_xlabel('F (T)')
    fig.tight_layout(); fig.savefig(f'../validation_{nm}_{tag}.png', dpi=65); plt.close('all')
