from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
for i, (file_id, n, b_lo) in enumerate(((6, +3.2, 0.85), (7, -1.2, 0.7))):
    r = open_run(f'data/{file_id}')
    B, R = r.col('magnet_field'), r.col('sr1_X') / 1e-8
    onset = sdh_onset(R, B, r_full_scale=5000)
    print(f'run {file_id}: onset {onset.onset_b:.2f} T '
          f'({onset.onset_freq:.2f} T carrier); '
          f'tones '+', '.join(f'{t.freq:.1f} T' for t in onset.tones))
    f, spec = sdh_fft(R[:, None], B, b_range=(b_lo, 10),
                      bg_degree=5, window='hann', log=False, nfft=4096)
    y = spec[0]
    peaks, _ = find_peaks(y, prominence=max(y[(f > 3) & (f < 45)]) * .04)
    peaks = sorted((j for j in peaks if 3 < f[j] < 45), key=lambda j: y[j], reverse=True)[:6]
    print('  FFT peaks: '+', '.join(f'{f[j]:.1f} T' for j in peaks))
    fl = float(luttinger_frequency(abs(n) * 1e16))
    ax[i].plot(f, y, lw=1, label=f'run {file_id}, B≥{b_lo:g} T')
    ax[i].axvline(fl, color='k', ls='--', lw=1, label=f'F_L={fl:.1f} T')
    if file_id == 6:
        for j, model_f in enumerate((7.3, 25.8)):
            ax[i].axvline(model_f, color='tab:red', ls=':', lw=1,
                          label='ABAB model' if j == 0 else None)
    ax[i].set(xlim=(0, 45), xlabel='frequency (T)', ylabel='FFT magnitude',
              title=f'n = {n:+.1f}×10¹² cm⁻²; B-space detrend, Hann window')
    ax[i].legend()
    ax[i].grid(alpha=.25)
plt.show()
