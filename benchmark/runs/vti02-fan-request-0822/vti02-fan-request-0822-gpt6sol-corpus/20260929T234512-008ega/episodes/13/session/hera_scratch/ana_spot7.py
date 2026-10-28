# Run 7, raw before analysis; read-only disk analysis.
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft
from scipy.signal import find_peaks
r7 = open_run('data/7'); print(summarize_run(r7))
B7 = r7.col('magnet_field'); I7 = r7.col('sr0_X') / -1e6
R7 = np.abs(r7.col('sr1_X') / I7)
fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
ax[0].plot(B7, R7, lw=.8); ax[0].set_ylabel('|Rxx| (Ω)'); ax[0].set_title('Run 7 raw — B₁–B₂')
ax[1].plot(B7, r7.col('k_2400_tg_curr')*1e12, label='TG')
ax[1].plot(B7, r7.col('k_2400_bg_curr')*1e12, label='BG')
ax[1].legend(); ax[1].set_xlabel('B (T)'); ax[1].set_ylabel('Gate current (pA)')
fig.tight_layout(); plt.show()
print(f'R: {R7.min():.1f}–{R7.max():.1f} Ω; I_drain: {I7.min()*1e9:.3f}–{I7.max()*1e9:.3f} nA; T: {r7.col("T_sample").min():.3f}–{r7.col("T_sample").max():.3f} K')
o7 = sdh_onset(R7, B7, b_lo=.3, r_full_scale=5000)
print(o7.summary())
fig, ax = plt.subplots(figsize=(9, 4))
for lo in (1.5, 2.0, 3.0):
    f, spec = sdh_fft(R7[:, None], B7, b_range=(lo, 10), log=False, nfft=4096)
    y = spec[0] / spec[0].max(); ax.plot(f, y, label=f'{lo}–10 T')
    peaks, _ = find_peaks(y, prominence=.08)
    print(f'FFT {lo}–10 T:', [(round(float(f[p]), 1), round(float(y[p]), 2)) for p in peaks if 3 < f[p] < 40])
ax.set_xlim(0, 42); ax.set_xlabel('Frequency (T)'); ax.set_ylabel('Normalized FFT magnitude')
ax.set_title('Run 7 — window dependence, B-space detrend'); ax.legend(); fig.tight_layout(); plt.show()
