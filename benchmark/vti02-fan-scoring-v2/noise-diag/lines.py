"""Complex periodogram of per-row residuals (savgol along the time-ordered fast axis), sr1 and sr0, every run with >=100 pts.
Reports the top one-sided peaks and the fitted line amplitude near candidate f0."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.signal import savgol_filter
inv = json.load(open('inventory_raw.json'))
f = np.arange(-4, 4, 0.001)
def pgram(t, z):
    out = np.empty(f.size, complex)
    for i in range(0, f.size, 1000):
        ff = f[i:i + 1000]
        out[i:i + 1000] = np.exp(-2j * np.pi * ff[:, None] * t[None, :]) @ z
    return out
res = {}
only = sys.argv[1:] 
for r in inv:
    key = f"{r['day']}-r{r['run']}"
    if only and key not in only: continue
    if (r.get('npts') or 0) < 100: continue
    d = loadrun(r['day'], r['run'])
    if d['sr1Y'] is None or d['sr0Y'] is None: continue
    if d['nrows'] > 1 and d['nfast'] < 15: continue
    w = 9 if d['nfast'] >= 15 else 9
    T, Z1, Z0 = [], [], []
    for i in range(d['nrows']):
        tt = d['t'][i]
        if tt.size < w + 2: continue
        rr = lambda z: z - savgol_filter(z, w, 2)
        T.append(tt); Z1.append(rr(d['sr1X'][i]) + 1j * rr(d['sr1Y'][i])); Z0.append(rr(d['sr0X'][i]) + 1j * rr(d['sr0Y'][i]))
    t = np.concatenate(T); t = t - t[0]; z1 = np.concatenate(Z1); z0 = np.concatenate(Z0)
    # restrict very long runs to keep cost down
    if t.size > 6000: sel = slice(0, 6000); t, z1, z0 = t[sel], z1[sel], z0[sel]
    P1 = pgram(t, z1); P0 = pgram(t, z0)
    out = {}
    for lab, P, z in (('sr1', P1, z1), ('sr0', P0, z0)):
        pw = np.abs(P) ** 2 / z.size; med = np.median(pw)
        k = np.argmax(pw); fk = f[k]
        # amplitude of a complex sinusoid at fk: |sum z e^{-i w t}| / N  (savgol attenuation ignored)
        amp = np.abs(P[k]) / z.size
        # also at the sr0-identified line near +1.2165 and its mirror
        k12 = np.argmax(np.where(np.abs(f - 1.22) < 0.03, pw, 0)); km = np.argmax(np.where(np.abs(f + 1.22) < 0.03, pw, 0))
        out[lab] = dict(fpk=float(fk), pk=float(pw[k] / med), f12=float(f[k12]), p12=float(pw[k12] / med), a12=float(np.abs(P[k12]) / z.size), pm12=float(pw[km] / med),
                        rms=float(np.sqrt(np.mean(np.abs(z) ** 2))))
    dt = np.median(np.diff(d['t'][0])) if d['nfast'] > 1 else np.nan
    res[key] = dict(tau=d['tau'], dt=float(dt), B=None if d['B'] is None else [float(np.nanmin(d['B'])), float(np.nanmax(d['B']))], **out)
    s1, s0 = out['sr1'], out['sr0']
    print(f"{key:7s} tau {d['tau']:.2f} dt {dt:.2f}: sr1 top {s1['fpk']:+.3f} x{s1['pk']:.0f} | @+1.22: {s1['f12']:+.3f} x{s1['p12']:.0f} amp {s1['a12']*1e9:.1f} nV (mirror x{s1['pm12']:.0f}) || "
          f"sr0 top {s0['fpk']:+.3f} x{s0['pk']:.0f} | @+1.22: {s0['f12']:+.3f} x{s0['p12']:.0f} amp {s0['a12']*1e6:.2f} uV (mirror x{s0['pm12']:.0f})", flush=True)
json.dump(res, open('lines%s.json' % ('_' + '_'.join(only) if only else ''), 'w'), indent=1)
