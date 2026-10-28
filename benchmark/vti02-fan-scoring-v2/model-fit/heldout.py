"""Held-out evaluation of corpus / physical refits / empirical on the partition points -> heldout.csv, heldout_summary.csv."""
import json
import numpy as np, pandas as pd
FLN = 10.3392
P = pd.read_csv('partition_points.csv', dtype={'session': str})
CV = pd.read_csv('fit_curves.csv'); NN = CV.n.values
E = json.load(open('empirical.json')); eb = E[str(E['best'])]
ce, cove = np.array(eb['coef']), np.array(eb['cov'])


def phys(col, side, FL):
    ne = NN > 0
    if side == 'e':
        return np.interp(FL, FLN * NN[ne], CV[col].values[ne], left=np.nan, right=np.nan)
    nh = ~ne
    return np.interp(FL, (FLN * np.abs(NN[nh]))[::-1], CV[col].values[nh][::-1], left=np.nan, right=np.nan)


def emp(side, FL):
    if side != 'e':
        return np.nan, np.nan
    A = np.vander(np.atleast_1d(FL) / 20.0, len(ce))
    return float((A @ ce)[0]), float(np.sqrt(A @ cove @ A.T)[0, 0])


rows = []
for _, r in P.iterrows():
    d = dict(r)
    for m in ('corpus', 'A', 'B', 'C'):
        d[f'p_{m}'] = phys(m, r.side, r.F_L_ref)
    d['p_emp'], d['p_emp_ci'] = emp(r.side, r.F_L_ref)
    rows.append(d)
H = pd.DataFrame(rows)
H['group'] = np.where(H.split == 'train', 'train ' + H.session, np.where(H.side == 'h', 'test hole', 'test e ' + H.session))
H.to_csv('heldout.csv', index=False)
out = []
for gname, g in list(H.groupby('group')) + [('test e (all)', H[(H.split == 'test') & (H.side == 'e')]), ('test all', H[H.split == 'test'])]:
    rec = dict(group=gname, n=len(g), FL=f'{g.F_L_ref.min():.1f}-{g.F_L_ref.max():.1f}', y_mean=g.y.mean())
    for m in ('corpus', 'A', 'B', 'C', 'emp'):
        res = g.y - g[f'p_{m}']
        rec[f'bias_{m}'] = res.mean(); rec[f'rmse_{m}'] = np.sqrt(np.mean(res ** 2))
    out.append(rec)
S = pd.DataFrame(out); S.to_csv('heldout_summary.csv', index=False)
pd.set_option('display.width', 250)
print(S.round(4).to_string())
