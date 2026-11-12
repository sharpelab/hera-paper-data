"""Q6: hole-side light-tone and F_L/heavy-split detection vs light-tone periods in the window, by the live-check
rules (fft_q1.analyse + q1_eval) with hole bands.  Periods k = F_light(model, n_ref) x 1/B span.
Bands (fractions of model F_L): light [0.08, 0.45] and >= 0.75 dF, heavy [0.55, 0.895], F_L [0.925, 1.08].
Floor: median |S| over [1.12 F_L, 0.95 Nyquist] (widened to 4 T, as tones.py).  light_true: contrast >= 4 and within
max(0.5 dF, 0.75 T) of the model light tone.  split_true: heavy and F_L both >= 4, a dip < 0.8 between them, and
F_L - heavy >= 0.5 dF.  Writes detect_columns.csv; prints rates by k bin beside the electron curve."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model, band_peak
from tones import n_ref, floor_of

WIN = {'0824-r4': [('full0.76', 0.76, 6.1), ('o1.0', 1.0, 6.1), ('o1.53', 1.53, 6.1), ('o2.0', 2.0, 6.1), ('sub0.76-2', 0.76, 2.0), ('sub0.76-3', 0.76, 3.0)],
       '0824-r5': [('full0.51', 0.51, 6.1), ('o0.76', 0.76, 6.1), ('o1.0', 1.0, 6.1), ('o1.53', 1.53, 6.1), ('o2.0', 2.0, 6.1), ('sub0.51-2', 0.51, 2.0), ('sub0.76-3', 0.76, 3.0)],
       '0825-r7': [('full1.5', 1.5, 6.0), ('o2.0', 2.0, 6.0)],
       '0822-r7': [('b0.76-4.5', 0.76, 4.5), ('b1.0-4.5', 1.0, 4.5), ('b1.53-4.5', 1.53, 4.5), ('b0.6-3', 0.6, 3.0), ('b0.76-2', 0.76, 2.0), ('full0.76-10', 0.76, 10.0), ('o1.0-10', 1.0, 10.0)]}
ELECTRON = {'(1.5, 2.0]': 0.29, '(2.0, 2.5]': 0.43, '(2.5, 3.5]': 0.70, '(3.5, 8.0]': 0.88}   # live-check split rates (grader doc)

if __name__ == '__main__':
    rows = []
    for t in load_all(include_ramp=False):
        key = t['id'].rsplit('-c', 1)[0] if t['session'] != '0822' else t['id']
        n, src = n_ref(t)
        if n < 0.3:
            continue
        fl, fh, fL = model(n); fl = 0.0 if np.isnan(fl) else fl
        for tag, lo, hi in WIN[key]:
            s = spec(t['B'], t['R'], max(lo, t['B'].min()), min(hi, t['B'].max()), 5 if True else 3, Fmax=45, dFgrid=0.01)
            if s is None or s['rows'] < 12:
                continue
            fl0, _ = floor_of(s, fL); Z = s['S'] / fl0; F = s['F']
            pl = band_peak(F, Z, max(0.08 * fL, 0.75 * s['dF']), 0.45 * fL)
            ph = band_peak(F, Z, 0.55 * fL, 0.895 * fL)
            pL = band_peak(F, Z, 0.925 * fL, 1.08 * fL)
            dip = np.nan
            if np.isfinite(ph[0]) and np.isfinite(pL[0]):
                k = (F > ph[0]) & (F < pL[0]); dip = Z[k].min() / min(ph[1], pL[1]) if k.any() else 1.0
            span = 1 / s['lo'] - 1 / s['hi']
            rows.append(dict(trace=t['id'], win=tag, lo=round(s['lo'], 2), hi=round(s['hi'], 2), rows=s['rows'], n_ref=round(n, 3), I_nA=round(t['I_nA'], 1), tau_s=t['tau_s'],
                             F_light_mod=round(fl, 2), F_heavy_mod=round(fh, 2), F_L=round(fL, 2), dF=round(s['dF'], 3), nyq=round(s['nyq'], 1),
                             k_light=round(fl * span, 2), Fpk_light=round(pl[0], 2), snr_light=round(pl[1], 1), Fpk_heavy=round(ph[0], 2), snr_heavy=round(ph[1], 1),
                             Fpk_FL=round(pL[0], 2), snr_FL=round(pL[1], 1), dip=round(dip, 2) if np.isfinite(dip) else np.nan))
    A = pd.DataFrame(rows)
    A['light_true'] = (A.snr_light >= 4) & ((A.Fpk_light - A.F_light_mod).abs() <= np.maximum(0.5 * A.dF, 0.75))
    A['det_heavy'] = A.snr_heavy >= 4
    A['det_FL'] = A.snr_FL >= 4
    A['split_true'] = A.det_heavy & A.det_FL & (A.dip < 0.8) & ((A.Fpk_FL - A.Fpk_heavy) >= 0.5 * A.dF)
    A.to_csv('detect_columns.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
    bins = [0, 1.0, 1.5, 2.0, 2.5, 3.5, 8.0]
    A['kbin'] = pd.cut(A.k_light, bins).astype(str)
    use = A[A.n_ref >= 0.5]
    print('hole column-windows with |n| >= 0.5 (light pocket occupied in the model):', len(use))
    T = use.groupby('kbin', observed=True).agg(N=('trace', 'size'), light=('light_true', 'mean'), heavy=('det_heavy', 'mean'), FL=('det_FL', 'mean'),
                                               split=('split_true', 'mean'), med_snr_heavy=('snr_heavy', 'median'), med_snr_FL=('snr_FL', 'median'), med_snr_light=('snr_light', 'median')).round(2)
    T['electron_split'] = [ELECTRON.get(i, np.nan) for i in T.index]
    print(T.to_string())
    print(use.groupby('trace').agg(N=('win', 'size'), light=('light_true', 'sum'), heavy=('det_heavy', 'sum'), FL=('det_FL', 'sum'), split=('split_true', 'sum')).to_string())
    print(A[A.trace.isin(['0822-r7', '0824-r5-c0', '0825-r7-c0'])][['trace', 'win', 'n_ref', 'dF', 'k_light', 'Fpk_light', 'snr_light', 'Fpk_heavy', 'snr_heavy', 'Fpk_FL', 'snr_FL', 'dip', 'light_true', 'split_true']].to_string(index=False))
    print(A[A.trace.str.startswith('0824-r4') & (A.win == 'full0.76')][['trace', 'n_ref', 'k_light', 'F_light_mod', 'Fpk_light', 'snr_light', 'F_heavy_mod', 'Fpk_heavy', 'snr_heavy', 'F_L', 'Fpk_FL', 'snr_FL', 'dip', 'light_true', 'split_true']].to_string(index=False))
