"""Direct line search in 08-23 r0 (tau 30 ms, dt 0.29 s, B = 0): complex periodogram of the lock-in output residual using real timestamps."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.signal import savgol_filter
day, run = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (23, 0)
d = loadrun(day, run); t = d['t'].ravel(); X = d['sr1X'].ravel(); Y = d['sr1Y'].ravel(); x0 = d['sr0X'].ravel(); y0 = d['sr0Y'].ravel()
o = np.argsort(t); t, X, Y, x0, y0 = t[o], X[o], Y[o], x0[o], y0[o]
t = t - t[0]
def resid(z, w=15): return z - savgol_filter(z, w, 2)
Z1 = resid(X) + 1j * resid(Y); Z0 = resid(x0) + 1j * resid(y0)
f = np.arange(-8, 8, 0.0005)
def pgram(z):
    out = np.empty(f.size)
    for i in range(0, f.size, 2000):
        ff = f[i:i + 2000]
        out[i:i + 2000] = np.abs(np.exp(-2j * np.pi * ff[:, None] * t[None, :]) @ z) ** 2 / z.size
    return out
P1 = pgram(Z1); P0 = pgram(Z0)
for lab, P, z in (('sr1', P1, Z1), ('sr0', P0, Z0)):
    top = np.argsort(P)[::-1]
    picks = []
    for k in top:
        if all(abs(f[k] - p) > 0.05 for p in picks): picks.append(f[k])
        if len(picks) >= 8: break
    print(lab, 'total var', np.mean(np.abs(z) ** 2), 'peaks (Hz, power/mean):', ', '.join(f'{p:+.4f}:{P[np.argmin(abs(f-p))]/np.median(P):.0f}' for p in picks))
np.savez('ls_%d_%d.npz' % (day, run), f=f, P1=P1, P0=P0)
print('dt median', np.median(np.diff(t)), 'duration', t[-1])
