from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft

for fid, density in [(6,3.2),(7,-1.2)]:
    r = open_run(Path('data')/str(fid))
    plot_raw(r)
    plt.show()
    B=r.col('magnet_field')
    I=r.col('sr0_X')/(-1e6)
    R=r.col('sr1_X')/I
    print(f'Run {fid}: n={density:+.2f}e12, D~0; complete={r.complete}, interrupted={r.interrupted}; '
          f'R=[{R.min():.2f},{R.max():.2f}] ohm; I=[{I.min()*1e9:.3f},{I.max()*1e9:.3f}] nA; '
          f'T=[{r.col("T_sample").min():.3f},{r.col("T_sample").max():.3f}] K')
    print('Gate current maxima (pA):',*[round(np.max(np.abs(r.col(k)))*1e12,1) for k in ['k_2400_tg_curr','k_2400_bg_curr']])
    on=sdh_onset(R,B,r_full_scale=5000)
    print(on.summary())
    print('Onset sensitivity to B-background degree:')
    for degree in [2,3,4,5,6]:
        check=sdh_onset(R,B,r_full_scale=5000,bg_degree=degree)
        print(degree, round(check.onset_b,4), 'T', 'carrier',round(check.onset_freq,2))
    fig,axs=plt.subplots(2,1,figsize=(11,7))
    axs[0].plot(B,R,'.-',ms=2)
    axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {fid}, B1-B2: raw measured-current-normalized resistance')
    for lo in [1,1.5,2,3]:
        f,spec=sdh_fft(R[:,None],B,b_range=(lo,8),bg_degree=3,log=False,nfft=4096)
        y=spec[0]; axs[1].plot(f,y/y.max(),label=f'{lo}-8 T')
    axs[1].axvline(abs(density)*10.33916924,color='k',ls='--',label='F_L, geometry scale')
    axs[1].set(xlim=(0,55),xlabel='Frequency (T)',ylabel='Normalized FFT (linear R)')
    axs[1].legend();fig.tight_layout();plt.show()
