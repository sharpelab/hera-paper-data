"""Partition residuals (observed - model) on model-fit's full data set (partition_points.csv), frame-free:
y = F_light/F_L_ref (or 1 - F_heavy/F_L_ref) vs model p(|n| = F_L_ref / 10.3392) on the point's side.
Frame of record = model-fit's F_L-tone frame (0825 0.9496; 0822 0.8625 (n_frame + 0.100); 0821 0.927; 0824 / hole: tone sums).
Frame sensitivity: literature frame (0825 0.951, 0822 0.886 x 1.018 = 0.902 through the origin).
Also: masses vs the LK ladders -> eval_partition.csv, eval_summary.csv, eval_masses.csv."""
import json
import numpy as np, pandas as pd
FLN = 10.3392
MF = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/model-fit/'
P = pd.read_csv(MF + 'partition_points.csv', dtype={'session': str})
T = pd.read_csv('tone_table_all.csv')
MODELS = ['corpus', 'B', 'Halder_ABAB', 'Shi_ABAB', 'graphite_eps5.7', 'B_g2lo', 'B_g2hi']
E = json.load(open(MF + 'empirical.json')); ce = np.array(E[str(E['best'])]['coef'])


def pmodel(m, side, FL):
    t = T[(T.model == m) & ((T.n > 0) if side == 'e' else (T.n < 0))]
    a = np.abs(t.n.values); o = np.argsort(a)
    return np.interp(np.asarray(FL) / FLN, a[o], t.frac.values[o], left=np.nan, right=np.nan)


def residuals(P):
    H = P.copy()
    for m in MODELS:
        H['p_' + m] = [float(pmodel(m, s, f)) for s, f in zip(H.side, H.F_L_ref)]
    H['p_emp'] = np.where(H.side == 'e', np.vander(H.F_L_ref.values / 20.0, len(ce)) @ ce, np.nan)
    H['group'] = np.where(H.split == 'train', 'train ' + H.session,
                          np.where(H.side == 'h', 'test hole', 'test e ' + H.session))
    return H


def summarize(H, models):
    out = []
    groups = [(k, g) for k, g in H.groupby('group')] + [('train (all)', H[H.split == 'train']),
                                                        ('test e (all)', H[(H.split == 'test') & (H.side == 'e')])]
    for gname, g in groups:
        rec = dict(group=gname, n=len(g))
        for m in models:
            r = (g.y - g['p_' + m]).dropna()
            rec[m] = f'{r.mean():+.3f} / {np.sqrt((r ** 2).mean()):.3f}' if len(r) else '-'
        out.append(rec)
    return pd.DataFrame(out)


H = residuals(P)
H.to_csv('eval_partition.csv', index=False)
S = summarize(H, MODELS + ['emp'])
S.to_csv('eval_summary.csv', index=False)
pd.set_option('display.width', 250)
print('bias / rmse (observed - model), frame of record'); print(S.to_string(index=False))

# hole points one by one
print('\nhole points'); print(H[H.side == 'h'][['session', 'run', 'col', 'tone', 'F_L_ref', 'y', 'sy'] + ['p_' + m for m in MODELS[:5]]].round(3).to_string(index=False))

# low-F_L end of the training data (where the models differ most)
print('\n08-25 / 08-22 training, binned by F_L_ref: median y and residuals')
tr = H[H.split == 'train'].copy(); tr['bin'] = pd.cut(tr.F_L_ref, [11, 14, 17, 20, 24, 28, 31])
agg = {'y': 'median'}; agg.update({'p_' + m: 'median' for m in MODELS[:5]})
print(tr.groupby('bin', observed=True).agg(N=('y', 'size'), **{k: (k, v) for k, v in agg.items()}).round(3).to_string())

# frame sensitivity: literature frame for 0825 / 0822 training points
F2 = P.copy()
m25 = F2.session == '0825'; m22 = F2.session == '0822'
for msk, s_new in ((m25, lambda nf: FLN * 0.951 * nf), (m22, lambda nf: FLN * 0.902 * nf)):
    old = F2.loc[msk, 'F_L_ref'].values; new = s_new(F2.loc[msk, 'n_frame'].values)
    F2.loc[msk, 'y'] = np.where(F2.loc[msk, 'tone'] == 'light', F2.loc[msk, 'y'] * old / new, 1 - (1 - F2.loc[msk, 'y']) * old / new)
    F2.loc[msk, 'F_L_ref'] = new
H2 = residuals(F2)
S2 = summarize(H2, MODELS[:5])
print('\nframe sensitivity (literature frame on 0825 / 0822):'); print(S2[S2.group.str.startswith('train')].to_string(index=False))
S2.to_csv('eval_summary_litframe.csv', index=False)

# masses
lk = pd.read_csv(MF + 'lk_masses.csv', dtype={'session': str})
rows = []
for m in MODELS[:5]:
    t = T[(T.model == m) & (T.n > 0)]
    for n in (1.5, 2.0, 2.8, 3.0):
        r = t.iloc[(t.n - n).abs().argmin()]
        rows.append(dict(model=m, n=n, m_light=r.m_light, m_heavy=r.m_heavy, ratio=r.m_heavy / r.m_light))
    t = T[(T.model == m) & (T.n < 0)]
    for n in (-0.9, -1.2):
        r = t.iloc[(t.n - n).abs().argmin()]
        rows.append(dict(model=m, n=n, m_light=r.m_light, m_heavy=r.m_heavy, ratio=r.m_heavy / r.m_light))
Mm = pd.DataFrame(rows); Mm.to_csv('eval_masses.csv', index=False)
print('\nmodel masses'); print(Mm.pivot_table(index='n', columns='model', values=['m_light', 'm_heavy', 'ratio']).round(3).T.to_string())
print('\nmeasured LK (model-fit):'); print(lk.round(3).to_string(index=False))
