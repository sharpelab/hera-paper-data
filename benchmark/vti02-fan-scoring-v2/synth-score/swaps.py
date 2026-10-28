import sys, warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy.stats import kendalltau, spearmanr
P = pd.read_csv('compare_episodes.csv').set_index('label')
E = pd.read_csv('sim_episodes.csv')
pd.set_option('display.width', 250)
for win in ('own', 'clip075'):
    s = E[(E.tone == 'halder') & (E.acq == 'own') & (E.win == win) & np.isclose(E.excess, 87e-9)].groupby('label')[['a', 'b', 'c']].agg(['mean', 'std'])
    Q = P[['model', 'h', 'band', 'cells', 'cells_h']].copy()
    for k in 'abc':
        Q[k] = s[(k, 'mean')]; Q[k + '_sd'] = s[(k, 'std')]
    Q['rk_g_c'] = Q.cells_h.rank(ascending=False); Q['rk_s_c'] = Q.c.rank(ascending=False)
    Q['rk_g_b'] = Q.cells.rank(ascending=False); Q['rk_s_b'] = Q.b.rank(ascending=False)
    Q['swap_c'] = Q.rk_s_c - Q.rk_g_c; Q['swap_b'] = Q.rk_s_b - Q.rk_g_b
    print(f'\n=== window {win}')
    print(Q.sort_values('swap_c', key=abs, ascending=False).round(2).to_string())
    # bootstrap SE of kendall for c
    rng = np.random.default_rng(0); ks = []
    for _ in range(2000):
        i = rng.integers(0, len(Q), len(Q)); ks.append(kendalltau(Q.cells_h.values[i], Q.c.values[i])[0])
    print('kendall c vs cells_h bootstrap: median %.2f, 90%% [%.2f, %.2f]' % (np.nanmedian(ks), *np.nanpercentile(ks, [5, 95])))
    # seed noise: kendall between two seed-halves of the sim itself
    x = E[(E.tone == 'halder') & (E.acq == 'own') & (E.win == win) & np.isclose(E.excess, 87e-9)]
    s1 = x[x.seed < 2].groupby('label').c.mean(); s2 = x[x.seed >= 3].groupby('label').c.mean()
    print('sim split-half kendall (seeds 0-1 vs 3-4):', round(kendalltau(s1, s2.loc[s1.index])[0], 3))
