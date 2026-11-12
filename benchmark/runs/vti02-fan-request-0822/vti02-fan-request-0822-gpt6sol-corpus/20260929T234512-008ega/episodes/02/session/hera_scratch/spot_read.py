from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft

for rid in (6, 7):
    run = open_run(Path('data') / str(rid))
    B = run.col('magnet_field')
    R = run.col('sr1_X') / (run.col('sr0_X') / -1e6)
    I = run.col('sr0_X') / -1e6
    print(summarize_run(run))
    print('B', B.min(), B.max(), 'R abs quantiles', np.quantile(abs(R), [0, .1, .5, .9, .99, 1]),
          'I nA', np.quantile(I * 1e9, [0, .5, 1]),
          'T', np.quantile(run.col('T_sample'), [0, .5, 1]))
    print('gate I pA maxima', max(abs(run.col('k_2400_tg_curr'))) * 1e12,
          max(abs(run.col('k_2400_bg_curr'))) * 1e12)
    try:
        on = sdh_onset(abs(R), B, r_full_scale=5000, b_lo=.3)
        print(on.summary())
    except Exception as e:
        print('onset failure', type(e).__name__, str(e))
    for lo in (1.5, 2, 2.5, 3, 4):
        f, sp = sdh_fft(abs(R)[:, None], B, b_range=(lo, 10), nfft=4096,
                        bg_degree=5, log=False)
        spec = sp[0]
        p, props = find_peaks(spec, prominence=max(spec) * .04)
        p = [j for j in p if 3 <= f[j] <= 45]
        p = sorted(p, key=lambda j: -spec[j])[:8]
        print('FFT', lo, [(round(f[j], 2), round(spec[j] / max(spec), 3)) for j in p])
