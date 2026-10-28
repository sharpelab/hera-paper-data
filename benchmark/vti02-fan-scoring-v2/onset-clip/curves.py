"""B_on,low(n) under each candidate, per column, + linear-in-n fits used by the rescore."""
import json, csv, numpy as np
from common import mass
from pfit import RT
O = json.load(open('predict.json'))
P = {(r['rec'], int(r['col'])): r for r in csv.DictReader(open('pfit.csv')) if r['Te'] == '1.2'}
E = {(r['rec'], int(r['col']), r['tone']): r for r in csv.DictReader(open('envelopes.csv'))}
f = float
def onset_shift(B_on, s, k):  # SNR multiplied by k: u_on -> u_on + ln(k)/|s|
    return 1 / (1 / B_on + np.log(k) / abs(s))
rows = []
for o in O:
    if 'light_own' not in o or o['n'] < 1.8: continue
    rec, j, n = o['rec'], o['col'], o['n']
    ratio = mass(n, 'm_l') / mass(n, 'm_h')
    # heavy onset: tracker where uncensored, else the envelope prediction at own settings
    h_trk = o.get('heavy_trk'); hc = o.get('heavy_trk_cens') == 'True'
    Bh = h_trk if (h_trk and not hc and np.isfinite(h_trk)) else o.get('heavy_own', np.nan)
    sl = o['s_light']
    r = dict(rec=rec, n=n, Bh=Bh, a_model=Bh * ratio, a_meas_lo=Bh * 0.49, a_meas_hi=Bh * 0.70, b_own=o['light_own'], s_light=sl)
    if rec == '0825-r8':
        sig_op = f(E[(rec, j, 'heavy')]['sigma']); sig_w = 0.41
        r['b_ref_op'] = o['light_own']
        r['b_ref_white'] = onset_shift(o['light_own'], sl, sig_op / sig_w)
        # operational sigma model sigma^2 = floor^2 + white^2, floor from the 0825 record, white 40 nV/rtHz
        for lab, I, tau in (('b_10_0.3', 10, 0.3), ('b_10_0.1', 10, 0.1)):
            w = 40e-9 * np.sqrt(5 / (64 * tau)) / (I * 1e-9); fl = np.sqrt(max(sig_op ** 2 - sig_w ** 2, 0))
            r[lab] = onset_shift(o['light_own'], sl, sig_op / np.sqrt(fl ** 2 + w ** 2))
    rows.append(r)
json.dump(rows, open('curves.json', 'w'), indent=0, default=float)
fits = {}
for rec in ('0825-r8', '0822-r8'):
    L = [r for r in rows if r['rec'] == rec]
    print(f"== {rec}: N={len(L)} columns, n {min(r['n'] for r in L):.2f}-{max(r['n'] for r in L):.2f}")
    for k in ('Bh', 'a_model', 'a_meas_lo', 'a_meas_hi', 'b_own', 'b_ref_op', 'b_ref_white', 'b_10_0.3', 'b_10_0.1'):
        v = np.array([r[k] for r in L if k in r and np.isfinite(r[k])]); nn = np.array([r['n'] for r in L if k in r and np.isfinite(r[k])])
        if not v.size: continue
        p = np.polyfit(nn, v, 1); fits[f'{rec}:{k}'] = list(p)
        print(f"  {k:12s} median {np.median(v):.2f} IQR [{np.percentile(v,25):.2f},{np.percentile(v,75):.2f}]  lin fit B = {p[1]:.2f} + {p[0]:+.3f} n  (at n=2: {np.polyval(p,2):.2f}, n=3: {np.polyval(p,3):.2f})")
json.dump(fits, open('curve_fits.json', 'w'), indent=1)
