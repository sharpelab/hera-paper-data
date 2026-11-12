"""Interference-current amplitude i_n(t) from the drain-current channel sr0, every run, in windows of ~60 s:
sr0 complex residual (minus run median) fitted to c*exp(i 2 pi f0 t) (one-sided line, f0 = 1.21628 Hz), input-referred via H(f0; tau)."""
import sys, json, datetime as dtm, numpy as np
sys.path.insert(0, '.')
from nd import *
F0 = 1.21628
H = lambda tau: 1 / (1 + (2 * np.pi * F0 * tau) ** 2) ** 2
inv = json.load(open('inventory_raw.json'))
rows = []
for r in inv:
    if (r.get('npts') or 0) < 30: continue
    d = loadrun(r['day'], r['run'])
    if d['sr0Y'] is None: continue
    gain = abs(d['meta']['measurement_config']['sr0_gain'])
    t = d['t'].ravel(); z = (d['sr0X'] + 1j * d['sr0Y']).ravel(); o = np.argsort(t); t, z = t[o], z[o]
    z = z - np.median(z.real) - 1j * np.median(z.imag)
    tau = d['tau']
    edges = np.arange(t[0], t[-1] + 60, 60.0)
    amps = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (t >= a) & (t < b)
        if m.sum() < 8: continue
        tt = t[m]; zz = z[m]
        E = np.exp(1j * 2 * np.pi * F0 * tt)
        # LS: zz = c*E + k (k complex offset)
        A = np.c_[E, np.ones_like(E)]
        c, *_ = np.linalg.lstsq(A, zz, rcond=None)
        # conditioning: if E ~ const over the window (alias to DC) c and k are degenerate
        cond = np.abs(np.mean(E))
        if cond > 0.9: continue
        amps.append((0.5 * (a + b), np.abs(c[0]) / gain / H(tau)))
    if not amps: continue
    amps = np.array(amps)
    med = np.median(amps[:, 1])
    rows.append(dict(run=f"{r['day']}-r{r['run']}", start=float(t[0]), end=float(t[-1]), tau=tau, dt=float(np.median(np.diff(t))),
                     i_n_pA=float(med * 1e12), i_n_p10=float(np.percentile(amps[:, 1], 10) * 1e12), i_n_p90=float(np.percentile(amps[:, 1], 90) * 1e12), nwin=len(amps),
                     series=[(float(a), float(b * 1e12)) for a, b in amps]))
    st = dtm.datetime.fromtimestamp(t[0]).strftime('%m-%d %H:%M')
    print(f"{rows[-1]['run']:7s} {st} tau {tau:.2f} dt {rows[-1]['dt']:.2f}: i_n {med*1e12:6.1f} pA (p10 {rows[-1]['i_n_p10']:.0f}, p90 {rows[-1]['i_n_p90']:.0f}, {len(amps)} win)")
json.dump(rows, open('i_n_series.json', 'w'))
