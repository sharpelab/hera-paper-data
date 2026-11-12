import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.constants import h, e
from hera.analysis import open_run, sdh_onset, sdh_fft

fig, axs = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, rid, n, blo in zip(axs, (6, 7), (3.2, -1.2), (0.7, 0.71)):
    run = open_run(f'data/{rid}')
    pars = run.meta['instruments']['sr1']['snapshot']['parameters']
    ib = pars['amplitude']['value'] / run.meta['measurement_config']['bias_resistor']
    fs = pars['sensitivity']['value'] / ib
    b = run.col('magnet_field'); r = run.col('sr1_X') / ib
    onset = sdh_onset(r, b, r_full_scale=fs)
    print(f'run {rid}: {onset.summary()}')
    f, sp = sdh_fft(r[:, None], b, b_range=(blo, 10.0), bg_degree=5, log=False)
    y = sp[0]; y = y / np.max(y[(f >= 3) & (f <= 40)])
    ax.plot(f, y, lw=1)
    ax.axvline(h/(4*e)*abs(n)*1e16, color='k', ls=':', label='F_L (g=4)')
    ax.set_xlim(3, 40); ax.set_xlabel('SdH frequency (T)'); ax.set_title(f'run {rid}, n={n:+.1f}×10¹²')
    ax.legend(fontsize=8)
    pk, _ = find_peaks(y, prominence=.04)
    pk = sorted((i for i in pk if 3 < f[i] < 40), key=lambda i: y[i], reverse=True)[:7]
    print(f'run {rid}, FFT {blo:.2f}..10 T, strongest peaks:', [(round(float(f[i]), 2), round(float(y[i]), 2)) for i in pk])
axs[0].set_ylabel('normalized FFT magnitude')
fig.tight_layout(); plt.show()
