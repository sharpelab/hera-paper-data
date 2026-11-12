import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for fid in (6,7):
    r=open_run(f'data/{fid}')
    display(plot_raw(r)); plt.close()
    ch={c.cid:c for c in resolve_channels(r.meta)}
    I=r.col('sr0_X')/ch['sr0'].gain
    R=(r.col('sr1_X')/ch['sr1'].gain)/I
    B=r.col('magnet_field')
    print(f'run {fid}: complete={r.complete}, interrupted={r.interrupted}; R={R.min():.2f}..{R.max():.2f} Ohm; drain={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    for col in ('k_2400_tg_curr','k_2400_bg_curr','T_sample'):
        print(col, np.min(r.col(col)), np.max(r.col(col)))
    print('Full record onset diagnostic:'); print(sdh_onset(R,B,r_full_scale=5000).summary())
    print('Low-field onset diagnostic (exclude large high-field MR from background fit):')
    on=sdh_onset(R,B,b_hi=4,r_full_scale=5000); print(on.summary())
    fig,ax=plt.subplots(1,2,figsize=(12,4))
    for hi in (4,6,10):
        sel=(B>=0.3)&(B<=hi); bs=B[sel]; rs=R[sel]
        bg=np.polynomial.Polynomial.fit(bs,rs,5)
        ax[0].plot(bs,rs-bg(bs),label=f'fit to {hi} T',lw=.7)
    ax[0].set(xlim=(.3,4),xlabel='B (T)',ylabel='R minus polynomial in B (Ohm)'); ax[0].legend(fontsize=7)
    for lo in (1.,1.5):
        for deg in (3,5):
            f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
            ax[1].plot(f,sp[0]/sp[0].max(),label=f'B>{lo}, degree {deg}')
            p,_=find_peaks(sp[0],prominence=.03*sp[0].max())
            p=sorted(p,key=lambda j:sp[0,j],reverse=True)[:7]
            print('FFT',lo,deg,[(round(float(f[j]),2),round(float(sp[0,j]/sp[0].max()),3)) for j in p])
    ax[1].set(xlim=(0,65),xlabel='F (T)',ylabel='FFT amplitude / maximum'); ax[1].legend(fontsize=7)
    fig.suptitle(f'Run {fid}: extraction stability; frequency-bin spacing is not precision')
    fig.tight_layout(); display(fig); plt.close(fig)
