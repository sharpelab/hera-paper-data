"""Per-column diagnosis: grader column terms (Halder, 0.75 T clip) vs simulated detection rate (halder tones)."""
import sys, pickle, warnings
warnings.filterwarnings('ignore'); sys.dont_write_bytecode = True
import numpy as np, pandas as pd
import designs as DS
D = pickle.load(open('designs.pkl', 'rb'))
Cc = pd.read_csv('sim_columns.csv.gz')
rows = []
for d in D:
    B = np.unique(d['B']); Bw = B[B >= 0.75]
    W = 1 / Bw[0] - 1 / Bw[-1]; hi = 1 / (3 * np.max(-np.diff(1 / Bw)))
    n = d['n_sim']; fl = DS.halder_fl(n); FL = 10.3392 * n
    ok = ~np.isnan(fl) & (FL <= hi); p = np.where(np.isnan(fl), 0, fl * W)
    # local rows/period of F_L over the window's top half in 1/B (where the light signal lives)
    du = -np.diff(1 / Bw); umid = 0.5 * (1 / Bw[:-1] + 1 / Bw[1:])
    for j in range(n.size):
        rows.append(dict(label=d['label'], j=j, n=n[j], fl=fl[j], p=p[j], FL=FL[j], hi=hi, FL_ok=bool(ok[j]), inband=bool(ok[j] and p[j] >= 3),
                         rpp_worst=1 / (FL[j] * du.max()), rpp_best=1 / (FL[j] * du.min()), W075=W,
                         I=d['I'], tau=d['tau'], nrow075=Bw.size))
G = pd.DataFrame(rows)
C = Cc.copy(); C['det'] = C.light & C.split
C['j'] = C.groupby(['label', 'acq', 'excess', 'seed', 'win']).cumcount()
R = C.groupby(['label', 'j', 'acq', 'excess', 'win']).agg(det=('det', 'mean'), light=('light', 'mean'), split=('split', 'mean'),
                                                          snr_light=('snr_light', 'median'), snr_FL=('snr_FL', 'median')).reset_index()
W = R.pivot_table(index=['label', 'j'], columns=['win', 'acq', 'excess'], values=['det', 'snr_light', 'light', 'split'])
W.columns = ['_'.join([c[0], c[1], c[2], str(int(round(c[3] * 1e9)))]) for c in W.columns]
M = G.set_index(['label', 'j']).join(W).reset_index()
M.to_csv('diag_columns.csv', index=False, float_format='%.4g')

pd.set_option('display.width', 250)
for win in ('clip075', 'own'):
    det = M[f'det_{win}_own_87']; det0 = M[f'det_{win}_own_0']; detr = M[f'det_{win}_ref_87']
    M['cls'] = np.select([M.inband & (det >= 0.5), M.inband & (det < 0.5) & (det0 >= 0.5), M.inband & (det0 < 0.5),
                          ~M.inband & (det >= 0.5) & ~M.FL_ok, ~M.inband & (det >= 0.5) & M.FL_ok],
                         ['agree_pos', 'inband_lost_to_noise', 'inband_undetected_even_noisefree', 'det_but_FL_over_highline', 'det_but_p<k'], 'agree_neg')
    print(f'\n== window {win}: column classes (halder, own acquisition, 87 nV; det = light_true & split in >= 50% of seeds)')
    print(M.groupby(['label', 'cls']).size().unstack(fill_value=0).to_string())
    print(M.cls.value_counts().to_string())
    # detection vs p (k calibration) for FL_ok columns
    b = pd.cut(M.p, [0, 1, 1.5, 2, 2.5, 3, 4, 6, 50])
    print(f'\ndetection rate vs grader p (light periods in 0.75 T window), FL under high line; window {win}')
    print(M[M.FL_ok].groupby(b, observed=True).agg(N=('p', 'size'), det_noisefree=(f'det_{win}_own_0', 'mean'), det_own87=(f'det_{win}_own_87', 'mean'),
          det_ref87=(f'det_{win}_ref_87', 'mean'), light_own87=(f'light_{win}_own_87', 'mean'), split_own87=(f'split_{win}_own_87', 'mean')).round(2).to_string())
    print('FL over high line: N', int((~M.FL_ok).sum()), 'det own87', round(M.loc[~M.FL_ok, f'det_{win}_own_87'].mean(), 2),
          ' noclip87', round(M.loc[~M.FL_ok, f'det_{win}_own_noclip_87'].mean(), 2), ' ref87', round(M.loc[~M.FL_ok, f'det_{win}_ref_87'].mean(), 2))
    print(M[~M.FL_ok].groupby('label').agg(N=('p', 'size'), rpp_worst=('rpp_worst', 'median'), rpp_best=('rpp_best', 'median'), p=('p', 'median'),
          det_own=(f'det_{win}_own_87', 'mean'), det_noclip=(f'det_{win}_own_noclip_87', 'mean'), det_ref=(f'det_{win}_ref_87', 'mean')).round(2).to_string())
