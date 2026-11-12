"""Lomb-Scargle (real, floating mean) of the leak-removed quadrature residual across rows with real timestamps, high-B rows.
Row gaps break the within-row aliasing, so a coherent line shows at its true frequency."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
from scipy.signal import lombscargle
cases = [(21, 8, 3.5, 10), (24, 4, 1.5, 6), (25, 8, 3.5, 8), (22, 8, 3.5, 10), (23, 6, 3, 8), (25, 7, 3, 6), (21, 5, 3, 10), (21, 10, 3, 10), (25, 5, 2, 6), (25, 6, 2, 6)]
f = np.arange(0.02, 4.0, 0.0005)
for day, run, lo, hi in cases:
    d = loadrun(day, run); X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    B = d['B']; t = d['t']
    T, V = [], []
    for i in range(d['nrows']):
        ok = (B[i] >= lo) & (B[i] < hi) & (np.abs(R[i]) < 1500)
        if ok.sum() < 5: continue
        y = Yc[i][ok]; tt = t[i][ok]
        if d['nrows'] > 1 and ok.sum() > 8:
            k = np.arange(y.size); y = y - np.polyval(np.polyfit(k, y, 1), k)
        T.append(tt); V.append(y)
    t1 = np.concatenate(T); y1 = np.concatenate(V)
    if d['nrows'] == 1:  # 1D: detrend along B with a running median
        from scipy.ndimage import median_filter
        o = np.argsort(t1); t1, y1 = t1[o], y1[o]; y1 = y1 - median_filter(y1, 9, mode='nearest')
    t1 = t1 - t1[0]
    P = lombscargle(t1, y1 - y1.mean(), 2 * np.pi * f, normalize=False)
    amp = np.sqrt(4 * P / y1.size)
    top = []
    for k in np.argsort(amp)[::-1]:
        if all(abs(f[k] - q) > 0.03 for q in top): top.append(f[k])
        if len(top) >= 6: break
    i0 = np.argmin(abs(f - 1.21628))
    print(f"{day}-r{run} B[{lo},{hi}) N {y1.size} span {t1[-1]:.0f}s dt {np.median(np.diff(d['t'],axis=1)) if d['nfast']>1 else np.nan:.2f}: rms {y1.std()*1e9:.0f} nV | top: " +
          ', '.join(f"{q:.4f}Hz {amp[np.argmin(abs(f-q))]*1e9:.0f}nV" for q in top) + f" | at f0 1.2163: {amp[i0-4:i0+5].max()*1e9:.0f} nV")
    np.save(f'ls_{day}_{run}.npy', np.c_[f, amp])
