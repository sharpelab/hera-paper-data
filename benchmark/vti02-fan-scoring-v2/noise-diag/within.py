"""Within-run decomposition of the quadrature (leak-removed Y) noise: fast axis vs along B, binned by B, |X|, |dX/dn|, |dX/dB|."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (25, 7), (24, 5), (23, 6), (23, 7)]
def prep(day, run):
    d = loadrun(day, run); X, Y, t = d['sr1X'], d['sr1Y'], d['t']
    tau = d['tau']
    # leak fit on low-R points only (phase offset of the reference), per run
    I = d['I']; R = X / I
    m = np.abs(R) < 400
    a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    dt = np.nanmedian(np.diff(t, axis=1)); cf = corr_d2(dt, tau) if d['nfast'] > 2 else 1
    # fast-axis d2 at interior points
    F = np.full(X.shape, np.nan); F[:, 1:-1] = d2(Yc, 1) / np.sqrt(6) * cf
    # along-row-sequence (slow) d2, rows in acquisition order (as stored)
    Sl = np.full(X.shape, np.nan); Sl[1:-1, :] = d2(Yc, 0) / np.sqrt(6)
    FX = np.full(X.shape, np.nan); FX[:, 1:-1] = d2(X, 1) / np.sqrt(6)
    SX = np.full(X.shape, np.nan); SX[1:-1, :] = d2(X, 0) / np.sqrt(6)
    dXn = np.gradient(X, axis=1) if d['nfast'] > 2 else np.zeros_like(X)
    dXB = np.gradient(X, axis=0)
    dens = lambda s: to_density(s, tau, d['slope']) * 1e9
    return d, dict(X=X, Yc=Yc, F=F, S=Sl, FX=FX, SX=SX, dXn=dXn, dXB=dXB, B=np.broadcast_to(d['B'], X.shape) if d['B'] is not None else None, a=a, dens=dens, R=R)
if __name__ == '__main__':
    for day, run in RUNS:
        d, p = prep(day, run); dens = p['dens']; B = p['B']
        print(f"== {day}-r{run} tau {d['tau']} I {d['I']*1e9:.0f} nA sens {d['sens']} leak a {p['a']:+.3f}  (nV/rtHz, robust)")
        def show(lab, key, edges):
            s = f'  {lab:8s}'
            for lo, hi in zip(edges[:-1], edges[1:]):
                m = (key >= lo) & (key < hi)
                f = p['F'][m]; sl = p['S'][m]
                f = f[np.isfinite(f)]; sl = sl[np.isfinite(sl)]
                if f.size + sl.size < 20: continue
                s += f" [{lo:g},{hi:g}) f{dens(rob(f)) if f.size>10 else np.nan:5.0f} s{dens(rob(sl)) if sl.size>10 else np.nan:5.0f}"
            print(s)
        show('B(T)', B, [0, 1, 1.5, 2, 3, 4, 6, 8, 11])
        ax = np.abs(p['X']) / d['I']
        show('|R|ohm', ax, [0, 50, 100, 150, 250, 400, 800, 2000, 1e6])
        g = np.abs(p['dXn']) / d['I']
        show('|dR/dcol|', g, [0, 2, 5, 10, 20, 50, 100, 1e6])
        g = np.abs(p['dXB']) / d['I']
        show('|dR/drow|', g, [0, 2, 5, 10, 20, 50, 100, 1e6])
