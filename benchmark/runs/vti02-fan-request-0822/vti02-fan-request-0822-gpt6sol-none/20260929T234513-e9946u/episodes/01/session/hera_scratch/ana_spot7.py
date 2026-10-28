from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
from scipy.signal import find_peaks
from hera.analysis import sdh_fft, sdh_onset

def run(i):
    return open_run(Path.cwd() / 'data' / str(i))

g7 = run(7)
print(summarize_run(g7))
B7 = g7.col('magnet_field')
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(B7, g7.col('sr0_X'), lw=0.7)
ax[0].set_ylabel('raw sr0 X (V)')
ax[1].plot(B7, g7.col('sr1_X') * 1e6, lw=0.7)
ax[1].set_ylabel('raw sr1 X (µV)')
ax[1].set_xlabel('B (T)')
fig.suptitle('data/7 — raw lock-in channels, hole spot')
fig.tight_layout(); plt.show()

R7 = np.abs(g7.col('sr1_X') / (g7.col('sr0_X') / g7.meta['measurement_config']['sr0_gain']))
ix7 = np.argsort(B7); B7s, R7s = B7[ix7], R7[ix7]
f7, spec7 = sdh_fft(R7s[:, None], B7s, b_range=(2, 10), nfft=2048, bg_degree=5, log=False)
p7, _ = find_peaks(spec7[0]); p7 = sorted((j for j in p7 if 4 < f7[j] < 40), key=lambda j: -spec7[0, j])[:6]
print('data/7: Rxx median/max %.1f/%.1f Ω; |I_gate|max TG/BG %.3f/%.3f nA' %
      (np.median(R7), np.max(R7), 1e9*np.max(np.abs(g7.col('k_2400_tg_curr'))), 1e9*np.max(np.abs(g7.col('k_2400_bg_curr')))))
print('FFT peaks, 2–10 T: ', [(round(float(f7[j]), 2), round(float(spec7[0, j]), 1)) for j in p7])
try: print(sdh_onset(R7s, B7s, b_lo=1.0, b_hi=10.0, r_full_scale=5000).summary())
except ValueError as err: print('onset unavailable:', err)
fig, ax = plt.subplots(2, 1, figsize=(9, 6))
ax[0].plot(B7s, R7s, lw=0.7); ax[0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title='data/7 — measured-current resistance')
ax[1].plot(f7, spec7[0]); ax[1].set(xlim=(0, 45), xlabel='SdH frequency (T)', ylabel='FFT magnitude (a.u.)', title='2–10 T; B-polynomial background removed')
for j in p7[:4]: ax[1].axvline(f7[j], ls=':', lw=0.8)
fig.tight_layout(); plt.show()
