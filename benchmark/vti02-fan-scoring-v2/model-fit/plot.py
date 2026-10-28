"""Diagnostic figure: partition vs F_L (data by session/tone, corpus, refit B, refit C, empirical band)."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
FLN = 10.3392
P = pd.read_csv('partition_points.csv', dtype={'session': str}); CV = pd.read_csv('fit_curves.csv')
E = json.load(open('empirical.json')); eb = E[str(E['best'])]; c, cov = np.array(eb['coef']), np.array(eb['cov'])
fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw=dict(width_ratios=[2.2, 1]))
col = {'0825': '#2a78d6', '0822': '#eb6834', '0821': '#1baf7a', '0824': '#e87ba4'}
for ax, side in zip(axs, ('e', 'h')):
    ne = CV.n > 0 if side == 'e' else CV.n < 0
    x = FLN * np.abs(CV.n[ne])
    for m, st, lab in (('corpus', '--', 'corpus (γ2 −0.020, γ3 0)'), ('B', '-', 'refit B (γ2 −0.0145, γ3 0.3)'), ('C', ':', 'refit C (γ2 −0.016, Δ′ 0, γ3 0.3)')):
        ax.plot(x, CV[m][ne], st, color='#444', lw=1.6 if m == 'B' else 1.2, label=lab)
    if side == 'e':
        F = np.linspace(10, 34, 100); A = np.vander(F / 20, len(c)); y = A @ c; s = np.sqrt(np.einsum('ij,jk,ik->i', A, cov, A))
        ax.fill_between(F, y - 1.96 * s, y + 1.96 * s, color='#bbb', alpha=0.5, lw=0, label='empirical linear, 95 % CI')
    D = P[P.side == side]
    for (sess, tone), g in D.groupby(['session', 'tone']):
        ax.errorbar(g.F_L_ref, g.y, yerr=g.sy, fmt='o' if tone == 'light' else ('s' if tone == 'heavy' else 'D'), ms=4,
                    mfc='white' if tone == 'heavy' else col[sess], mec=col[sess], ecolor=col[sess], elinewidth=0.6, lw=0,
                    label=f'{sess} {"from " + tone if tone != "sum" else "light/(light+heavy)"}' + (' (test)' if g.split.iloc[0] == 'test' else ''))
    ax.set_xlabel('F_L reference (T)'); ax.set_title('electron side' if side == 'e' else 'hole side (all held out)', fontsize=10)
    ax.grid(alpha=0.25)
axs[0].set_ylabel('light partition  F_light / F_L'); axs[0].legend(fontsize=7, ncol=2, loc='lower right')
axs[1].legend(fontsize=6, loc='upper left'); axs[0].set_ylim(0.05, 0.33); axs[1].set_ylim(0.05, 0.5)
fig.tight_layout(); fig.savefig('partition_vs_FL.png', dpi=120)
