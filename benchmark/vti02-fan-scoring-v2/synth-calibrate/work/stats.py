"""Tone-amplitude moment statistics live vs sim (calibration fans)."""
import sys, json, copy
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '..'); sys.path.insert(0, '.')
from load import load
from fft_q1 import SIGV
import vti02_sim as vs
from compare import fan_settings, WINS
from evalfan import analyse_arr
W_PCT = float(__import__('os').environ.get('W_PCT', '2'))
EN = {'0825-r8': 55e-9, '0822-r8': 95e-9}
FANS = {}
for nm in EN:
    d = load(nm); st = fan_settings(d)
    L = pd.concat([analyse_arr(d['R'], d['B'], d['n'], st['I'], SIGV[nm], lo, hi, tag) for lo, hi, tag in WINS[nm]])
    FANS[nm] = (d, st, L)

def sim_stats(p, nm, seed=0):
    d, st, L = FANS[nm]; s = p['s825'] if nm == '0825-r8' else p['s822']
    Rc = vs.clean_R(d['B'], d['n'] * s, p, lambda nn: vs.observed_tones(nn, p['r0'], p['r1']))
    q = dict(p); q['e_n_V_rtHz'] = EN[nm]; q['e_excess_V_rtHz'] = 0.0
    R = vs.acquire(Rc, d['B'], st['I'], st['tau'], st['sens'], np.random.default_rng(seed), q, st['slope'], st['delay'])
    S = pd.concat([analyse_arr(R, d['B'], d['n'], st['I'], SIGV[nm], lo, hi, tag) for lo, hi, tag in WINS[nm]])
    S.attrs['R'] = R
    return S

def moments(p, seed=0, verbose=False):
    out = []; rows = []
    for nm, (d, st, L) in FANS.items():
        S = sim_stats(p, nm, seed)
        for tag in L.win.unique():
            a = L[L.win == tag].reset_index(drop=True); b = S[S.win == tag].reset_index(drop=True)
            tert = pd.qcut(a.n_act, 3, labels=False)
            for k in range(3):
                m = tert == k
                fa = 0.5 * a.floor[m].values; fb = 0.5 * b.floor[m].values
                r = {q: float(np.median(np.log(np.maximum(b[q][m].values, fb) / np.maximum(a[q][m].values, fa)))) for q in ('A_light', 'A_heavy', 'A_FL')}
                r['floor'] = float(np.median(np.log(b.floor[m].values / a.floor[m].values)))
                rows.append(dict(fan=nm, win=tag, tert=k, **r)); out += list(r.values())
        # amplitude distribution: high percentiles (clipping) and the negative tail
        pl = np.nanpercentile(d['R'], [1, 99, 99.9]); ps = np.nanpercentile(S.attrs['R'], [1, 99, 99.9])
        extra = [(ps[0] - pl[0]) / 30.0, np.log(ps[1] / pl[1]), np.log(ps[2] / pl[2])]
        rows.append(dict(fan=nm, win='Rpct', tert=-1, A_light=extra[0], A_heavy=extra[1], A_FL=extra[2], floor=0.0))
        out += [W_PCT * e for e in extra]
    df = pd.DataFrame(rows)
    if verbose: print(df.round(2).to_string())
    return np.array(out), df

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); p = p.get('params', p)
    for kv in sys.argv[2:]:
        k, v = kv.split('='); p[k] = float(v)
    r, df = moments(p, verbose=True)
    print('rms log-ratio', np.sqrt(np.mean(r ** 2)).round(3), df[['A_light', 'A_heavy', 'A_FL', 'floor']].mean().round(2).to_dict())
