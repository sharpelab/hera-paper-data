"""Does the sr0 (drain-current) interference line reappear in sr1 as i_n x R?  Complex regression of d2(Z1) on d2(Z0)*R/gain,
using the time-ordered axis. |c| ~ 1 and stable arg(c) => the voltage-channel excess is the same interference current through the sample."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
RUNS = [(21, 5), (21, 10), (21, 11), (21, 12), (21, 13), (21, 14), (21, 15), (22, 6), (22, 7), (22, 8), (23, 6), (23, 7), (24, 4), (24, 5), (24, 6), (24, 8), (24, 12), (25, 5), (25, 7), (25, 8), (23, 4), (21, 8)]
Be = [(0, 0.2), (0.2, 2), (2, 4), (4, 6), (6, 11)]
for day, run in RUNS:
    d = loadrun(day, run)
    gain = d['meta']['measurement_config']['sr0_gain']
    Z1 = d['sr1X'] + 1j * d['sr1Y']; Z0 = d['sr0X'] + 1j * d['sr0Y']
    I0 = np.median(Z0) / gain            # complex mean current (A)
    R = (d['sr1X'] + 1j * d['sr1Y']) / (I0 * np.abs(I0) / I0) / 1   # V / |I| (complex) ~ R e^{i phase}
    R = Z1 / np.abs(I0)
    ax = 1 if d['nfast'] > 6 else 0
    if d['nrows'] == 1: ax = 1
    a1 = d2(Z1, ax); a0 = d2(Z0, ax) / gain            # current fluctuation (A)
    Rm = (R[:, 1:-1] if ax == 1 else R[1:-1])
    B = d['B'] if d['B'] is not None else np.zeros(Z1.shape)
    Bm = B[:, 1:-1] if ax == 1 else B[1:-1]
    pred = Rm * a0          # predicted voltage fluctuation if the interference current flows like the drive current
    s = f"{day}-r{run:<2d} tau {d['tau']} dt {np.nanmedian(np.diff(d['t'], axis=1)):.2f} f0*dt mod1 {(1.21628*np.nanmedian(np.diff(d['t'], axis=1)))%1:.2f}: "
    for lo, hi in Be:
        m = (Bm >= lo) & (Bm < hi) & np.isfinite(pred) & (np.abs(Rm) < 3000)
        if m.sum() < 40: continue
        y = a1[m]; x = pred[m]
        c = np.vdot(x, y) / np.vdot(x, x)
        r2 = 1 - np.sum(np.abs(y - c * x) ** 2) / np.sum(np.abs(y - y.mean()) ** 2)
        frac = np.sqrt(np.mean(np.abs(c * x) ** 2) / np.mean(np.abs(y) ** 2))
        s += f"B[{lo},{hi}) |c| {abs(c):.2f} arg {np.degrees(np.angle(c)):+5.0f} R2 {r2:+.2f} (line share of d2 rms {frac:.2f}, n{m.sum()}) ; "
    print(s)
