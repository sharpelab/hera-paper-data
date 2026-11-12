import csv, numpy as np, collections
from common import ALPHA
rows = list(csv.DictReader(open('pfit.csv')))
g = collections.defaultdict(list)
for r in rows: g[(r['rec'], r['Te'])].append(r)
for (rec, Te), L in g.items():
    print(f"== {rec} Te={Te}  ncol={len(L)}  b_lo={L[0]['b_lo']} I={L[0]['I_nA']} tau={L[0]['tau']}")
    for t in ('light', 'heavy', 'FL'):
        s = np.array([float(r[f's_{t}']) for r in L]); se = np.array([float(r[f'sse_{t}']) for r in L]); m = np.array([float(r[f'm_{t}']) for r in L])
        TD = -s / (ALPHA * m); TDse = se / (ALPHA * m)
        ok = np.isfinite(se) & (se < 1.0) & (np.array([float(r[f'A0_{t}']) for r in L]) > 0)
        if ok.sum() == 0: print('   ', t, 'no good fits'); continue
        w = 1 / TDse[ok] ** 2; mean = (TD[ok] * w).sum() / w.sum()
        print(f"   {t:6s} good {ok.sum():3d}  s med {np.median(s[ok]):6.2f}  T_D med {np.median(TD[ok]):5.2f} IQR [{np.percentile(TD[ok],25):.2f},{np.percentile(TD[ok],75):.2f}]  wmean {mean:.2f}  med se {np.median(TDse[ok]):.2f}")
    sl = np.array([float(r['s_light']) for r in L]); sh = np.array([float(r['s_heavy']) for r in L])
    sel = np.array([float(r['sse_light']) < 0.5 and float(r['sse_heavy']) < 0.5 for r in L])
    ml = np.array([float(r['m_light']) for r in L]); mh = np.array([float(r['m_heavy']) for r in L])
    if sel.any(): print(f"   slope ratio light/heavy med {np.median(sl[sel]/sh[sel]):.2f} IQR [{np.percentile(sl[sel]/sh[sel],25):.2f},{np.percentile(sl[sel]/sh[sel],75):.2f}] (n={sel.sum()}); model m ratio {np.median(ml/mh):.2f}")
