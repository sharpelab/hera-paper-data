"""Q5: does acquisition matter in simulation? own vs reference acquisition; SNR-factor prediction; per-column SNR ratios."""
import sys, pickle, warnings
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from scipy.stats import spearmanr
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
E = pd.read_csv('sim_episodes.csv'); M = pd.read_csv('diag_columns.csv')
pd.set_option('display.width', 250)
x = E[(E.tone == 'halder') & (E.win == 'clip075')]
t = x.groupby(['label', 'acq', 'excess'])[['a', 'b']].mean().unstack(['acq', 'excess'])
out = []
for lab, d in D.items():
    Bw = d['B'][d['B'] >= 0.75]
    r = dict(label=lab, I_nA=d['I'] * 1e9, tau=d['tau'], fd_tau=d['fd'] / d['tau'], rows075=Bw.size, snr_factor=d['snr'])
    for exc in (55e-9, 87e-9, 165e-9):
        ao, ar = t.loc[lab, ('a', 'own', exc)], t.loc[lab, ('a', 'ref', exc)]
        bo, br = t.loc[lab, ('b', 'own', exc)], t.loc[lab, ('b', 'ref', exc)]
        r[f'a_own_{round(exc*1e9)}'] = ao; r[f'a_ref_{round(exc*1e9)}'] = ar
        r[f'b_own_{round(exc*1e9)}'] = bo; r[f'b_ref_{round(exc*1e9)}'] = br
        r[f'ratio_a_{round(exc*1e9)}'] = ao / ar if ar > 0 else np.nan
        r[f'ratio_b_{round(exc*1e9)}'] = bo / br if br > 0 else np.nan
    m = M[(M.label == lab) & M.inband]
    q = m['snr_light_clip075_own_87'] / m['snr_light_clip075_ref_87']
    r['colsnr_ratio_med'] = q.median() if len(q) else np.nan
    q0 = m['snr_light_clip075_own_0'] / m['snr_light_clip075_ref_0']
    r['colsnr_ratio_noisefree'] = q0.median() if len(q0) else np.nan
    out.append(r)
T = pd.DataFrame(out).set_index('label')
T.to_csv('acquisition_effect.csv', float_format='%.3f')
cols = ['I_nA', 'tau', 'fd_tau', 'rows075', 'snr_factor', 'a_own_87', 'a_ref_87', 'ratio_a_55', 'ratio_a_87', 'ratio_a_165', 'b_own_87', 'b_ref_87', 'ratio_b_87', 'ratio_b_165', 'colsnr_ratio_med']
print(T[cols].round(2).to_string())
v = T[T.a_ref_87 > 0]
print('\nmean ratio_a  55/87/165:', [round(v[f'ratio_a_{e}'].mean(), 2) for e in (55, 87, 165)], ' median col SNR ratio', round(v.colsnr_ratio_med.median(), 2),
      ' predicted (SNR factor) mean', round(v.snr_factor.mean(), 3))
tot = {e: (T[f'a_own_{e}'].sum(), T[f'a_ref_{e}'].sum(), T[f'b_own_{e}'].sum(), T[f'b_ref_{e}'].sum()) for e in (55, 87, 165)}
print('pooled a own/ref, b own/ref:', {e: (round(v[0] / v[1], 2), round(v[2] / v[3], 2)) for e, v in tot.items()})
# does rows in window explain the loss among I=10 nA tau=0.3 designs?
w = v[(v.I_nA < 20) & (v.tau == 0.3)]
print('10 nA tau 0.3 designs: spearman(ratio_a_87, rows075) =', round(spearmanr(w.ratio_a_87, w.rows075)[0], 2), 'n=', len(w))
