from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
from scipy.signal import find_peaks
from hera.analysis import sdh_fft, sdh_onset

def run(i):
    return open_run(Path.cwd() / 'data' / str(i))

g6 = run(6)
print(summarize_run(g6))
B6 = g6.col('magnet_field')
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(B6, g6.col('sr0_X'), lw=0.7)
ax[0].set_ylabel('raw sr0 X (V)')
ax[1].plot(B6, g6.col('sr1_X') * 1e6, lw=0.7)
ax[1].set_ylabel('raw sr1 X (µV)')
ax[1].set_xlabel('B (T)')
fig.suptitle('data/6 — raw lock-in channels, electron spot')
fig.tight_layout(); plt.show()

R6 = np.abs(g6.col('sr1_X') / (g6.col('sr0_X') / g6.meta['measurement_config']['sr0_gain']))
ix6 = np.argsort(B6); B6s, R6s = B6[ix6], R6[ix6]
f6, spec6 = sdh_fft(R6s[:, None], B6s, b_range=(2, 10), nfft=2048, bg_degree=5, log=False)
p6, _ = find_peaks(spec6[0]); p6 = sorted((j for j in p6 if 4 < f6[j] < 40), key=lambda j: -spec6[0, j])[:6]
print('data/6: Rxx median/max %.1f/%.1f Ω; |I_gate|max TG/BG %.3f/%.3f nA' %
      (np.median(R6), np.max(R6), 1e9*np.max(np.abs(g6.col('k_2400_tg_curr'))), 1e9*np.max(np.abs(g6.col('k_2400_bg_curr')))))
print('FFT peaks, 2–10 T: ', [(round(float(f6[j]), 2), round(float(spec6[0, j]), 1)) for j in p6])
try: print(sdh_onset(R6s, B6s, b_lo=1.0, b_hi=10.0, r_full_scale=5000).summary())
except ValueError as err: print('onset unavailable:', err)
fig, ax = plt.subplots(2, 1, figsize=(9, 6))
ax[0].plot(B6s, R6s, lw=0.7); ax[0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title='data/6 — measured-current resistance')
ax[1].plot(f6, spec6[0]); ax[1].set(xlim=(0, 45), xlabel='SdH frequency (T)', ylabel='FFT magnitude (a.u.)', title='2–10 T; B-polynomial background removed')
for j in p6[:4]: ax[1].axvline(f6[j], ls=':', lw=0.8)
fig.tight_layout(); plt.show()
