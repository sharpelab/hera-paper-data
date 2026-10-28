from hera.analysis import sdh_onset, sdh_fft
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

on6 = sdh_onset(rxx6, b6, r_full_scale=5000)
print(on6.summary())
fig, ax = plt.subplots(figsize=(9, 4))
for blo in (1.0, 1.5, 2.0, 3.0):
    f, z = sdh_fft(rxx6[:, None], b6, b_range=(blo, 10), nfft=4096,
                   bg_degree=5, log=False)
    power = z[0]
    ax.plot(f, power / power.max(), label=f'{blo:g}–10 T')
    pk, _ = find_peaks(power, prominence=0.03*power.max())
    pk = sorted((p for p in pk if 3 <= f[p] <= 40), key=lambda p: power[p], reverse=True)[:5]
    print(f'{blo:g}–10 T: ' + ', '.join(f'{f[p]:.1f} T' for p in pk))
ax.axvline(33.1, color='k', linestyle=':', label='F_L (prior) 33.1 T')
ax.set(xlim=(0, 40), xlabel='SdH frequency (T)', ylabel='FFT power / window maximum',
       title='Run 6: window stability (B-space detrend, 1/B FFT)')
ax.legend(ncol=2); ax.grid(alpha=0.2)
plt.tight_layout(); plt.show()
