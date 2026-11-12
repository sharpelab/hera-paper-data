"""Per-episode table, rank correlations with the component score and simulated detection, Pareto scatter.
-> episodes.csv, correlations.csv, pareto.png, table.md"""
import sys, pickle
import numpy as np, pandas as pd
from scipy.stats import spearmanr, kendalltau
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = pickle.load(open('designs.pkl', 'rb'))
S = pd.read_csv('scores.csv')
E_STAR = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0   # decisive level (nats, sigma_a 0.5)
SA = 'nats0.5'
G = pd.DataFrame([dict(label=d['label'], model=d['model'], corpus=d['corpus'], cut={'3a4cf818': '08-22', '45433bea': '08-21'}.get(d['cut'], d['cut']),
                       h=d['h'], I_nA=d['I'] * 1e9, tau=d['tau'], fd=d['fd'], Bmin=d['B'].min(), Bmax=d['B'].max(), nB=d['B'].size,
                       ncol=d['n'].size, cells075=d['cells075'], snr_mult=d['snr_mult']) for d in D]).set_index('label')
P = S.pivot(index='label', columns='setting', values=SA)
G['E_base'] = P['base']; G['E_corner_alias'] = P['corner']; G['E_corner'] = P['corner_nyq']; G['E_nyq'] = P['nyq']
G['E_min1'] = P.drop(columns=['corner', 'corner_nyq', 'nyq', 'support', 'quant_mean', 'M4Q2', 'clutter', 'light2', 'band']).min(axis=1)    # worst one-at-a-time physics/noise nuisance
G['E_band'] = P['band']; G['E_clutter'] = P['clutter']; G['E_M4Q2'] = P['M4Q2']
base = S[S.setting == 'base'].set_index('label')
G['KL_noise'] = base['KL']; G['cells'] = base['cells']; G['active'] = base['active']; G['E0.7'] = base['nats0.7']; G['E1.0'] = base['nats1.0']
G['corner_of'] = S[S.setting == 'corner'].set_index('label')['corner_of']; G['E_support'] = P['support']
G['Q_io'] = np.minimum(1.0, G.E_corner / E_STAR)
G['Q_io_base'] = np.minimum(1.0, G.E_base / E_STAR)
# simulated detection: synth-score (87 nV, clip 0.75, capped cells of light AND split) and the vti_noise generator (own acquisition, band off)
ss = pd.read_csv('../synth-score/compare_episodes.csv').set_index('label')
G['sim075_b'] = ss['sim075_b']
acq = pd.read_csv('/data/sharpelab/hera-data/vti-noise/generator/work/acq_episodes.csv')
a = acq[(acq.variant == 'band_off') & (acq.acq == 'own') & (acq.win == 'clip075')].groupby('label')['b'].mean()
G['simvn_b'] = a
G.to_csv('episodes.csv', float_format='%.4g')
rows = []
for y in ('cells075', 'sim075_b', 'simvn_b'):
    for x in ('E_corner', 'E_corner_alias', 'E_base', 'KL_noise'):
        m = G[[x, y]].dropna()
        r, pr = spearmanr(m[x], m[y]); t, pt = kendalltau(m[x], m[y])
        rows.append(dict(x=x, y=y, n=len(m), spearman=r, p_s=pr, kendall=t, p_k=pt))
Cr = pd.DataFrame(rows); Cr.to_csv('correlations.csv', index=False, float_format='%.3f')
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
print(Cr.round(3).to_string())
cols = ['model', 'corpus', 'cut', 'h', 'tau', 'I_nA', 'Bmin', 'nB', 'ncol', 'KL_noise', 'active', 'cells', 'E_base', 'E_corner_alias', 'E_corner', 'E_support', 'corner_of', 'E_band', 'E_clutter',
        'E0.7', 'E1.0', 'Q_io', 'cells075', 'sim075_b', 'simvn_b']
T = G[cols].sort_values('E_corner', ascending=False)
print(T.round(2).to_string())
with open('table.md', 'w') as f:
    f.write('| episode | model | arm | cut | h | tau | Bmin | KL noise (nats) | active cols | cells | E base | E corner (aliased ok) | E corner + Nyquist | Q_io | cells075 | sim075_b | simvn_b |\n|' + '---|' * 17 + '\n')
    for lab, r in T.iterrows():
        f.write(f"| {lab} | {r.model} | {r.corpus} | {r.cut} | {r.h:.2f} | {r.tau} | {r.Bmin:.2f} | {r.KL_noise:.3g} | {int(r.active)} | {r.cells:.1f} | {r.E_base:.1f} | {r.E_corner_alias:.1f} | {r.E_corner:.1f} | {r.Q_io:.2f} | {r.cells075:.2f} | "
                f"{'' if pd.isna(r.sim075_b) else f'{r.sim075_b:.2f}'} | {'' if pd.isna(r.simvn_b) else f'{r.simvn_b:.2f}'} |\n")
# Pareto scatter: evidence (least favourable) vs hours
fig, axs = plt.subplots(1, 2, figsize=(13, 5.2))
ax = axs[0]
mk = {'live': ('k', '*'), 'opus': ('C3', 'o'), 'fable': ('C0', 'o'), 'sonnet': ('C0', 's'), 'haiku': ('C0', '^'), 'sol': ('C2', 'o'), 'luna': ('C2', 's'), 'astra': ('C1', 'o')}
for lab, r in G.iterrows():
    c, m = mk.get(r.model, ('gray', 'x'))
    ax.scatter(r.h, r.E_corner, c=c, marker=m, s=70 if r.model == 'live' else 35, edgecolor='k' if r.corpus == 'corpus' else 'none', lw=0.8, zorder=3)
    if r.model == 'live' or r.E_corner < 2 or r.h > 8:
        ax.annotate(lab.replace('live ', '').split('/')[0][:14] + ('' if r.model == 'live' else ' ' + lab.split('/')[-1][-6:]), (r.h, r.E_corner), fontsize=7, xytext=(3, 3), textcoords='offset points')
# Pareto front
o = G.sort_values('h'); best = -1; fr = []
for lab, r in o.iterrows():
    if r.E_corner > best:
        fr.append((r.h, r.E_corner)); best = r.E_corner
fr = np.array(fr); ax.step(fr[:, 0], fr[:, 1], where='post', c='gray', lw=1, zorder=1)
ax.axhline(E_STAR, ls='--', c='k', lw=0.8); ax.text(1.0, E_STAR * 1.03, f'decisive {E_STAR:g} nats', fontsize=8)
ax.set_xscale('log'); ax.set_xlabel('hours (grader cost model)'); ax.set_ylabel('evidence E: least-favourable nuisance, Nyquist-gated (nats)')
ax.set_title('Ideal-observer evidence vs time (black edge = corpus arm)')
for k, (c, m) in mk.items():
    ax.scatter([], [], c=c, marker=m, label=k)
ax.legend(fontsize=7, loc='lower right')
ax = axs[1]
ax.scatter(G.cells075, G.E_corner, c='C0', s=25, label='component score (cells, 0.75 T clip)')
ax.scatter(G.sim075_b, G.E_corner, c='C3', s=20, marker='^', label='synth-score sim detection b (87 nV)')
for lab, r in G.iterrows():
    if r.model == 'live':
        ax.annotate(lab.replace('live ', ''), (r.cells075, r.E_corner), fontsize=7, xytext=(3, 3), textcoords='offset points')
ax.set_xlabel('score (0-1)'); ax.set_ylabel('evidence (nats)'); ax.legend(fontsize=8); ax.set_title('vs current grader and simulated detection')
fig.tight_layout(); fig.savefig('pareto.png', dpi=130)
