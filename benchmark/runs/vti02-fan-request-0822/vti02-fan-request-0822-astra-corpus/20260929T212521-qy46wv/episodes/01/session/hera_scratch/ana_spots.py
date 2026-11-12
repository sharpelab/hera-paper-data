import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
from scipy.signal import find_peaks

for fid, density in [(6, 3.2), (7, -1.2)]:
    run_s = open_run(f'data/{fid}')
    channels_s = {c.cid:c for c in resolve_channels(run_s.meta)}
    field_s = run_s.col('magnet_field')
    current_s = run_s.col('sr0_X') / channels_s['sr0'].gain
    resistance_s = (run_s.col('sr1_X') / channels_s['sr1'].gain) / current_s
    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    axes[0,0].plot(field_s, resistance_s)
    axes[0,0].set(ylabel='Signed Rxx B1-B2 (Ohm)', title=f'Run {fid}, n={density:+.1f}, D=0')
    axes[0,1].plot(field_s, current_s*1e9); axes[0,1].set_ylabel('Drain current (nA)')
    for col in ['k_2400_tg_curr','k_2400_bg_curr']:
        axes[1,0].plot(field_s, run_s.col(col)*1e12, label=col)
    axes[1,0].set_ylabel('Gate current (pA)'); axes[1,0].legend()
    axes[1,1].plot(field_s, run_s.col('T_sample')); axes[1,1].set_ylabel('Sample T (K)')
    for a in axes.flat: a.set_xlabel('B (T)')
    fig.tight_layout(); plt.show()
    print(f'Run {fid}: complete={not run_s.interrupted}, Rxx={resistance_s.min():.2f}..{resistance_s.max():.2f} Ohm; I={current_s.min()*1e9:.3f}..{current_s.max()*1e9:.3f} nA')
    # The full 0.3-10 T background fit is shown as a diagnostic, not silently accepted.
    print('Full-window onset diagnostic:')
    print(sdh_onset(resistance_s, field_s, r_full_scale=5000).summary())
    fig, axes = plt.subplots(1, 2, figsize=(12,4))
    for degree_s in [3,5,7]:
        if fid == 6:
            onset_s = sdh_onset(resistance_s, field_s, b_hi=5, f_min=4, bg_degree=degree_s, r_full_scale=5000)
            print(f'0.3-5 T onset, degree {degree_s}:\n{onset_s.summary()}')
            for tone_s in onset_s.tones:
                if 6 < tone_s.freq < 8:
                    axes[0].plot(tone_s.b_centers,tone_s.snr,label=f'{tone_s.freq:.2f} T, degree {degree_s}')
        for lower_s in [1.5, 2.0]:
            freq_s, spec_s = sdh_fft(resistance_s[:,None], field_s, b_range=(lower_s,6.5), bg_degree=degree_s, log=False, nfft=4096)
            mask_s=(freq_s>4)&(freq_s<45)
            axes[1].plot(freq_s,spec_s[0]/max(spec_s[0,mask_s]),label=f'{lower_s}-6.5 T, degree {degree_s}')
    axes[0].axhline(5,color='k',ls=':'); axes[0].set(xlabel='B (T)',ylabel='Matched-filter SNR')
    if fid==6: axes[0].legend(fontsize=7)
    axes[1].axvline(abs(density)*10.33916924,color='k',ls='--',label='nominal F_L')
    axes[1].set(xlim=(4,45),ylim=(0,1.2),xlabel='F (T)',ylabel='FFT / maximum in 4-45 T'); axes[1].legend(fontsize=7)
    fig.tight_layout(); plt.show()
