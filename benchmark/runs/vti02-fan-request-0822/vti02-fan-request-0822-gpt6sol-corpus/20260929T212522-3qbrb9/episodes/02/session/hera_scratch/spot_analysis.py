"""Raw and frequency read of in-session SdH spot checks 6 and 7."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

fig, axs = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
for row, (file_id, n, side) in enumerate(((6, 3.2, 'electron'), (7, -1.2, 'hole'))):
    r = open_run(f'data/{file_id}')
    B = r.col('magnet_field')
    R = r.col('sr1_X') / 1e-8
    T = r.col('T_sample')
    Itg = r.col('k_2400_tg_curr')
    Ibg = r.col('k_2400_bg_curr')
    ax = axs[row, 0]
    ax.plot(B, R, lw=1)
    ax.set(xlabel='B (T)', ylabel='Rxx (Ω)', title=f'run {file_id} raw, {side} n={n:+.1f}e12')
    ax.grid(alpha=.25)
    print(f'run {file_id}: B {B[0]:.3f} -> {B[-1]:.3f}, R {R.min():.2f} .. {R.max():.2f} Ω, T {T.min():.3f} .. {T.max():.3f} K, Itg median {np.median(Itg)*1e12:.1f} pA, Ibg median {np.median(Ibg)*1e12:.1f} pA')
    try:
        onset = sdh_onset(R, B, r_full_scale=5000)
        print(f'  onset {onset.onset_b:.3f} T, carrier {onset.onset_freq:.2f} T; tones:')
        for t in onset.tones:
            print(f'    {t.freq:.2f} T, onset {t.onset_b:.2f}, periods {t.n_periods:.1f}, contrast {t.contrast:.1f}, marginal {t.marginal}, residual {t.near_residual}, harmonic {t.harmonic_of}')
        print('  untracked', onset.untracked)
    except Exception as exc:
        print(f'  onset ERROR: {type(exc).__name__}: {exc}')
    for blo in ((2.0, 3.0) if file_id == 6 else (1.0, 2.0)):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, 10), bg_degree=5, log=False, nfft=4096)
        spectrum = sp[0]
        peaks, props = find_peaks(spectrum, prominence=max(spectrum[(f>3)&(f<50)])*.04)
        peaks = peaks[(f[peaks] > 3) & (f[peaks] < 50)]
        peaks = sorted(peaks, key=lambda i: spectrum[i], reverse=True)[:8]
        print(f'  FFT B={blo}-10 T: '+', '.join(f'{f[i]:.2f}T({spectrum[i]:.1f})' for i in peaks))
        if blo == ((2.0) if file_id == 6 else (1.0)):
            axs[row,1].plot(f, spectrum / np.max(spectrum[(f>3)&(f<50)]), lw=1)
    fl = luttinger_frequency(abs(n))
    axs[row,1].axvline(fl, color='k', ls='--', lw=1, label=f'F_L={fl:.1f} T')
    axs[row,1].set(xlim=(0, 50), xlabel='F (T)', ylabel='FFT (normalized)', title=f'run {file_id} FFT, B≥{2 if file_id==6 else 1} T')
    axs[row,1].legend()
    axs[row,1].grid(alpha=.25)
fig.savefig('hera_scratch/spot_checks_raw_fft.png', dpi=170)
