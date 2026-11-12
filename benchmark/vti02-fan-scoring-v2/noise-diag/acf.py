"""Time-ordered structure of the quadrature noise within rows: ACF at lags 1..8 points and row-averaged periodogram (aliased), by B band."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from within import prep
RUNS = [(21, 8), (22, 8), (24, 4), (25, 8), (23, 6), (23, 7), (21, 4), (25, 4), (22, 5)]
for day, run in RUNS:
    d, p = prep(day, run)
    Yc = p['Yc']; t = d['t']; dt = np.nanmedian(np.diff(t, axis=1)); B = d['B'][:, 0] if d['B'] is not None else np.zeros(d['nrows'])
    G = np.maximum(np.abs(p['dXn']), np.abs(p['dXB'])) / d['I']
    print(f"== {day}-r{run} tau {d['tau']} dt {dt:.2f}s ({dt/d['tau']:.1f} tau), filter ACF at lag1 {acf4(dt/d['tau']):.3f}")
    bands = [(0, 1.5), (1.5, 3), (3, 6), (6, 11)] if d['B'] is not None else [(-1, 1)]
    for lo, hi in bands:
        rows = np.where((B >= lo) & (B < hi))[0]
        if len(rows) < 3: continue
        acc = np.zeros(9); nacc = np.zeros(9); P = 0; nP = 0
        for i in rows:
            y = Yc[i].copy()
            if (np.abs(p['R'][i]) > 1500).any(): 
                ok = np.abs(p['R'][i]) < 1500
                if ok.sum() < 20: continue
                y = y[ok]
            # remove a smooth trend in column index (quadratic) to kill slow signal
            k = np.arange(y.size); y = y - np.polyval(np.polyfit(k, y, 2), k)
            v = np.mean(y * y)
            for L in range(9):
                acc[L] += np.mean(y[:y.size - L] * y[L:]) ; nacc[L] += 1
            w = np.hanning(y.size); f = np.fft.rfftfreq(y.size, dt); S = np.abs(np.fft.rfft(y * w)) ** 2 / (w ** 2).sum() * 2 * dt
            fg = np.linspace(0, 0.5 / dt, 11); P = P + np.interp(fg, f, S); nP += 1
        a = acc / nacc; a = a / a[0]
        Pm = np.sqrt(P / nP) * 1e9
        print(f"   B[{lo},{hi}) rows {len(rows)}: acf lags1-8 " + ' '.join(f'{x:+.2f}' for x in a[1:]) + ' | sqrt PSD(nV/rtHz, sampled seq) at f/fNyq 0..1: ' + ' '.join(f'{x:.0f}' for x in Pm))
