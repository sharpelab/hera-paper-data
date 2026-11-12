"""Which grader knob setting best tracks the simulated outcome? Scan k, high-line m, cell width, acquisition term.
Target: simulated b (capped cells of light_true & split) and c = b / h, halder tones, clip075 window, mean over 5 seeds."""
import sys, pickle, warnings, itertools
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from scipy.stats import spearmanr, kendalltau
import designs as DS
D = pickle.load(open('designs.pkl', 'rb'))
E = pd.read_csv('sim_episodes.csv')


def gscore(d, k=3.0, m=3.0, cellw=1.0, clip=0.75, electron_only=False):
    B = np.unique(d['B']); Bw = B[B >= clip]
    n = d['n_sim'] if electron_only else d['n']
    W = 1 / Bw[0] - 1 / Bw[-1]; hi = 1 / (m * np.max(-np.diff(1 / Bw)))
    fl = DS.halder_fl(n); FL = 10.3392 * np.abs(n)
    ok = ~np.isnan(fl) & (FL <= hi); p = np.where(ok, fl * W, 0)
    inb = ok & (p >= k)
    if not inb.any():
        return 0.0, 0
    f = fl[inb]; cell = np.floor((f - f.min()) * W / cellw + 1e-9).astype(int)
    return min(15, np.minimum(3, np.bincount(cell)).sum()) / 15.0, int(inb.sum())


out = []
H = np.array([d['h'] for d in D]); SNR = np.array([d['snr'] for d in D])
for exc in (55e-9, 87e-9, 165e-9):
    s = E[(E.tone == 'halder') & (E.acq == 'own') & (E.win == 'clip075') & np.isclose(E.excess, exc)].groupby('label')[['a', 'b', 'c']].mean()
    sb = s.loc[[d['label'] for d in D]]
    for k, m, cw, acqt in itertools.product((2.0, 2.5, 3.0, 3.5, 4.0), (2.0, 2.5, 3.0), (1.0, 2.0), ('none', 'snr', 'sqrt_snr')):
        q = np.array([gscore(d, k, m, cw)[0] for d in D]); a = np.array([gscore(d, k, m, cw)[1] for d in D])
        mult = {'none': 1.0, 'snr': SNR, 'sqrt_snr': np.sqrt(SNR)}[acqt]
        qa = q * mult
        out.append(dict(excess_nV=round(exc * 1e9), k=k, m=m, cellw=cw, acq=acqt,
                        rho_b=spearmanr(qa, sb.b)[0], tau_b=kendalltau(qa, sb.b)[0],
                        rho_c=spearmanr(qa / H, sb.c)[0], tau_c=kendalltau(qa / H, sb.c)[0],
                        rho_a=spearmanr(a, sb.a)[0], mae_b=float(np.mean(np.abs(qa - sb.b)))))
K = pd.DataFrame(out); K.to_csv('knob_scan.csv', index=False, float_format='%.3f')
pd.set_option('display.width', 250)
for e in (55, 87, 165):
    z = K[K.excess_nV == e]
    print(f'\n== excess {e} nV: default (k3 m3 cw1 none) and top 8 by tau_c')
    print(z[(z.k == 3) & (z.m == 3) & (z.cellw == 1)].round(3).to_string(index=False))
    print(z.sort_values('tau_c', ascending=False).head(8).round(3).to_string(index=False))
    print('marginal mean tau_c by k:', z.groupby('k').tau_c.mean().round(3).to_dict(), ' by m:', z.groupby('m').tau_c.mean().round(3).to_dict(),
          ' by acq:', z.groupby('acq').tau_c.mean().round(3).to_dict(), ' by cellw:', z.groupby('cellw').tau_c.mean().round(3).to_dict())
    print('marginal mean mae_b by acq:', z.groupby('acq').mae_b.mean().round(3).to_dict(), ' by k:', z.groupby('k').mae_b.mean().round(3).to_dict())
