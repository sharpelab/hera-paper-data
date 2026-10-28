from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, plot_raw, sdh_onset, sdh_fft

for rid in (6, 7):
    run = open_run(f'data/{rid}')
    print(summarize_run(run))
    print('channels', run.cols)
    meta = run.meta
    pars = meta['instruments']['sr1']['snapshot']['parameters']
    amp = float(pars['amplitude']['value'])
    sens = float(pars['sensitivity']['value'])
    tau = float(pars['time_constant']['value'])
    slope = pars['filter_slope']['value']
    ib = amp / meta['measurement_config']['bias_resistor']
    B = run.col('magnet_field')
    R = run.col('sr1_X') / ib
    print(f'run {rid}: amp={amp} I_bias={ib:.4g} sens={sens:g} tau={tau:g} slope={slope}, R range={R.min():.3g}..{R.max():.3g}, FS={sens/ib:.3g}, max |R|/FS={max(abs(R))/ (sens/ib):.3f}')
    print(f'T range={run.col("T_sample").min():.3f}..{run.col("T_sample").max():.3f}; I_tg max={max(abs(run.col("k_2400_tg_curr"))):.3g}, I_bg max={max(abs(run.col("k_2400_bg_curr"))):.3g}')
    fig, axs = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    axs[0].plot(B, R, lw=.7); axs[0].set_ylabel('Raw Rxx (ohm)')
    axs[1].plot(B, run.col('sr0_X'), lw=.7); axs[1].set_xlabel('B (T)'); axs[1].set_ylabel('Raw drain X (V)')
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{rid}_raw.png', dpi=140); plt.close(fig)
    try:
        on = sdh_onset(R, B, r_full_scale=sens/ib)
        print('onset', on.summary())
        print('onset_b', on.onset_b, 'clip_high_b', on.clip_high_b)
        if hasattr(on, 'tones'):
            for tone in on.tones: print('tone', tone)
        for lo in (on.onset_b, max(on.onset_b, 2), max(on.onset_b, 3)):
            hi = min(10, on.clip_high_b)
            if lo >= hi: continue
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), log=False)
            y = sp[0]
            pk, _ = find_peaks(y)
            pk = sorted((i for i in pk if 3 < f[i] < 50), key=lambda i: y[i], reverse=True)[:8]
            print(f'FFT {lo:.2f}..{hi:.2f}:', [(round(float(f[i]),2), round(float(y[i]),3)) for i in pk])
    except Exception as e:
        print('onset/FFT ERROR', type(e).__name__, e)
