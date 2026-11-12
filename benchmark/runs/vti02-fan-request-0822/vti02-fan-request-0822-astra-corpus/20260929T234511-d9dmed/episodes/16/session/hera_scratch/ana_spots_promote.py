from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft
for rid,n in [(6,3.2),(7,-1.2)]:
    r=open_run(Path('data')/str(rid))
    plot_raw(r); plt.show()
    B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
    on=sdh_onset(R,B,r_full_scale=5000)
    print(f'Run {rid}, n={n}e12, D=0; '+on.summary())
    fig,ax=plt.subplots(1,2,figsize=(11,4))
    for lo in [1.,2.,3.]:
        f,a=sdh_fft(R[:,None],B,b_range=(lo,10.),log=False,nfft=2048)
        ax[0].plot(f,a[0]/a[0].max(),label=f'B >= {lo:g} T')
    ax[0].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT');ax[0].legend()
    for t in on.tones: ax[1].semilogy(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
    ax[1].axhline(5,color='k',ls=':');ax[1].set(xlabel='B (T)',ylabel='matched-filter SNR');ax[1].legend(fontsize=7)
    plt.tight_layout();plt.show()
print('Read: sr1 / B_1-B_2 remains unclassified. Candidate electron tones near 7, 22, 29 T include a harmonic/sum-tone ambiguity; no pocket count assigned. Default onset for run 6 is censored at 0.3 T, where the 50 mT sampling fails Nyquist. Run 7 onset ~0.71 T is close to its 20 mT sampling floor, and the allowed hole density is in the close-pair model regime. Acquire an electron low-field extension before designing the fan; retain raw signed R (negative portions exist), not log-clipped R. No B-reversal symmetrization is available. Calibration and possible secondary CNP remain systematic uncertainties.')
