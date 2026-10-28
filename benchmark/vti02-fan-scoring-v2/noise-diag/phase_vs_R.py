"""Phase of the sr1 signal vs R (and B) in each fan: is the quadrature a deterministic function of the signal?"""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
FANS = [(21, 8), (22, 8), (24, 4), (25, 8), (25, 7), (24, 5), (23, 6), (23, 7), (21, 5), (22, 6)]
for day, run in FANS:
    d = loadrun(day, run); X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    B = d['B']
    sig = 40e-9 * np.sqrt(5 / 64 / d['tau'])
    big = np.abs(X) > 20 * sig
    ph = np.rad2deg(np.arctan2(Y, X)); ph = np.where(ph > 90, ph - 180, np.where(ph < -90, ph + 180, ph))
    Rb = np.array([0, 100, 200, 400, 700, 1000, 1500, 3000, 1e5])
    s = f"{day}-r{run} I={I*1e9:.0f}nA tau={d['tau']}: phase(deg) by R bin (ohm): "
    for lo, hi in zip(Rb[:-1], Rb[1:]):
        m = big & (np.abs(R) >= lo) & (np.abs(R) < hi)
        if m.sum() > 10: s += f"[{lo:.0f},{hi:.0f}) {np.median(ph[m]):+.2f}±{rob(ph[m]):.2f} (n{m.sum()}) "
    print(s)
    if B is not None:
        s = '    by B: '
        for lo, hi in ((0, 1.5), (1.5, 3), (3, 5), (5, 8), (8, 11)):
            m = big & (B >= lo) & (B < hi) & (np.abs(R) < 400)
            if m.sum() > 10: s += f"[{lo},{hi}) {np.median(ph[m]):+.2f}±{rob(ph[m]):.2f} (n{m.sum()}) "
        print(s)
