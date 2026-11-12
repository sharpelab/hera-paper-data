from hera.analysis import open_run, sdh_onset, sdh_fft
import numpy as np
from scipy.signal import find_peaks
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for row, fid in enumerate((6, 7)):
    run = open_run(f'data/{fid}')
    b = run.col('magnet_field')
    r = run.col('sr1_X') / 1e-8
    order = np.argsort(b)
    b, r = b[order], r[order]
    print('RUN', fid, 'complete', run.complete, 'B', b[0], b[-1], 'R range', np.min(r), np.median(r), np.max(r),
          'T range', np.min(run.col('T_sample')), np.max(run.col('T_sample')),
          'TG/BG I maxima', np.max(np.abs(run.col('k_2400_tg_curr'))), np.max(np.abs(run.col('k_2400_bg_curr'))))
    axes[row, 0].plot(b, r, lw=.75)
    axes[row, 0].set(xlabel='B (T)', ylabel='Rxx (ohm)', title=f'Run {fid} raw')
    for cut in (0.3, 0.7, 1.0, 1.5, 2.0):
        try:
            onset = sdh_onset(r, b, b_lo=cut, r_full_scale=5000)
            print('ONSET', fid, cut, onset.summary())
        except Exception as exc:
            print('ONSET ERROR', fid, cut, repr(exc))
    for cut in (1.5, 2.0, 2.5, 3.0):
        try:
            f, spec = sdh_fft(r[:, None], b, b_range=(cut, 10), nfft=4096, log=False)
            y = spec[0]
            peaks, _ = find_peaks(y, prominence=np.max(y) * .05)
            peaks = [j for j in peaks if 2 < f[j] < 50]
            peaks.sort(key=lambda j: y[j], reverse=True)
            print('FFT', fid, cut, [(round(f[j], 2), round(y[j]/np.max(y), 3)) for j in peaks[:8]])
            if cut == 2.0:
                axes[row, 1].plot(f, y)
                axes[row, 1].set(xlim=(0, 45), xlabel='frequency (T)', ylabel='FFT amplitude', title=f'Run {fid}, B>2 T')
        except Exception as exc:
            print('FFT ERROR', fid, cut, repr(exc))
fig.tight_layout()
fig.savefig('hera_scratch/spot_read.png', dpi=160)
