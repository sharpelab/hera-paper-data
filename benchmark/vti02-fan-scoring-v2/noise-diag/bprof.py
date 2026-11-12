"""Fine B profile of quadrature (and X for 1D) noise density, every B-swept run."""
import numpy as np
z = np.load('pts.npz'); A = z['A']; C = list(z['cols']); c = {k: A[:, i] for i, k in enumerate(C)}
def rob(v): return 1.4826 * np.median(np.abs(v - np.median(v)))
key = c['day'] * 100 + c['run']
Be = np.array([0.3, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8, 9, 10.1])
print('B bin lo: ' + ' '.join(f'{b:5.1f}' for b in Be[:-1]))
prof = {}
for k in np.unique(key):
    m0 = (key == k) & (np.abs(c['R']) < 1500) & (c['B'] > 0.3)
    if m0.sum() < 100: continue
    tau = c['tau'][m0][0]; e = np.sqrt(5 / 64 / tau)
    vals = []
    for lo, hi in zip(Be[:-1], Be[1:]):
        m = m0 & (c['B'] >= lo) & (c['B'] < hi)
        vals.append(rob(c['dY'][m]) / e * 1e9 if m.sum() >= 12 else np.nan)
    prof[int(k)] = vals
    print(f"{int(k)//100}-r{int(k)%100:<3d}t{tau:.1f} T{np.nanmedian(c['T'][m0]):4.0f}: " + ' '.join('    -' if np.isnan(v) else f'{v:5.0f}' for v in vals))
np.save('bprof.npy', dict(edges=Be, prof=prof), allow_pickle=True)
