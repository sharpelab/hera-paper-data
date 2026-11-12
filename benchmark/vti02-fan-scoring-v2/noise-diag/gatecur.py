"""Gate-current (Keithley 2400) time series: Lomb-Scargle 0.02-20 Hz on real timestamps; amplitude at 14.99 Hz (f_ref + f0) and 1.216 Hz; NPLC 1 vs 10."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.signal import lombscargle
from scipy.ndimage import median_filter
inv = json.load(open('inventory_raw.json'))
f = np.arange(0.02, 20.0, 0.0005)
targets = [1.21628, 13.777, 14.9933, 12.5607, 15.0, 2.4326]
res = []
for r in inv:
    if (r.get('npts') or 0) < 100: continue
    d = loadrun(r['day'], r['run'])
    npl = r.get('k_2400_tg', {}).get('nplci')
    for ch in ('k_2400_tg_curr', 'k_2400_bg_curr'):
        c = d['g'](ch)
        if c is None: continue
        t = d['t'].ravel(); y = c.ravel(); o = np.argsort(t); t, y = t[o], y[o]
        y = y - median_filter(y, 15, mode='nearest')
        t = t - t[0]
        if t.size > 3000: t, y = t[:3000], y[:3000]
        P = lombscargle(t, y - y.mean(), 2 * np.pi * f, normalize=False); amp = np.sqrt(4 * P / y.size)
        med = np.median(amp)
        top = []
        for k in np.argsort(amp)[::-1]:
            if all(abs(f[k] - q) > 0.02 for q in top): top.append(f[k])
            if len(top) >= 4: break
        at = {tg: float(amp[np.abs(f - tg) < 0.003].max()) for tg in targets}
        res.append(dict(run=f"{r['day']}-r{r['run']}", ch=ch, nplc=npl, dt=float(np.median(np.diff(t))), rms=float(y.std()), top=[(float(q), float(amp[np.argmin(abs(f-q))])) for q in top], at=at, med=float(med)))
        print(f"{r['day']}-r{r['run']:<2d} {ch[7:9]} NPLC {npl} dt {np.median(np.diff(t)):.2f}: rms {y.std()*1e12:6.2f} pA  top " +
              ', '.join(f"{q:.4f}Hz {amp[np.argmin(abs(f-q))]*1e12:.2f}pA(x{amp[np.argmin(abs(f-q))]/med:.0f})" for q in top) +
              ' | @14.993 ' + f"{at[14.9933]*1e12:.2f}pA(x{at[14.9933]/med:.0f}) @1.216 {at[1.21628]*1e12:.2f}pA(x{at[1.21628]/med:.0f})", flush=True)
json.dump(res, open('gatecur.json', 'w'), indent=1)
