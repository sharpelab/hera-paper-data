"""Per run: quadrature noise density (robust, binned) vs |dR/dB| and vs B; fits sigma^2 = w^2 + (k*gB)^2 and sigma^2 = w^2 + (c*B)^2."""
import numpy as np, sys
from scipy.optimize import least_squares
z = np.load('pts.npz'); A = z['A']; C = list(z['cols']); c = {k: A[:, i] for i, k in enumerate(C)}
def rob(v): return 1.4826 * np.median(np.abs(v - np.median(v)))
key = c['day'] * 100 + c['run']
res = []
for k in np.unique(key):
    m0 = (key == k) & (c['B'] > 0.3) & (np.abs(c['R']) < 1500)
    if m0.sum() < 200: continue
    tau = c['tau'][m0][0]; I = c['I'][m0][0]; enbw = np.sqrt(5 / 64 / tau)
    y = c['dY'][m0] / enbw * 1e9; g = c['gB'][m0]; B = c['B'][m0]
    x = c['dX'][m0] / enbw * 1e9
    # bins in gB (quantiles)
    q = np.quantile(g, np.linspace(0, 1, 9))
    gb, sb, sx, nb, bb = [], [], [], [], []
    for lo, hi in zip(q[:-1], q[1:]):
        mm = (g >= lo) & (g <= hi)
        if mm.sum() < 30: continue
        gb.append(np.median(g[mm])); sb.append(rob(y[mm])); sx.append(rob(x[mm])); nb.append(mm.sum()); bb.append(np.median(B[mm]))
    gb, sb, bb = map(np.array, (gb, sb, bb))
    f = lambda p: (np.sqrt(p[0] ** 2 + (p[1] * gb) ** 2) - sb) / sb
    p = least_squares(f, [43, 0.1], bounds=([20, 0], [80, 10])).x
    fB = lambda p2: (np.sqrt(p2[0] ** 2 + (p2[1] * bb) ** 2) - sb) / sb
    # B-only model on B bins
    qb = np.quantile(B, np.linspace(0, 1, 9)); b2, s2 = [], []
    for lo, hi in zip(qb[:-1], qb[1:]):
        mm = (B >= lo) & (B <= hi)
        if mm.sum() >= 30: b2.append(np.median(B[mm])); s2.append(rob(y[mm]))
    b2, s2 = np.array(b2), np.array(s2)
    fB = lambda p2: (np.sqrt(p2[0] ** 2 + (p2[1] * b2) ** 2) - s2) / s2
    p2 = least_squares(fB, [43, 10], bounds=([20, 0], [80, 200])).x
    rg = np.sqrt(np.mean(f(p) ** 2)); rb = np.sqrt(np.mean(fB(p2) ** 2))
    Tm = np.nanmedian(c['T'][m0])
    print(f"{int(k)//100}-r{int(k)%100:<3d} tau {tau:.1f} I {I*1e9:4.0f}nA T {Tm:5.1f}  gB bins (ohm/T): " + ' '.join(f'{a:.0f}:{s:.0f}' for a, s in zip(gb, sb)) +
          f"\n      fit gB: w {p[0]:.0f} k {p[1]*1e3:.0f} pV/rtHz per ohm/T  rms rel resid {rg:.2f} | fit B: w {p2[0]:.0f} c {p2[1]:.1f} nV/rtHz/T resid {rb:.2f} | X/Y noise ratio (low-gB bin) {sx[0]/sb[0]:.2f}")
    res.append((int(k), tau, I, Tm, p[0], p[1], rg, p2[0], p2[1], rb))
np.save('reg1.npy', np.array(res))
