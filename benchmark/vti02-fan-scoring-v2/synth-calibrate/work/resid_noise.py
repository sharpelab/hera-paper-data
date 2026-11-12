"""Where does the live FFT floor come from? Residual (live - clean model) decomposition on the calibration fans."""
import sys, json
import numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/synth-calibrate')
sys.path.insert(0, '.')
from load import load
from fft_q1 import col_fft, SIGV
import vti02_sim as vs
from compare import fan_settings

p = json.load(open(sys.argv[1])); p = p.get('params', p)
SC = {'0825-r8': p.get('s825', 0.95), '0822-r8': p.get('s822', 1.02)}
for nm in ['0825-r8', '0822-r8']:
    d = load(nm); st = fan_settings(d); B = d['B']; o = np.argsort(B)
    tf = lambda nn: vs.observed_tones(nn, p['r0'], p['r1'])
    Rc = vs.clean_R(B, d['n'] * SC[nm], p, tf)
    Rc = vs._blur_rows(Rc, vs.step_weights(st['delay'], st['tau']))
    res = d['R'] - Rc
    sig_w = p['e_n_V_rtHz'] * np.sqrt(5 / 64 / st['tau']) / st['I']
    print(f'== {nm}: white sigma_R {sig_w:.2f} ohm; SIGV-based {SIGV[nm] / st["I"]:.2f}')
    for lo, hi in ((1, 1.5), (1.5, 2.5), (2.5, 4), (4, 10)):
        s = (B >= lo) & (B < hi)
        r = res[s]
        # per-row common mode (mean over columns) vs expectation from independent residuals
        cm = r.mean(1); exp_cm = r.std() / np.sqrt(r.shape[1])
        # per-row gain: fit res = g_i * Rc_i
        g = (r * Rc[s]).sum(1) / (Rc[s] ** 2).sum(1)
        print(f'  B[{lo},{hi}) rows {s.sum():3d}: rms resid {r.std():7.2f}  rms clean {Rc[s].std():7.2f}  row-mean rms {cm.std():6.2f} (indep exp {exp_cm:5.2f})'
              f'  row gain rms {g.std():.3f}  corr(|res|,Rc) {np.corrcoef(np.abs(r).ravel(), Rc[s].ravel())[0,1]:+.2f}')
    # FFT floor of: live, clean model, residual, white noise
    for lo in (1.0, 1.53, 2.0):
        fl = {k: [] for k in ('live', 'clean', 'resid', 'white', 'clean+white')}
        rng = np.random.default_rng(1)
        for j in range(d['nfast']):
            n = d['n'][j]; fL = 10.3392 * n
            for k, y in (('live', d['R'][:, j]), ('clean', Rc[:, j]), ('resid', res[:, j]), ('white', sig_w * rng.standard_normal(B.size)),
                         ('clean+white', Rc[:, j] + sig_w * rng.standard_normal(B.size))):
                F, S, m, du, wn = col_fft(y, B, lo, B.max())
                hb = (F > 1.12 * fL) & (F < 0.95 * 0.5 / du)
                fl[k].append(np.median(S[hb]) if hb.sum() > 20 else np.nan)
        print(f'  window [{lo}, Bmax] median floor:', {k: round(float(np.nanmedian(v)), 2) for k, v in fl.items()})
