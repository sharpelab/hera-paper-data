"""1D B sweeps (spot checks + ladders): noise density by B x |dR/dB| (fine B steps -> good gradient), X and Y."""
import numpy as np
z = np.load('pts.npz'); A = z['A']; C = list(z['cols']); c = {k: A[:, i] for i, k in enumerate(C)}
def rob(v): return 1.4826 * np.median(np.abs(v - np.median(v)))
key = c['day'] * 100 + c['run']
Be = [2.3, 4, 6, 10.1]; Ge = [0, 60, 150, 300, 3000]
for day, runs in ((21, [5, 10, 11, 12, 13, 14, 15]), (22, [6, 7, 9, 10, 11, 12, 13, 14])):
    for run in runs:
        m0 = (key == day * 100 + run) & (np.abs(c['R']) < 1500)
        tau = c['tau'][m0][0]; e = np.sqrt(5 / 64 / tau)
        s = f"{day}-r{run:<2d} tau {tau} T {np.nanmedian(c['T'][m0]):5.1f}: "
        for lo, hi in zip(Be[:-1], Be[1:]):
            s += f' B[{lo},{hi}):'
            for glo, ghi in zip(Ge[:-1], Ge[1:]):
                m = m0 & (c['B'] >= lo) & (c['B'] < hi) & (c['gB'] >= glo) & (c['gB'] < ghi)
                s += f" {rob(c['dY'][m])/e*1e9:4.0f}/{rob(c['dX'][m])/e*1e9:<4.0f}" if m.sum() >= 12 else '   -     '
        print(s)
print('cells: Y/X noise nV/rtHz; within each B window, |dR/dB| bins', Ge)
