"""Transfer impedance of the 15 Hz interference into the sr1 probes: per ~90 s window, fit the f0 line in sr1 Yc (real) and in sr0 (complex),
Z_t = |sr1 line| / |i_n line| (both through the same H), vs window B and |R|. Also the white-noise residual after removing the line."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from nd import *
F0 = 1.21628
RUNS = [(21, 5), (21, 8), (21, 10), (21, 11), (21, 12), (22, 6), (22, 7), (22, 8), (23, 6), (23, 7), (24, 4), (24, 5), (25, 5), (25, 6), (25, 7), (25, 8), (21, 4), (22, 5), (23, 3), (24, 3), (25, 4)]
out = {}
for day, run in RUNS:
    d = loadrun(day, run); gain = abs(d['meta']['measurement_config']['sr0_gain'])
    X1, Y1 = d['sr1X'], d['sr1Y']; I = d['I']; m = np.abs(X1 / I) < 400; a = np.sum(X1[m] * Y1[m]) / np.sum(X1[m] ** 2); Yc = (Y1 - a * X1)
    t = d['t'].ravel(); o = np.argsort(t); t = t[o]
    yc = Yc.ravel()[o]; z0 = (d['sr0X'] + 1j * d['sr0Y']).ravel()[o]; z0 = z0 - np.median(z0.real) - 1j * np.median(z0.imag)
    R = (X1 / I).ravel()[o]; B = (d['B'] if d['B'] is not None else np.zeros_like(X1)).ravel()[o]
    rec = []
    win = 90.0 if d['nrows'] > 1 else 150.0
    for s0 in np.arange(t[0], t[-1], win):
        w = (t >= s0) & (t < s0 + win)
        if w.sum() < 10: continue
        E = np.exp(1j * 2 * np.pi * F0 * t[w])
        if np.abs(E.mean()) > 0.85: continue
        A0 = np.c_[E, np.ones(w.sum())]
        c0 = np.linalg.lstsq(A0, z0[w], rcond=None)[0][0] / gain          # A (lock-in output units, before 1/H)
        Ar = np.c_[np.cos(2 * np.pi * F0 * t[w]), np.sin(2 * np.pi * F0 * t[w]), np.ones(w.sum()), np.arange(w.sum()) / w.sum()]
        cy, *_ = np.linalg.lstsq(Ar, yc[w], rcond=None)
        res = yc[w] - Ar @ cy
        ampY = np.hypot(cy[0], cy[1])     # V; a one-sided rotating phasor of amplitude A shows amplitude A in Y
        rec.append((np.median(B[w]), np.median(np.abs(R[w])), abs(c0), ampY, ampY / max(abs(c0), 1e-15), rob(res), w.sum()))
    rec = np.array(rec); out[f'{day}-r{run}'] = dict(tau=d['tau'], rec=rec.tolist())
    tau = d['tau']
    s = f"{day}-r{run:<2d} tau {tau} dt {np.nanmedian(np.diff(d['t'],axis=1)):.2f}: "
    for lo, hi in ((-0.1, 0.2), (0.2, 2), (2, 4), (4, 6), (6, 11)):
        mm = (rec[:, 0] >= lo) & (rec[:, 0] < hi)
        if mm.sum() < 2: continue
        s += f"B[{lo},{hi}) Zt {np.median(rec[mm,4]):6.0f} ohm (|R| {np.median(rec[mm,1]):4.0f}) lineY {np.median(rec[mm,3])*1e9:5.1f} nV i_n.H {np.median(rec[mm,2])*1e12:5.1f} pA ; "
    print(s)
json.dump(out, open('zt.json', 'w'))
