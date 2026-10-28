from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
for rid,n in [(6,3.2),(7,-1.2)]:
    r=open_run(f'data/{rid}')
    ch={c.cid:c for c in resolve_channels(r.meta)}
    B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
    R=r.col('sr1_X')/ch['sr1'].gain/I
    order=np.argsort(B); B,R=B[order],R[order]
    print(f'RUN {rid}, n={n}: complete={r.complete}, interrupted={r.interrupted}, R={R.min():.2f}..{R.max():.2f} Ohm, I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, wall={np.ptp(r.col("time")):.1f}s')
    fig,axs=plt.subplots(2,2,figsize=(12,7))
    axs[0,0].plot(B,R);axs[0,0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'Run {rid}: raw signed Rxx B1-B2')
    for k in ['k_2400_tg_curr','k_2400_bg_curr']: axs[0,1].plot(r.col('magnet_field'),r.col(k)*1e12,label=k)
    axs[0,1].set(xlabel='B (T)',ylabel='gate current (pA)');axs[0,1].legend()
    try:
        on=sdh_onset(R,B,r_full_scale=5000)
        print(on.summary())
        for t in on.tones: axs[1,0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
        axs[1,0].axhline(5,color='k',ls=':');axs[1,0].legend();axs[1,0].set(xlabel='B center (T)',ylabel='tone SNR')
    except SdhOnsetError as e: print('ONSET ERROR:',e)
    for blo in [0.8,1.0,1.5,2.0]:
        for degree in [3,5]:
            f,spec=sdh_fft(R[:,None],B,b_range=(blo,10),bg_degree=degree,log=False,nfft=2048)
            pk,_=find_peaks(spec[0]);pk=sorted([p for p in pk if 3<f[p]<65],key=lambda p:spec[0,p],reverse=True)[:5]
            print(f'FFT B={blo}-10 degree={degree}:',[(round(float(f[p]),2),round(float(spec[0,p]),1)) for p in pk])
            if degree==5: axs[1,1].plot(f,spec[0]/max(spec[0]),label=f'{blo}-10 T')
    axs[1,1].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT');axs[1,1].legend()
    fig.tight_layout();fig.savefig(f'hera_scratch/spot_run{rid}.png',dpi=140);plt.show()
