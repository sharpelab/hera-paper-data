import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft
for fid,n in ((6,3.2),(7,-1.2)):
    r=open_run(f'data/{fid}')
    display(plot_raw(r)); plt.close()
    ch={c.cid:c for c in resolve_channels(r.meta)}
    I=r.col('sr0_X')/ch['sr0'].gain
    R=r.col('sr1_X')/ch['sr1'].gain/I; B=r.col('magnet_field')
    print(f'Run {fid}: n={n:+.1f}e12, D=0; complete={r.complete}, interrupted={r.interrupted}')
    print(f'R range {R.min():.2f}..{R.max():.2f} ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    print(sdh_onset(R,B,r_full_scale=5000).summary())
    fig,ax=plt.subplots(figsize=(9,4))
    for lo in (1.0,1.5,2.0):
        for degree in (3,5,7):
            f,p=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=degree,nfft=4096,log=False)
            ax.plot(f,p[0]/np.max(p),label=f'B>{lo}, degree {degree}',alpha=.65)
    ax.axvline(abs(n)*10.33916924,color='k',ls='--',label='geometry-prior F_L')
    ax.set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT magnitude',title=f'Run {fid}: extraction stability (positive B only)')
    ax.legend(fontsize=7,ncol=2); fig.tight_layout(); display(fig); plt.close(fig)
print('No stacking verdict yet: harmonics, breakdown, and the second CNP ridge remain confounds. Positive-B-only data cannot remove odd-in-B admixture.')
