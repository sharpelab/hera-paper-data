"""Detection rate vs light-tone periods in window (k_light_ref), live vs sim, pooled like q1_eval (0821/0822/0825, all windows)."""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '..'); sys.path.insert(0, '.')
from load import load
from fft_q1 import SIGV
import vti02_sim as vs
from compare import fan_settings
from evalfan import analyse_arr
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
p = vs.load_params()
SC = {'0825-r8': p['s825'], '0822-r8': p['s822'], '0821-r8': 1.007}
CFG = [('0821-r8', 2.0, None, 'o2.0'), ('0822-r8', 2.0, None, 'o2.0'), ('0822-r8', 1.53, None, 'o1.53'), ('0822-r8', 1.0, None, 'full1.0'), ('0822-r8', 1.0, 6.0, 'ana1-6'),
       ('0825-r8', 2.0, None, 'o2.0'), ('0825-r8', 1.53, None, 'o1.53'), ('0825-r8', 1.0, None, 'full1.0'),
       ('0822-r8', 1.0, 2.0, 'sub1-2'), ('0825-r8', 1.0, 2.0, 'sub1-2'), ('0822-r8', 1.0, 1.53, 'sub1-1.53'), ('0825-r8', 1.0, 1.53, 'sub1-1.53')]
out = []
cache = {}
for tones in ('observed', 'corpus'):
    tf = (lambda nn: vs.observed_tones(nn)) if tones == 'observed' else vs.corpus_tones
    for nm in ('0821-r8', '0822-r8', '0825-r8'):
        d = load(nm); st = fan_settings(d)
        Rc = vs.clean_R(d['B'], d['n'] * SC[nm], p, tf)
        for seed in range(3):
            R = vs.acquire(Rc, d['B'], st['I'], st['tau'], st['sens'], np.random.default_rng(seed), p, st['slope'], st['delay'])
            cache[(tones, nm, seed)] = (d, st, R)
for nm, lo, hi, tag in CFG:
    d, st, _ = cache[('observed', nm, 0)]
    a = analyse_arr(d['R'], d['B'], d['n'], st['I'], SIGV[nm], lo, hi, tag).assign(src='live', fan=nm, seed=-1)
    out.append(a)
    for tones in ('observed', 'corpus'):
        for seed in range(3):
            _, _, R = cache[(tones, nm, seed)]
            out.append(analyse_arr(R, d['B'], d['n'], st['I'], SIGV[nm], lo, hi, tag).assign(src=f'sim_{tones}', fan=nm, seed=seed))
A = pd.concat(out)
bins = [0, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 8.0]
A['kbin'] = pd.cut(A.k_light_ref, bins)
T = A.groupby(['kbin', 'src'], observed=True).agg(N=('col', 'size'), light_true=('light_true', 'mean'), split=('split_true', 'mean')).round(2).unstack('src')
pd.set_option('display.width', 250); print(T.to_string())
A.to_csv('../validation_kcurve_columns.csv', index=False)
fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
x = np.array([0.5 * (b.left + b.right) for b in T.index])
for ax, q in zip(axs, ('light_true', 'split')):
    for src, c in (('live', 'k'), ('sim_observed', 'r'), ('sim_corpus', 'b')):
        ax.plot(x, T[(q, src)], c + '-o', label=src)
    ax.set_xlabel('k_light_ref (light periods in window)'); ax.set_ylabel(f'{q} rate'); ax.set_title(f'{q} vs k: 0821+0822+0825, all windows'); ax.legend(); ax.set_ylim(0, 1.05)
fig.tight_layout(); fig.savefig('../validation_kcurve.png', dpi=80)
