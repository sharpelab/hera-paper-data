from hera.analysis import open_run, sdh_onset, sdh_fft
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for k, rid in enumerate((6, 7)):
    r = open_run(f'data/{rid}')
    B, R = r.col('magnet_field'), r.col('sr1_X') / 1e-8
    order = np.argsort(B)
    B, R = B[order], R[order]
    on = sdh_onset(R, B, r_full_scale=5000)
    print(f'run {rid}:\n{on.summary()}')
    for cutoff in (1.5, 2.0, 3.0):
        f, s = sdh_fft(R[:, None], B, b_range=(cutoff, 10.0), bg_degree=5, log=False)
        amp = s[0]
        peaks, _ = find_peaks(amp, prominence=np.nanmax(amp)*.1)
        peaks = sorted((i for i in peaks if 2 < f[i] < 55), key=lambda i: amp[i], reverse=True)[:5]
        print(f'  B>{cutoff:.1f} T peaks:', [(round(float(f[i]), 1), round(float(amp[i]/np.nanmax(amp)), 2)) for i in peaks])
        ax[k].plot(f, amp/np.nanmax(amp), label=f'B>{cutoff:.1f} T')
    ax[k].set(xlim=(0, 55), xlabel='frequency (T)', ylabel='normalized FFT amplitude', title=f'Run {rid}: FFT cutoff check')
    ax[k].legend()
fig.tight_layout()
plt.show()
