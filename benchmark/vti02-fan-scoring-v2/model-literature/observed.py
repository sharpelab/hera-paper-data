"""Observed vti-02 light fraction (read from live-check/fft_columns_eval.csv), in the F_L-pinned density frame.
n_true = n_act * s_fan, s_fan = median(Fpk_FL / F_L) over the fan (0825: 0.951, 0822: 1.018)."""
import pandas as pd, numpy as np
A = pd.read_csv('../live-check/fft_columns_eval.csv')
out = []
for fan, win in (('0825-r8', 'full1.0'), ('0822-r8', 'full1.0')):
    r = A[(A.fan == fan) & (A.win == win)].copy()
    s = (r.Fpk_FL / r.F_L).median()
    r['scale'] = s
    r['n_true'] = r.n_act * s
    r['frac_light'] = np.where(r.det_light, r.Fpk_light / r.Fpk_FL, np.nan)
    r['frac_1mheavy'] = np.where(r.split_heavy_FL, 1 - r.Fpk_heavy / r.Fpk_FL, np.nan)
    r['periods_light'] = r.Fpk_light * (1 / 1.0 - 1 / (8.0 if fan == '0825-r8' else 10.0))
    out.append(r[['fan', 'win', 'col', 'n_act', 'scale', 'n_true', 'Fpk_light', 'Fpk_heavy', 'Fpk_FL', 'dF',
                  'snr_light', 'frac_light', 'frac_1mheavy', 'periods_light']])
O = pd.concat(out)
O.to_csv('observed_fraction.csv', index=False, float_format='%.4f')
O['nb'] = pd.cut(O.n_true, np.arange(1.1, 3.31, 0.3))
print(O.groupby('nb', observed=True).agg(n=('n_true', 'mean'), fl=('frac_light', 'median'), fh=('frac_1mheavy', 'median'),
      sd_fl=('frac_light', 'std'), N=('col', 'size')).round(3).to_string())
g = O.dropna(subset=['frac_light'])
print('fit frac_light vs n_true (all, both fans):', np.round(np.polyfit(g.n_true, g.frac_light, 1), 4))
g2 = g[g.n_true >= 1.5]
print('fit n_true>=1.5:', np.round(np.polyfit(g2.n_true, g2.frac_light, 1), 4))
