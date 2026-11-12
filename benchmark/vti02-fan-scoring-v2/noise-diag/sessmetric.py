"""Reproduce the four sessions' quadrature 'excess' metric (synth-calibrate/work/yfloor.py: median column FFT floor of the quadrature
channel along 1/B, band [1.12 F_L, 0.95 Nyq], referred to a 40 nV/rtHz white floor) from the noise model simulated on each fan's own
timestamps, B grid, tau. Usage: sessmetric.py fit2.json [nseeds]"""
import sys, json, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check'); sys.path.insert(0, '.')
from load import load
from fft_q1 import col_fft
import model2 as M
cfg = json.load(open(sys.argv[1])); prm = cfg['prm']; prm['g'] = np.array(prm['g'])
nseed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
I_N = {r['run']: r['i_n_pA'] * 1e-12 for r in json.load(open('i_n_series.json'))}
LIVE = {'0825-r8': 55, '0822-r8': 95, '0821-r8': 165, '0824-r4': 146}
KEY = {'0825-r8': '25-r8', '0822-r8': '22-r8', '0821-r8': '21-r8', '0824-r4': '24-r4'}
def floor_metric(Z, d, I, lo):
    B = d['B']; fl = []
    for j in range(d['nfast']):
        if d['n'][j] < 0.5: continue
        fL = 10.3392 * d['n'][j]
        F, S, m, du, wn = col_fft(Z[:, j] / I, B, lo, B.max())
        hb = (F > 1.12 * fL) & (F < 0.95 * 0.5 / du)
        fl.append(np.median(S[hb]) if hb.sum() > 20 else np.nan)
    return np.nanmedian(fl)
out = {}
for nm in ('0825-r8', '0822-r8', '0821-r8', '0824-r4'):
    d = load(nm); B = d['B']; I = np.median(np.abs(d['I'])); X = d['g']('sr1_X')
    Y = X * np.tan(np.deg2rad(d['g']('sr1_P'))) if 'sr1_P' in d['cols'] else d['g']('sr1_Y')
    tau = d['lk']['sr1']['time_constant']; lo = max(1.0, B.min()) if nm != '0824-r4' else 2.0
    a = np.sum(X * Y) / np.sum(X * X); Yc = Y - a * X
    live_chan = Y if nm == '0824-r4' else Yc
    t = d['t']; Bg = np.broadcast_to(B[:, None], t.shape)
    rng0 = np.random.default_rng(0)
    wf = np.mean([floor_metric(40e-9 * np.sqrt(5 / 64 / tau) * rng0.standard_normal(t.shape), d, I, lo) for _ in range(5)])
    live = 40 * floor_metric(live_chan, d, I, lo) / wf
    sims = {}
    for parts in (('white',), ('white', 'line'), ('white', 'band'), ('white', 'line', 'band')):
        v = []
        for s in range(nseed):
            Z = M.simulate(t, Bg, tau, I_N.get(KEY[nm], 95e-12), prm, np.random.default_rng(100 + s), parts=parts)
            v.append(40 * floor_metric(Z, d, I, lo) / wf)
        sims['+'.join(parts)] = (float(np.mean(v)), float(np.std(v)))
    out[nm] = dict(tau=tau, live_recomputed=float(live), live_reported=LIVE[nm], sims=sims)
    print(nm, f"tau {tau}  live {live:.0f} (reported {LIVE[nm]})  " + '  '.join(f"{k}: {m:.0f}±{s:.0f}" for k, (m, s) in sims.items()), flush=True)
json.dump(out, open('sessmetric_' + sys.argv[1].replace('.json', '') + '.json', 'w'), indent=1)
