import sys, json, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '..'); sys.path.insert(0, '.')
from load import load
from fft_q1 import col_fft
import vti02_sim as vs
from compare import fan_settings
p = json.load(open(sys.argv[1])); p = p.get('params', p)
for nm, s in (('0825-r8', p['s825']), ('0822-r8', p['s822'])):
    d = load(nm); st = fan_settings(d); B = d['B']
    Rc = vs._blur_rows(vs.clean_R(B, d['n'] * s, p, lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])), vs.step_weights(st['delay'], st['tau']))
    sw = p['e_n_V_rtHz'] * np.sqrt(5 / 64 / st['tau']) / st['I']
    rng = np.random.default_rng(0)
    for lo, hi in ((1, 3), (1, 4), (1, 6), (1, 8), (1, 10), (2, 6), (2, 10)):
        if hi > B.max() + 0.01: continue
        f = {'live': [], 'clean+w': [], 'white': []}
        for j in range(d['nfast']):
            fL = 10.3392 * d['n'][j]
            for k, y in (('live', d['R'][:, j]), ('clean+w', Rc[:, j] + sw * rng.standard_normal(B.size)), ('white', sw * rng.standard_normal(B.size))):
                F, S, m, du, wn = col_fft(y, B, lo, hi)
                hb = (F > 1.12 * fL) & (F < 0.95 * 0.5 / du)
                f[k].append(np.median(S[hb]) if hb.sum() > 20 else np.nan)
        L, C, W = (np.array(f[k]) for k in ('live', 'clean+w', 'white'))
        # adjacent-column correlation of log floor (deterministic leakage is smooth along n)
        cc = lambda a: np.corrcoef(np.log(a[:-1]), np.log(a[1:]))[0, 1]
        print(f'{nm} [{lo},{hi}] floor live {np.nanmedian(L):6.2f} clean+w {np.nanmedian(C):6.2f} white {np.nanmedian(W):5.2f} | adj-col corr log floor live {cc(L):+.2f} sim {cc(C):+.2f}')
