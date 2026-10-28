"""Injection-recovery of the light-tone Dingle slope: take each 0825-r8 / 0822-r8 column's fit (T_e 1.2), rebuild the
data as model-with-light-slope-replaced + the column's own residual, refit, compare."""
import pickle, csv, numpy as np, warnings
from pfit import fit, design
warnings.filterwarnings('ignore')
fits = pickle.load(open('pfit.pkl', 'rb'))
rows = {(r['rec'], int(r['col']), float(r['Te'])): r for r in csv.DictReader(open('pfit.csv'))}
res = []
for (rec, j, Te), f in fits.items():
    if Te != 1.2 or rec not in ('0825-r8', '0822-r8') or j % 3: continue
    r = rows[(rec, j, Te)]
    m = [float(r[f'm_{t}']) for t in ('light', 'heavy', 'FL', 'light2', 'diff')]
    u = f['u']; resid = f['y'] - f['yfit']
    for s_inj in (-1.06, -2.5):
        s = f['s'].copy(); s[0] = s_inj; s[3] = 2 * s_inj
        A = design(u, f['F'], s, m, Te, f['u0']); y = A @ f['coef'] + resid
        B = 1 / u
        g = fit(B, y, list(f['F']), m, Te=Te, b_lo=B.min() - 1e-9, b_hi=B.max() + 1e-9)
        res.append((rec, j, s_inj, g['s'][0], g['s_se'][0], f['amp0'][0]))
res = np.array([(x[2], x[3], x[4]) for x in res])
for s_inj in (-1.06, -2.5):
    k = res[:, 0] == s_inj; d = res[k, 1]
    print(f"inject s_light = {s_inj}: recovered median {np.median(d):.2f}  IQR [{np.percentile(d,25):.2f}, {np.percentile(d,75):.2f}]  n={k.sum()}  med se {np.median(res[k,2]):.2f}")
