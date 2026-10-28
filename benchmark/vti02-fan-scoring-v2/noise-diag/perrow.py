"""Per-row quadrature noise (fast-axis d2, low-gradient points) vs time, B, T_sample."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from within import prep
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (23, 6), (23, 7)]
for day, run in RUNS:
    d, p = prep(day, run); dens = p['dens']; B = d['B'][:, 0]
    G = np.maximum(np.abs(p['dXn']), np.abs(p['dXB'])) / d['I']
    t = d['t']; t0 = t[0, 0]; T = d['T']
    out = []
    for i in range(d['nrows']):
        m = (G[i] < 30) & np.isfinite(p['F'][i]) & (np.abs(p['R'][i]) < 1500)
        v = p['F'][i][m]
        out.append((i, (t[i, 0] - t0) / 60, B[i], T[i].mean() if T is not None else np.nan, dens(rob(v)) if v.size >= 8 else np.nan, v.size))
    out = np.array(out)
    np.savetxt(f'perrow_{day}-r{run}.csv', out, delimiter=',', header='row,tmin,B,T,noise_nVrtHz,npts', comments='')
    print(f'== {day}-r{run} tau {d["tau"]}: row: t(min) B T noise')
    step = max(1, len(out) // 25)
    print('   ' + ' | '.join(f"{int(r[0])}:{r[1]:.0f}m {r[2]:.2f}T {r[3]:.3f}K {r[4]:.0f}" for r in out[::step]))
    ok = np.isfinite(out[:, 4])
    print('   corr(noise, B) %.2f  corr(noise, t) %.2f  corr(noise, T) %.2f' % tuple(np.corrcoef(out[ok, 4], out[ok, k])[0, 1] for k in (2, 1, 3)))
