"""Consolidated per-column tone table -> vti02_tones.csv (every run, both sides; blanks = not detected / not usable)."""
import numpy as np, pandas as pd
FLN = 10.3392
C = pd.read_csv('columns_tones.csv', dtype={'session': str})
FR = {'0825': (0.9496, 0.0, 'F_L-tone fit, origin (08-25 r7+r8)'), '0822': (0.8625, -0.100, 'F_L-tone fit with offset (08-22 r6+r8)'),
      '0821': (0.927, 0.0, 'F_L-tone fit, origin (08-21 r5+r8)'), '0824': (0.85, 0.0, 'Luttinger sums r4 c37 / r5 c3 (0.837, 0.860)')}
CASES = {'0821': 0.92, '0822': 0.886, '0824': 0.90, '0825': 1.0}
lk = pd.read_csv('lk_masses.csv', dtype={'session': str})
out = C.copy()
out['n_scale'] = out.session.map(lambda s: FR[s][0]); out['n0_frame'] = out.session.map(lambda s: FR[s][1])
out['n_scale_src'] = out.session.map(lambda s: FR[s][2]); out['n_scale_cases_toml'] = out.session.map(CASES)
out['n_actual'] = out.n_scale * (out.n_frame - out.n0_frame)
for t in ('light', 'heavy', 'F_L'):
    out[f'mstar_{t}'] = np.nan
for _, r in lk.iterrows():
    m = (out.session == r.session) & (out.kind == 'lk')
    out.loc[m, f'mstar_{r.tone}'] = r.m_med
keep = ['session', 'run', 'col', 'kind', 'T_K', 'n_frame', 'n_scale', 'n0_frame', 'n_scale_src', 'n_scale_cases_toml', 'n_actual',
        'dF', 'F_L', 'sig_L', 'rec_L', 'F_light', 'sig_light', 'rec_light', 'F_heavy', 'sig_heavy', 'rec_heavy',
        'mstar_light', 'mstar_heavy', 'mstar_F_L']
out[keep].round(4).to_csv('vti02_tones.csv', index=False)
print(len(out), 'rows')
