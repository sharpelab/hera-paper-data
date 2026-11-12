import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all, read, col
from common import detrend
from scipy.signal import hilbert
tr = {t['id']: t for t in load_all(include_ramp=False)}
for k, lo, hi, band in [('0822-r7', 0.6, 4.5, (5.2, 8.2)), ('0822-r7', 0.6, 4.5, (8.3, 10.8)), ('0824-r5-c0', 0.51, 6.0, (4.8, 7.0)), ('0825-r7-c0', 1.5, 6.0, (5.0, 8.0))]:
    t = tr[k]; b, y = detrend(t['B'], t['R'], lo, hi, 5)
    u = 1 / b; o = np.argsort(u); u, y = u[o], y[o]
    uu = np.linspace(u[0], u[-1], 4096); yy = np.interp(uu, u, y)
    F = np.fft.rfftfreq(uu.size, uu[1] - uu[0]); S = np.fft.rfft(yy)
    S[(F < band[0]) | (F > band[1])] = 0
    z = hilbert(np.fft.irfft(S, uu.size))
    ph = np.unwrap(np.angle(z)); f = np.gradient(ph, uu) / (2 * np.pi)
    amp = np.abs(z)
    # report mean instantaneous F in consecutive u-chunks (drop edges)
    edges = np.linspace(u[0] + 0.1, u[-1] - 0.1, 9)
    out = []
    for a, c in zip(edges[:-1], edges[1:]):
        m = (uu >= a) & (uu < c)
        out.append(f'B {1 / c:.2f}-{1 / a:.2f}: {np.average(f[m], weights=amp[m] ** 2):.2f}')
    # global: phase slope fit
    p = np.polyfit(uu[(uu > u[0] + 0.1) & (uu < u[-1] - 0.1)], ph[(uu > u[0] + 0.1) & (uu < u[-1] - 0.1)], 2)
    print(k, band, '| phase fit F(u) = %.2f + %.2f*(u-umid)' % ((2 * p[0] * np.mean(uu) + p[1]) / (2 * np.pi), 2 * p[0] / (2 * np.pi)))
    print('   ', ' ; '.join(out))
# time/B relation and T for 0822 r7
m, X = read('0822', 7); tt = col(m, X, 'time'); B = col(m, X, 'magnet_field'); T = col(m, X, 'T_sample'); Ig = col(m, X, 'k_2400_tg_curr')
print('0822 r7 time span h', (tt[-1] - tt[0]) / 3600, 'B first/last', B[0], B[-1], 'T range', np.nanmin(T), np.nanmax(T), 'I_tg pA', np.nanpercentile(Ig * 1e12, [5, 50, 95]))
