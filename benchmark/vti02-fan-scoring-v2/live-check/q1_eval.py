"""Q1 evaluation: reference light-tone curve from 0825 full window; truth-checked detections; k-binned detection rates; metric comparison."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, '.')
from load import f_light, f_L
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500)
A = pd.read_csv('fft_columns.csv')
ref = A[(A.fan == '0825-r8') & (A.win == 'full1.0') & A.det_light]
rfit = np.polyfit(ref.n_act, ref.Fpk_light / ref.Fpk_FL, 1)
print('reference light fraction r(n) = F_light_obs / F_L_obs = %.4f n + %.4f' % tuple(rfit), ' (model fraction at n=1.5/2.0/3.0: %.3f/%.3f/%.3f; obs %.3f/%.3f/%.3f)' % (
    f_light(1.5)/f_L(1.5), f_light(2.0)/f_L(2.0), f_light(3.0)/f_L(3.0), *np.polyval(rfit, [1.5, 2.0, 3.0])))
A['F_light_ref'] = np.polyval(rfit, A.n_act) * A.F_L
span = 1 / A.dF
A['k_light_ref'] = A.F_light_ref * span
A['k_light_mod'] = A.F_light_mod * span
tol = np.maximum(0.5 * A.dF, 0.75)
A['light_true'] = (A.snr_light >= 4) & ((A.Fpk_light - A.F_light_ref).abs() <= tol)
# heavy/F_L split: both peaks, each within tolerance of its reference (heavy_ref = F_L_obs - light_ref)
A['FL_obs_ref'] = 0.95 * A.F_L if False else A.F_L
A['split_true'] = A.split_heavy_FL & ((A.Fpk_FL - A.Fpk_heavy) >= 0.5 * A.dF)
A.to_csv('fft_columns_eval.csv', index=False)
main = A[A.win.isin(['o2.0', 'o1.53', 'full1.0', 'full0.75', 'ana1-6'])]
print('\nPer fan/window: columns; light detections raw vs truth-checked; heavy|F_L split; metric predictions (k by model F_light, rows/period >= 3)')
g = main.groupby(['fan', 'win'], sort=False)
T = g.agg(cols=('col', 'size'), dF=('dF', 'first'), rpp_min=('rpp_FL', 'min'), light_raw=('det_light', 'sum'), light_true=('light_true', 'sum'),
          FL=('det_FL', 'sum'), split=('split_true', 'sum'),
          k1_mod=('k_light_mod', lambda s: int((s >= 1).sum())), k2_mod=('k_light_mod', lambda s: int((s >= 2).sum())),
          k1_ref=('k_light_ref', lambda s: int((s >= 1).sum())), k2_ref=('k_light_ref', lambda s: int((s >= 2).sum())))
print(T.to_string())
# confusion: metric (k>=K by model) vs light_true, per window
print('\nConfusion metric(model k>=K) vs light_true; and vs split_true')
rows = []
for (fan, win), a in main.groupby(['fan', 'win'], sort=False):
    for K in (1, 2):
        p = a.k_light_mod >= K
        for tgt in ('light_true', 'split_true'):
            t = a[tgt]
            rows.append(dict(fan=fan, win=win, K=K, target=tgt, TP=int((p & t).sum()), FP=int((p & ~t).sum()), FN=int((~p & t).sum()), TN=int((~p & ~t).sum())))
print(pd.DataFrame(rows).to_string())
# k-binned detection rate, all windows incl sub-windows, uniform-1/B fans with rows/period >= 3 (exclude 0824)
B = A[(A.fan != '0824-r4')].copy()
bins = [0, 0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 8.0]
B['kbin'] = pd.cut(B.k_light_ref, bins)
print('\nDetection vs periods of the (observed-curve) light tone in the window, 0821/0822/0825 all windows:')
print(B.groupby('kbin', observed=True).agg(N=('col', 'size'), light_true=('light_true', 'mean'), split=('split_true', 'mean'), FL=('det_FL', 'mean'),
      med_snr_light=('snr_light', 'median')).round(2).to_string())
B['kbin_mod'] = pd.cut(B.k_light_mod, bins)
print('\nSame, binned by MODEL k (what the metric computes):')
print(B.groupby('kbin_mod', observed=True).agg(N=('col', 'size'), light_true=('light_true', 'mean'), split=('split_true', 'mean')).round(2).to_string())
for fan in ['0821-r8', '0822-r8', '0825-r8']:
    b = B[(B.fan == fan) & ~B.win.str.startswith('sub')]
    print(fan, 'by k_ref bin, light_true rate:', b.groupby('kbin', observed=True).light_true.agg(['size', 'mean']).round(2).to_dict('index'))
