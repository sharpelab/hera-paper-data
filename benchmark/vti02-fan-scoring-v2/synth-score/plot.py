import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
P = pd.read_csv('compare_episodes.csv').set_index('label')
E = pd.read_csv('sim_episodes.csv')
COL = {'sonnet': '#2a78d6', 'haiku': '#eb6834', 'fable': '#1baf7a', 'opus': '#eda100', 'sol': '#e87ba4', 'luna': '#008300', 'astra': '#4a3aa7', 'live': '#555555'}
MK = {'sonnet': 'o', 'haiku': 's', 'fable': 'D', 'opus': '^', 'sol': 'v', 'luna': 'P', 'astra': 'X', 'live': '*'}
fig, ax = plt.subplots(2, 3, figsize=(15, 9.5))
for r, win in enumerate(('clip075', 'own')):
    s = E[(E.tone == 'halder') & (E.acq == 'own') & (E.win == win) & np.isclose(E.excess, 87e-9)].groupby('label')[['a', 'b', 'c']].agg(['mean', 'std'])
    for c, (sk, gk, gl) in enumerate((('a', 'band', 'grader band count'), ('b', 'cells', 'grader capped cells'), ('c', 'cells_h', 'grader cells / h'))):
        a = ax[r, c]
        for lab, row in P.iterrows():
            m = row.model
            a.errorbar(row[gk], s.loc[lab, (sk, 'mean')], yerr=s.loc[lab, (sk, 'std')], fmt=MK[m], color=COL[m], ms=8 if m != 'live' else 12,
                       mec='white', mew=1, ecolor='#bbbbbb', elinewidth=1, capsize=0, label=m)
        lim = max(P[gk].max(), s[(sk, 'mean')].max()) * 1.08
        a.plot([0, lim], [0, lim], color='#cccccc', lw=1, zorder=0)
        a.set_xlim(-0.03 * lim, lim); a.set_ylim(-0.03 * lim, lim)
        a.set_xlabel(gl + ' (Halder, 0.75 T clip)'); a.set_ylabel(f'sim {sk}' + (' (cols light&split)' if sk == 'a' else ' (capped cells)' if sk == 'b' else ' (cells / h)'))
        a.set_title(f'{sk} vs {gk}, detection window: {"0.75 T clip" if win == "clip075" else "design own"}', fontsize=10)
        a.grid(color='#eeeeee'); [sp.set_visible(False) for k, sp in a.spines.items() if k in ('top', 'right')]
        for lab in ('fable-corpus/20260923T011400-r3w0gf', 'opus-none/20260923T013750-ou2xbh', 'live 0821-r8', 'fable-corpus/20260922T200401', 'fable-corpus/20260922T192335 #1'):
            a.annotate(lab.split('/')[-1][-12:], (P.loc[lab, gk], s.loc[lab, (sk, 'mean')]), fontsize=7, color='#444444', xytext=(4, 4), textcoords='offset points')
h, l = ax[0, 0].get_legend_handles_labels(); u = dict(zip(l, h))
fig.legend(u.values(), u.keys(), loc='upper center', bbox_to_anchor=(0.5, 0.965), ncol=8, frameon=False)
fig.suptitle('Grader component score vs simulated detection (Halder tones, own acquisition, 87 nV/rtHz excess, 5 seeds; bars = seed sd)', y=0.995, fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig('scatter.png', dpi=110)
