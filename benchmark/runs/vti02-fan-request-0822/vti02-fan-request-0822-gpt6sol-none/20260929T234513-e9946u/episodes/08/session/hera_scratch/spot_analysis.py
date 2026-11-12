from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for row, rid in enumerate((6, 7)):
    run = open_run(Path('data') / str(rid))
    channels = resolve_channels(run.meta)
    ci = current_channel(channels)
    cv = next(c for c in channels if c.cid == 'sr1')
    I = run.col(ci.col) / ci.gain
    R = (run.col(cv.col) / cv.gain) / I
    B = run.col('magnet_field')
    T = run.col('T_sample')
    print(f'run {rid}: rows {run.rows}, B {B[0]:.3f}->{B[-1]:.3f} T, T {np.median(T):.3f} [{T.min():.3f},{T.max():.3f}] K')
    print(f'  I {np.median(I)*1e9:.3f} nA, R med {np.median(R):.2f} Ohm, range {R.min():.2f}..{R.max():.2f}, max fs {np.max(np.abs(run.col(cv.col)))/50e-6:.3f}')
    print(f'  TG |I| p99 {np.percentile(np.abs(run.col("k_2400_tg_curr")), 99)*1e12:.0f} pA, BG p99 {np.percentile(np.abs(run.col("k_2400_bg_curr")), 99)*1e12:.0f} pA')
    sort = np.argsort(B)
    B, R = B[sort], R[sort]
    axes[row, 0].plot(B, R, lw=.8)
    axes[row, 0].set(xlabel='B (T)', ylabel='Rxx (Ohm)', title=f'run {rid}: raw, measured-current normalized')
    try:
        o = sdh_onset(R, B, b_lo=1.0, b_hi=10.0, r_full_scale=5000, f_min=3.0)
        print('  onset:', o.summary())
    except SdhOnsetError as exc:
        print('  onset failed:', exc)
    f, spec = sdh_fft(R[:, None], B, b_range=(2.0, 10.0), log=False, nfft=2048, bg_degree=5)
    a = spec[0]
    pk, _ = find_peaks(a)
    pk = sorted((p for p in pk if 3 < f[p] < 60), key=lambda p: a[p], reverse=True)[:8]
    print('  FFT peaks 2-10T:', [(round(float(f[p]),2), round(float(a[p]),2)) for p in pk])
    axes[row, 1].plot(f, a)
    axes[row, 1].set(xlim=(0, 60), xlabel='frequency (T)', ylabel='FFT magnitude', title=f'run {rid}: 2-10 T detrended')
fig.tight_layout()
fig.savefig('hera_scratch/spot_analysis.png', dpi=140)
