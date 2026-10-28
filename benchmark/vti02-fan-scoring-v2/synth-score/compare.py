"""Grader component scores vs simulated detection. -> compare_episodes.csv, correlations.csv, scatter.png"""
import sys, pickle, warnings
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from scipy.stats import spearmanr, kendalltau
D = pickle.load(open('designs.pkl', 'rb'))
E = pd.read_csv('sim_episodes.csv')
G = pd.DataFrame([dict(label=d['label'], model=d['model'], h=d['h'], I_nA=d['I'] * 1e9, tau=d['tau'], sens=d['sens'], fd=d['fd'],
                       nB=d['B'].size, Bmin=d['B'].min(), Bmax=d['B'].max(), ncol=d['n'].size, nsim=d['n_sim'].size,
                       band=d['g']['band'], credit=d['g']['credit'], cells=d['g']['cells'], cells_acq=d['g']['cells_acq'],
                       band_e=d['g_e']['band'], cells_e=d['g_e']['cells'], cells_own=d['g_own']['cells'], band_own=d['g_own']['band']) for d in D])
G['cells_h'] = G.cells / G.h; G['cells_acq_h'] = G.cells_acq / G.h


def sim(tone='halder', acq='own', win='own', excess=87e-9):
    x = E[(E.tone == tone) & (E.acq == acq) & (E.win == win) & np.isclose(E.excess, excess)]
    return x.groupby('label')[['a', 'b', 'c', 'light', 'split']].agg(['mean', 'std'])


def corr(M, pairs):
    out = []
    for sx, gy in pairs:
        r, pr = spearmanr(M[sx], M[gy]); t, pt = kendalltau(M[sx], M[gy])
        out.append(dict(sim=sx, grader=gy, spearman=r, p_s=pr, kendall=t, p_k=pt))
    return out


PAIRS = [('a', 'band'), ('a', 'credit'), ('b', 'cells'), ('b', 'cells_acq'), ('c', 'cells_h'), ('c', 'cells_acq_h')]
rows = []
for tone in ('halder', 'observed', 'corpus'):
    for win in ('own', 'clip075'):
        for acq in ('own', 'ref', 'own_noclip'):
            for exc in (55e-9, 87e-9, 165e-9, 0.0):
                s = sim(tone, acq, win, exc)
                M = G.set_index('label').join(pd.DataFrame({k: s[(k, 'mean')] for k in 'abc'}))
                for r in corr(M, PAIRS):
                    rows.append(dict(tone=tone, win=win, acq=acq, excess_nV=round(exc * 1e9), **r))
Cr = pd.DataFrame(rows); Cr.to_csv('correlations.csv', index=False, float_format='%.3f')
# primary table
s = sim(); s0 = sim(win='clip075'); sr = sim(acq='ref'); sn = sim(excess=0.0)
P = G.set_index('label').copy()
for k in 'abc':
    P[f'sim_{k}'] = s[(k, 'mean')]; P[f'sim_{k}_sd'] = s[(k, 'std')]
    P[f'sim075_{k}'] = s0[(k, 'mean')]; P[f'ref_{k}'] = sr[(k, 'mean')]; P[f'nf_{k}'] = sn[(k, 'mean')]
P['sim_light'] = s[('light', 'mean')]; P['sim_split'] = s[('split', 'mean')]
for x, y in (('sim_c', 'cells_h'), ('sim_b', 'cells'), ('sim_a', 'band')):
    P[f'rk_{x}'] = P[x].rank(ascending=False); P[f'rk_{y}'] = P[y].rank(ascending=False)
P['swap_c'] = P.rk_sim_c - P.rk_cells_h; P['swap_b'] = P.rk_sim_b - P.rk_cells; P['swap_a'] = P.rk_sim_a - P.rk_band
P.to_csv('compare_episodes.csv', float_format='%.3f')
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
print(P[['model', 'h', 'nsim', 'band', 'sim_a', 'sim075_a', 'nf_a', 'cells', 'sim_b', 'sim075_b', 'ref_b', 'cells_h', 'sim_c', 'swap_a', 'swap_b', 'swap_c']].round(2).to_string())
print(Cr[(Cr.tone == 'halder') & (Cr.acq == 'own') & (Cr.excess_nV == 87)].round(3).to_string())
