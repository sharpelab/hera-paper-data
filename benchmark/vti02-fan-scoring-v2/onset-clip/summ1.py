import csv, numpy as np, collections
rows = list(csv.DictReader(open('envelopes.csv')))
g = collections.defaultdict(list)
for r in rows: g[(r['rec'], r['tone'])].append(r)
fl = lambda x: float(x) if x not in ('', None) else np.nan
print(f"{'rec':8s} {'tone':6s} {'cols':>4s} {'trk':>4s} {'cens':>4s} {'onset unc med [min,max]':>26s} {'TD1.2 med [IQR]':>22s} {'TD4 med':>8s} {'Fratio':>6s}")
for (rec, tone), L in g.items():
    trk = [r for r in L if r['onset_b']]
    cen = [r for r in trk if r['censored'] == 'True']
    unc = np.array([fl(r['onset_b']) for r in trk if r['censored'] != 'True'])
    td = np.array([fl(r['TD_1.2']) for r in trk]); td = td[np.isfinite(td)]
    td4 = np.array([fl(r['TD_4.0']) for r in trk]); td4 = td4[np.isfinite(td4)]
    fr = np.array([fl(r['F'])/fl(r['F_exp']) for r in trk])
    s = f"{np.median(unc):.2f} [{unc.min():.2f},{unc.max():.2f}]" if unc.size else '-'
    t = f"{np.median(td):.1f} [{np.percentile(td,25):.1f},{np.percentile(td,75):.1f}] n{td.size}" if td.size else '-'
    print(f"{rec:8s} {tone:6s} {len(L):4d} {len(trk):4d} {len(cen):4d} {s:>26s} {t:>22s} {np.median(td4) if td4.size else np.nan:8.1f} {np.median(fr) if fr.size else np.nan:6.2f}")
