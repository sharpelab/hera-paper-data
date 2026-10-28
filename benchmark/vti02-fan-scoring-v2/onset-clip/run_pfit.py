import warnings, pickle, csv, numpy as np, sys
from common import *
from pfit import fit
warnings.filterwarnings('ignore')
exec(open('measure.py').read().split('out, tracks')[0].split('from common import *')[1])   # reuse the record list
Te_list = (1.2, 4.0)
out, fits = [], {}
env = {(r['rec'], int(r['col']), r['tone']): r for r in csv.DictReader(open('envelopes.csv'))}
for rec, j, n, B, R, I, tau in recs:
    if rec == '0821-r8': continue
    ex = tones_expected(n)
    F0 = [float(env[(rec, j, t)]['F']) for t in ('light', 'heavy', 'FL')]
    F0 = F0 + [2 * F0[0], F0[1] - F0[0]]
    ml, mh = mass(n, 'm_l'), mass(n, 'm_h'); m = [ml, mh, ml + mh, 2 * ml, mh + ml]   # diff-orbit mass m_h + m_l (combination)
    # low edge: record min, but light tone needs >= 2.5 pts/period at the local step
    Bs = np.sort(np.unique(B)); dB = np.gradient(Bs); ppp = Bs ** 2 / (F0[0] * dB)
    b_lo = max(Bs.min(), Bs[ppp >= 2.5].min() if (ppp >= 2.5).any() else Bs.max())
    if rec == '0822-r6': b_lo = max(b_lo, 1.0)   # 50 mT steps below 1 T
    for Te in Te_list:
        try: f = fit(B, R, F0, m, Te=Te, b_lo=b_lo, b_hi=4.0)
        except Exception as e: print(rec, j, e); continue
        row = dict(rec=rec, col=j, n=round(n, 3), I_nA=round(I, 1), tau=tau, Te=Te, b_lo=round(b_lo, 3), npts=f['npts'], rms=round(f['rms'], 3))
        for k, t in enumerate(('light', 'heavy', 'FL', 'light2', 'diff')):
            row[f'F_{t}'] = round(f['F'][k], 2); row[f's_{t}'] = round(f['s'][k], 3); row[f'sse_{t}'] = round(f['s_se'][k], 3)
            row[f'A0_{t}'] = round(f['amp0'][k], 3); row[f'm_{t}'] = round(m[k], 4)
        row['u0'] = round(f['u0'], 4)
        out.append(row); fits[(rec, j, Te)] = f
with open('pfit.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, list(out[0].keys())); w.writeheader(); [w.writerow(r) for r in out]
pickle.dump(fits, open('pfit.pkl', 'wb')); print(len(out))
