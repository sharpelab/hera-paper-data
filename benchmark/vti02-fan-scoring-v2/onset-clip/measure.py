"""Per column, per tone (light, heavy, F_L): fixed-frequency matched-filter envelope + onset (sdh_onset tracker),
and Dingle fits at T_e = 1.2 K and 4 K with model masses. Writes envelopes.csv + tracks.npz."""
import warnings, numpy as np, csv, pickle
from common import *
warnings.filterwarnings('ignore')
recs = []   # (rec, col, n, B, R, I_nA, tau)
for nm, lo_n in (('0825-r8', 0.0), ('0822-r8', 0.0), ('0824-r4', 0.8), ('0821-r8', 0.0)):
    d = load_fan(nm); tau = d['lk']['sr1']['time_constant']; I = float(np.median(np.abs(d['I']))) * 1e9
    for j in range(d['nfast']):
        if d['n'][j] >= lo_n: recs.append((nm, j, float(d['n'][j]), d['B'], d['R'][:, j], I, tau))
# 1D / 5-column spots
r = load_run(21, 5); recs.append(('0821-r5', 0, 2.77, r['B'], r['R'], float(np.median(np.abs(r['I'])))*1e9, r['tau']))
r = load_run(22, 6); recs.append(('0822-r6', 0, 0.886 * 3.2, r['B'], r['R'], float(np.median(np.abs(r['I'])))*1e9, r['tau']))
r = load_run(24, 5); nf = 5; nr = r['B'].size // nf
for j in range(nf):
    tg = r['tg'].reshape(nr, nf)[0, j]; n = 0.90 * (-1.04 + (tg + 0.30) / 0.90 * 3.14)
    if n > 0.8: recs.append(('0824-r5', j, round(n, 3), r['B'].reshape(nr, nf)[:, j], r['R'].reshape(nr, nf)[:, j], float(np.median(np.abs(r['I'])))*1e9, r['tau']))
r = load_run(25, 7); nr = r['B'].size // nf
for j in range(nf):
    tg = r['tg'].reshape(nr, nf)[0, j]; n = 3.14 * tg - 0.032
    if n > 0.8: recs.append(('0825-r7', j, round(n, 3), r['B'].reshape(nr, nf)[:, j], r['R'].reshape(nr, nf)[:, j], float(np.median(np.abs(r['I'])))*1e9, r['tau']))
out, tracks = [], {}
for rec, j, n, B, R, I, tau in recs:
    ex = tones_expected(n); FL = ex['FL']
    mm = dict(light=mass(n, 'm_l'), heavy=mass(n, 'm_h')); mm['FL'] = mm['light'] + mm['heavy']
    for tone, tol in (('light', max(0.25 * ex['light'], 1.0)), ('heavy', 0.06 * FL), ('FL', 0.06 * FL)):
        F, con = refine_freq(B, R, ex[tone], tol, b_lo=max(1.0, B.min()), b_hi=min(8.0, B.max()))
        tr = envelope(B, R, F, b_lo=0.3, b_hi=8.0)
        row = dict(rec=rec, col=j, n=round(n, 3), I_nA=round(I, 1), tau=tau, tone=tone, F=round(F, 2), F_exp=round(ex[tone], 2),
                   fft_contrast=round(con, 1), m_model=round(mm[tone], 4))
        if tr is None or 'err' in tr:
            row['err'] = 'short' if tr is None else tr['err'][:50]; out.append(row); continue
        row.update(onset_b=round(tr['onset_b'], 3), censored=tr['censored'], b_lo_rec=round(tr['b_lo_rec'], 3),
                   snr_max=round(float(tr['snr'].max()), 1), sigma=tr['sigma'], du_med=tr['du_med'], win_invB=tr['win_invB'])
        for Te in (1.2, 4.0):
            f = dingle_fit(tr, mm[tone], Te)
            if f:
                row[f'slope_{Te}'] = round(f['slope'], 3); row[f'slope_se_{Te}'] = round(f['slope_se'], 3)
                row[f'TD_{Te}'] = round(f['TD'], 2); row[f'c_{Te}'] = round(f['c'], 3); row[f'nwin_{Te}'] = f['nwin']
                row[f'ufit_{Te}'] = f"{f['u_lo']:.2f}-{f['u_hi']:.2f}"
        out.append(row); tracks[(rec, j, tone)] = dict(n=n, F=F, Bc=tr['b_centers'], amp=tr['amp'], snr=tr['snr'], sigma=tr['sigma'],
                                                      onset=tr['onset_b'], cens=tr['censored'], m=mm[tone], I=I, tau=tau, du=tr['du_med'],
                                                      win=tr['win_invB'])
keys = sorted({k for r in out for k in r}, key=lambda k: list(out[0]).index(k) if k in out[0] else 99)
keys = list(dict.fromkeys(list(out[0].keys()) + ['err','onset_b','censored','b_lo_rec','snr_max','sigma','du_med','win_invB'] +
                          [f'{a}_{t}' for t in (1.2, 4.0) for a in ('slope','slope_se','TD','c','nwin','ufit')]))
with open('envelopes.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, keys); w.writeheader(); [w.writerow(r) for r in out]
pickle.dump(tracks, open('tracks.pkl', 'wb'))
print(len(out), 'rows')
