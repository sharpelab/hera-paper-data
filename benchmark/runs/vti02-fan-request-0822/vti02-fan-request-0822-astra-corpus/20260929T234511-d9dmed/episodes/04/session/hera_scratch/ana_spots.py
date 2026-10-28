from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, plot_raw, sdh_onset, sdh_fft, summarize_run

for rid, n in [(6, 3.2), (7, -1.2)]:
    r = open_run(Path('data') / str(rid))
    print(summarize_run(r))
    plot_raw(r); plt.show()  # Native TSV, signed R and measured drain current FIRST.
    channels = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col('sr0_X') / channels['sr0'].gain
    R = (r.col('sr1_X') / channels['sr1'].gain) / I
    B = r.col('magnet_field')
    print(f'Elapsed {np.ptp(r.col("time"))/60:.2f} min; R {R.min():.2f}..{R.max():.2f} ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    print(f'T_sample {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K; peak |TG/BG current| {np.max(abs(r.col("k_2400_tg_curr")))*1e12:.1f}/{np.max(abs(r.col("k_2400_bg_curr")))*1e12:.1f} pA')
    on = sdh_onset(R, B, r_full_scale=5000)
    print('Full-record onset (all flags retained):\n' + on.summary())
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    if rid == 6:
        # Sensitivity check, not a replacement of the censored full-record result.
        # High-field MR is large; use the measured low-B record to isolate onset.
        for deg in (3, 5):
            local = sdh_onset(R, B, b_hi=4, bg_degree=deg, r_full_scale=5000)
            print(f'Low-field-only onset, B <= 4 T, degree {deg}:\n' + local.summary())
            for tone in local.tones:
                if 6 < tone.freq < 8:
                    ax[0].plot(tone.b_centers, tone.snr, 'o-', label=f'{tone.freq:.2f} T, degree {deg}')
        cuts = (1.03, 1.5, 2.0)
    else:
        cuts = (on.onset_b, 1.0, 1.5)
        for tone in on.tones[:3]:
            ax[0].plot(tone.b_centers, tone.snr, 'o-', label=f'{tone.freq:.2f} T')
    ax[0].axhline(5, color='k', ls=':'); ax[0].set(xlabel='B (T)', ylabel='matched-filter SNR', yscale='log'); ax[0].legend(fontsize=8)
    for cutoff in cuts:
        for deg in (3,5):
            f, spec = sdh_fft(R[:,None], B, b_range=(cutoff,10), bg_degree=deg, nfft=2048, log=False)
            band = (f > 3) & (f < 65)
            norm = spec[0,band].max()
            ax[1].plot(f, spec[0]/norm, label=f'B>={cutoff:.2f}, degree {deg}')
            pk, _ = find_peaks(spec[0]); pk = [p for p in pk if band[p]]
            pk = sorted(pk, key=lambda p:-spec[0,p])[:5]
            print(f'FFT cutoff={cutoff:.2f} degree={deg}: candidate peaks {[round(float(f[p]),2) for p in pk]} T')
    ax[1].axvline(abs(n)*10.33916924, color='k', ls=':', label='nominal g=4 F_L')
    ax[1].set(xlim=(0,65), ylim=(0,1.15), xlabel='F (T)', ylabel='FFT / max above 3 T')
    ax[1].legend(fontsize=7); fig.suptitle(f'Run {rid}: onset and FFT sensitivity, signed R; no B symmetrization available')
    fig.tight_layout(); plt.show()
