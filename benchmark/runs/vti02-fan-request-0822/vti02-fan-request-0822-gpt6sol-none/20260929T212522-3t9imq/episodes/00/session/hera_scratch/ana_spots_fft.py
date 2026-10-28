# Diagnostic FFT only; frequency identities require tracking across n in the fan.
from scipy.signal import find_peaks
fig, axes = plt.subplots(1, 2, figsize=(12, 3.5))
for ax, rid in zip(axes, (6, 7)):
    B, R = spot[rid]
    f, spec = sdh_fft(R[:, None], B, b_range=(1.5, 9.5), nfft=1024, bg_degree=5, log=False)
    y = spec[0]
    pk, _ = find_peaks(y)
    pk = sorted((p for p in pk if 2 < f[p] < 65), key=lambda p: y[p], reverse=True)[:5]
    print(f'data/{rid}: strongest 1.5..9.5 T FFT peaks ' + ', '.join(f'{f[p]:.1f} T' for p in pk))
    ax.plot(f, y)
    ax.set(xlim=(0, 65), xlabel='1/B frequency (T)', ylabel='magnitude (ohm)', title=f'data/{rid}: B-space detrended')
fig.tight_layout(); plt.show()
