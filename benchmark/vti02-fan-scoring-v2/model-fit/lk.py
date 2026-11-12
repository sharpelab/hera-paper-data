"""LK masses from the ladder rungs (08-21 runs 5 [base] + 10-15; 08-22 runs 9-14), same extraction choices as the
tones. A(T) = A0 X/sinh X, X = 14.69 m* T / B_eff, B_eff = 2/(1/lo + 1/hi); heated rungs only (T > 3 K; base T_e
uncertain on this rig). Per tone: median and spread of m* over window x degree choices. -> lk_masses.csv"""
import numpy as np, pandas as pd
from scipy.optimize import curve_fit
raw = pd.read_csv('columns_raw.csv', dtype={'session': str})
L = raw[(raw.kind == 'lk') | ((raw.session == '0821') & (raw.run == 5))]
rows = []
for sess, g in L.groupby('session'):
    for (lo, hi, deg), h in g.groupby(['lo', 'hi', 'deg']):
        h = h[h.T_K > 3.0].sort_values('T_K')
        if len(h) < 4:
            continue
        Beff = 2 / (1 / lo + 1 / hi)
        for tone, A in (('light', 'A_light'), ('heavy', 'A_heavy'), ('F_L', 'A_L')):
            T = h.T_K.values; y = h[A].values
            f = lambda T, A0, m: A0 * (14.69 * m * T / Beff) / np.sinh(14.69 * m * T / Beff)
            try:
                p, cov = curve_fit(f, T, y, p0=(y[0] * 1.5, 0.05), bounds=([0, 0.003], [np.inf, 0.5]))
                rows.append(dict(session=sess, lo=lo, hi=hi, deg=deg, B_eff=Beff, tone=tone, m=p[1], sig=np.sqrt(cov[1, 1]),
                                 F_med=h['F_' + tone if tone != 'F_L' else 'F_L'].median()))
            except Exception:
                pass
R = pd.DataFrame(rows); R.to_csv('lk_fits_raw.csv', index=False)
S = R.groupby(['session', 'tone']).agg(n=('m', 'size'), m_med=('m', 'median'), m_min=('m', 'min'), m_max=('m', 'max'),
                                       sig_fit=('sig', 'median'), F=('F_med', 'median')).reset_index()
S.to_csv('lk_masses.csv', index=False)
print(S.round(4).to_string())
