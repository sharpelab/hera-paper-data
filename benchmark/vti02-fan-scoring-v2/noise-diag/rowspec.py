"""Within-row spectrum of the leak-removed quadrature at high B, averaged over rows (aliased band 0..1/(2dt))."""
import sys, numpy as np
sys.path.insert(0, '.')
from nd import *
for day, run, lo, hi in ((21, 8, 4, 6.5), (21, 8, 2.4, 3.5), (24, 4, 1.5, 6), (22, 8, 4, 8), (25, 8, 4, 8), (25, 8, 1, 2), (23, 6, 3, 8), (23, 7, 3, 8)):
    d = loadrun(day, run); X, Y = d['sr1X'], d['sr1Y']; I = d['I']; R = X / I
    m = np.abs(R) < 400; a = np.sum(X[m] * Y[m]) / np.sum(X[m] ** 2); Yc = Y - a * X
    B = d['B'][:, 0]; t = d['t']; dt = np.median(np.diff(t, axis=1))
    rows = np.where((B >= lo) & (B < hi))[0]
    nf = 64; acc = 0; nacc = 0
    for i in rows:
        ok = np.abs(R[i]) < 1500
        y = Yc[i][ok]
        if y.size < 30: continue
        k = np.arange(y.size); y = y - np.polyval(np.polyfit(k, y, 1), k)
        w = np.hanning(y.size)
        S = np.abs(np.fft.rfft(y * w, n=2 * nf)) ** 2 / (w ** 2).sum()
        acc = acc + S; nacc += 1
    fa = np.fft.rfftfreq(2 * nf, dt)
    S = np.sqrt(acc / nacc * dt) * 1e9  # nV/rtHz-ish of the sampled sequence
    print(f'== {day}-r{run} B[{lo},{hi}) rows {nacc} dt {dt:.3f} fNyq {0.5/dt:.3f}Hz')
    print('   f_alias: ' + ' '.join(f'{x:.3f}' for x in fa[::4]))
    print('   amp    : ' + ' '.join(f'{x:5.0f}' for x in S[::4]))
    kk = np.argsort(S)[::-1][:3]; print('   top aliased freqs', [(round(fa[k], 3), round(S[k])) for k in kk], ' f0 alias expected', round(abs(((1.21628 * dt + 0.5) % 1 - 0.5) / dt), 3))
