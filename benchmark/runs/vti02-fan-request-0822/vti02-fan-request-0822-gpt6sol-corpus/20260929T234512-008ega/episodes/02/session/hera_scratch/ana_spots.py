from hera.analysis import open_run, summarize_run, sdh_fft, sdh_onset
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

_sp = {}
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, rid in enumerate((6, 7)):
    run = open_run(f'data/{rid}')
    B = run.col('magnet_field')
    R = run.col('sr1_X') / (run.col('sr0_X') / -1e6)
    _sp[rid] = (B, R)
    print(summarize_run(run))
    print(f'run {rid}: T {run.col("T_sample").min():.3f}–{run.col("T_sample").max():.3f} K, '
          f'|Rxx|max {np.max(np.abs(R)):.1f} ohm, '
          f'|I_tg/bg|max {np.max(np.abs(run.col("k_2400_tg_curr")))*1e12:.0f}/'
          f'{np.max(np.abs(run.col("k_2400_bg_curr")))*1e12:.0f} pA')
    ax[j].plot(B, R, '.', ms=1.5)
    ax[j].set(xlabel='B (T)', ylabel='Rxx (ohm)', title=f'run {rid}: raw Rxx')
fig.tight_layout(); plt.show()

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, rid in enumerate((6, 7)):
    B, R = _sp[rid]
    for lo, hi in ((0.8, 10), (1.0, 10), (1.5, 10)):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=4096,
                       bg_degree=3, log=False)
        spec = s[0]
        ax[j].plot(f, spec / np.max(spec), label=f'{lo:g}–{hi:g} T')
        if lo == 1.0:
            peaks, _ = find_peaks(spec, prominence=.06 * np.max(spec))
            peaks = sorted((p for p in peaks if 3 < f[p] < 40),
                           key=lambda p: -spec[p])[:6]
            print(f'run {rid}, B=1–10 T, bg degree 3: '
                  + ', '.join(f'{f[p]:.1f} T' for p in peaks))
    ax[j].set(xlim=(0, 42), xlabel='frequency (T)', ylabel='normalized FFT magnitude',
              title=f'run {rid}: window stability')
    ax[j].legend()
fig.tight_layout(); plt.show()

_on = sdh_onset(np.abs(_sp[6][1]), _sp[6][0], r_full_scale=5000, b_lo=.3)
print('Run 6 onset diagnostic (censored low-field tone; use with the raw/spectral check):')
print(_on.summary())
