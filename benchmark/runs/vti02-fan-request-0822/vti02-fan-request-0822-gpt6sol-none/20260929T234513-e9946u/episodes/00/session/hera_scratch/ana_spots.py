import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_fft, sdh_onset
from scipy.signal import find_peaks

file_path = Path.cwd() / 'data'
def run(i):
    return open_run(file_path / str(i))

fig, ax = plt.subplots(2, 2, figsize=(12, 7), sharex='row')
for row, rid in enumerate((6, 7)):
    rr = run(rid)
    bb = rr.col('magnet_field')
    ii = rr.col('sr0_X') / rr.meta['measurement_config']['sr0_gain']
    rxx = rr.col('sr1_X') / ii
    ax[row, 0].plot(bb, rxx, lw=.75)
    ax[row, 0].set_ylabel(f'run {rid}: Rxx (Ω)')
    ax[row, 1].plot(bb, ii*1e9, lw=.75)
    ax[row, 1].set_ylabel('drain current (nA)')
    ax[row, 0].grid(alpha=.2); ax[row, 1].grid(alpha=.2)
    print(f'run {rid}: {rr.rows} points, B {bb.min():.2f}–{bb.max():.2f} T, Rxx {rxx.min():.0f}–{rxx.max():.0f} Ω, '
          f'I median {np.median(ii)*1e9:.3f} nA, T {rr.col("T_sample").min():.3f}–{rr.col("T_sample").max():.3f} K, '
          f'TG/BG max |I| {np.max(np.abs(rr.col("k_2400_tg_curr")))*1e12:.0f}/'
          f'{np.max(np.abs(rr.col("k_2400_bg_curr")))*1e12:.0f} pA')
for a in ax[-1]: a.set_xlabel('B (T)')
fig.suptitle('Raw SdH spot data: calibrated D_A = 0')
fig.tight_layout(); plt.show()

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, rid in enumerate((6, 7)):
    rr = run(rid); bb = rr.col('magnet_field')
    ii = rr.col('sr0_X') / rr.meta['measurement_config']['sr0_gain']
    rxx = rr.col('sr1_X') / ii
    ff, ss = sdh_fft(rxx[:, None], bb, b_range=(1.5, 9.8), nfft=2048, bg_degree=3, log=False)
    sp = ss[0]; pp, _ = find_peaks(sp)
    pp = sorted((p for p in pp if 3 < ff[p] < 70), key=lambda p: sp[p], reverse=True)[:5]
    ax[j].plot(ff, sp); ax[j].set_xlim(0, 65); ax[j].set_xlabel('SdH frequency (T)'); ax[j].set_ylabel('FFT magnitude (Ω)')
    ax[j].set_title(f'run {rid}, B 1.5–9.8 T')
    for p in pp[:4]: ax[j].annotate(f'{ff[p]:.1f}', (ff[p], sp[p]), fontsize=8)
    print(f'run {rid} FFT peaks: '+', '.join(f'{ff[p]:.1f} T' for p in pp))
    try:
        onset = sdh_onset(rxx, bb, b_lo=1.0, b_hi=9.8, r_full_scale=5000)
        print(onset.summary())
    except Exception as exc:
        print(f'run {rid} onset unresolved: {type(exc).__name__}: {exc}')
fig.tight_layout(); plt.show()
