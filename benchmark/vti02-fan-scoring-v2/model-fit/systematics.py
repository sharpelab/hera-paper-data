"""gamma2 systematics for refit B (gamma3 = 0.3): tone subsets, F_L range, 0822 frame choice. -> systematics.csv
Also model masses at the LK points vs measured."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '.')
import swm
FLN = swm.FL_PER_N
P = pd.read_csv('partition_points.csv', dtype={'session': str}); TR = P[P.split == 'train'].copy()
g2s = np.round(np.arange(-0.022, -0.0079, 0.001), 4)
NE = np.linspace(0.95, 3.4, 50)
cvs = {g2: swm.tones_2d(swm.params(g2=g2, g3=0.3), NE) for g2 in g2s}
cvs = {g2: t[:, 0] / t[:, 2] for g2, t in cvs.items()}


def best(D):
    ch = [np.sum(((D.y - np.interp(D.F_L_ref, FLN * NE, cvs[g])) / D.sy) ** 2) for g in g2s]
    i = int(np.argmin(ch)); j = slice(max(i - 3, 0), i + 4)
    a, b, _ = np.polyfit(g2s[j], np.array(ch)[j], 2)
    return -b / (2 * a)


# 0822 frame through the origin (s = 0.8932) instead of the offset fit
alt = TR.copy(); m = alt.session == '0822'
FLo = FLN * 0.8932 * alt.n_frame[m]
alt.loc[m, 'y'] = np.where(alt.tone[m] == 'light', alt.y[m] * alt.F_L_ref[m] / FLo, 1 - (1 - alt.y[m]) * alt.F_L_ref[m] / FLo)
alt.loc[m, 'F_L_ref'] = FLo
V = [('all (baseline)', TR), ('light tone only', TR[TR.tone == 'light']), ('heavy tone only', TR[TR.tone == 'heavy']),
     ('08-25 only', TR[TR.session == '0825']), ('08-22 only', TR[TR.session == '0822']),
     ('F_L >= 18 T', TR[TR.F_L_ref >= 18]), ('F_L < 18 T', TR[TR.F_L_ref < 18]), ('08-22 origin frame 0.893', alt)]
rows = [dict(variant=n, n=len(D), g2=best(D)) for n, D in V]
S = pd.DataFrame(rows); S.to_csv('systematics.csv', index=False); print(S.round(4).to_string())
# masses at the LK points (n_act from the F_L frame): 08-21 n_frame 3.0 x 0.927 = 2.78; 08-22 0.8625 x 3.3 = 2.85
for lab, p in (('corpus', swm.ABAB), ('B', swm.params(g2=-0.0145, g3=0.3))):
    for n in (2.78, 2.85):
        ms = swm.M.bernal_mstar(n * 1e16, 'ABAB', swm.params(g2=p.g2, g3=0.0), 0.0)
        print(lab, n, 'radial (g3=0) masses', [(round(F, 1), round(mm, 4)) for F, mm in ms])
