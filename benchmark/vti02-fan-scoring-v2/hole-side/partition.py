"""Q4: observed hole partition p = 1 - F_heavy / F_L against the Halder_ABAB (and corpus) light fraction.
Frame-free rows use the trace's own F_L-like tone (n = F_L / 10.3392); frame rows use the QH ladder or the grader
frame for F_L.  Writes partition.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from common import model, FLN

D = pd.read_csv('detect_columns.csv'); full = D[D.win == 'full0.76'].set_index('trace')
rows = [  # trace, heavy, F_L, F_L source, heavy source
    ('0822-r7', 6.59, 9.38, 'own tone (sdh_onset 9.36-9.38, onset 1.27 T)', 'low-field heavy (sdh_onset 6.46-6.59; FFT 0.6-2.3 T 6.53)'),
    ('0822-r7', 7.02, 9.38, 'own tone', 'consensus to 4.5 T (6.67-7.42, pulled by the F_L tone)'),
    ('0824-r5-c0', 5.76, 7.51, 'own tone (7.48-7.53, 6/12 choices, contrast 6)', 'consensus 5.20-6.22'),
    ('0824-r5-c0', 6.14, 7.51, 'own tone', 'sdh_onset tone 6.14'),
]
for c in ('0824-r4-c1', '0824-r4-c2', '0824-r4-c3'):
    r = full.loc[c]; rows.append((c, r.Fpk_heavy, r.Fpk_FL, f'own tone, sub-threshold (contrast {r.snr_FL})', 'full window 0.76-6 T'))
out = []
for tr, h, fL, s1, s2 in rows:
    n = fL / FLN
    out.append(dict(trace=tr, basis='frame-free', F_heavy=h, F_L=fL, n_from_FL=round(n, 3), F_L_src=s1, heavy_src=s2, p_obs=round(1 - h / fL, 3),
                    p_Halder=round(model(n)[0] / FLN / n, 3), p_corpus=round(model(n, 'h', 'corpus')[0] / FLN / n, 3)))
for tr, h, n, s1 in [('0825-r7-c0', 6.54, 0.842, 'QH ladder nu 8,7,6'), ('0822-r7', 6.59, 1.011, 'QH ladder nu 7,6,5')] + \
        [(c, full.loc[c].Fpk_heavy, full.loc[c].n_ref, 'grader frame x0.90') for c in ('0824-r4-c0', '0824-r4-c4', '0824-r4-c5', '0824-r4-c6', '0824-r4-c7')]:
    fL = FLN * n
    out.append(dict(trace=tr, basis='frame', F_heavy=h, F_L=round(fL, 2), n_from_FL=n, F_L_src=s1, heavy_src='consensus / full window', p_obs=round(1 - h / fL, 3),
                    p_Halder=round(model(n)[0] / FLN / n, 3), p_corpus=round(model(n, 'h', 'corpus')[0] / FLN / n, 3)))
P = pd.DataFrame(out); P['resid_Halder'] = (P.p_obs - P.p_Halder).round(3); P['resid_corpus'] = (P.p_obs - P.p_corpus).round(3)
P.to_csv('partition.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 40)
print(P[['trace', 'basis', 'F_heavy', 'F_L', 'n_from_FL', 'p_obs', 'p_Halder', 'p_corpus', 'resid_Halder', 'resid_corpus']].to_string(index=False))
ff = P[(P.basis == 'frame-free')]
for nm, sub in (('frame-free, one row per trace (first heavy choice)', ff.drop_duplicates('trace')), ('frame-free, all rows', ff),
                ('frame rows |n| >= 0.6', P[(P.basis == 'frame') & (P.n_from_FL >= 0.6)])):
    print(f"{nm}: N {len(sub)}, Halder bias {sub.resid_Halder.mean():+.3f} rms {np.sqrt((sub.resid_Halder ** 2).mean()):.3f}; corpus bias {sub.resid_corpus.mean():+.3f} rms {np.sqrt((sub.resid_corpus ** 2).mean()):.3f}")
