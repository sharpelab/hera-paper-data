from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
out=Path('hera_scratch')
for fid in (6,7):
    r=open_run(f'data/{fid}')
    fig=plot_raw(r); fig.savefig(out/f'spot_{fid}_raw.png'); plt.close(fig)
    cs=resolve_channels(r.meta); c=current_channel(cs); v=next(c for c in cs if c.cid=='sr1')
    B=r.col('magnet_field'); R=(r.col(v.col)/v.gain)/(r.col(c.col)/c.gain)
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    axs[0,0].plot(B,R,'.-',ms=2); axs[0,0].set(xlim=(0,3),ylim=(-30,350),xlabel='B (T)',ylabel='Signed Rxx (Ohm)')
    for lo,hi in ((1,4),(1.2,6),(1.5,10)):
        for degree in (3,5):
            f,a=sdh_fft(R[:,None],B,b_range=(lo,hi),bg_degree=degree,log=False,nfft=4096)
            axs[0,1].plot(f,a[0]/max(a[0]),label=f'{lo}-{hi} T, p{degree}')
            idx,_=find_peaks(a[0]); idx=sorted((k for k in idx if 3<f[k]<45),key=lambda k:a[0,k],reverse=True)[:6]
            print(fid,lo,hi,degree,'peaks',[(round(f[k],2),round(a[0,k]/max(a[0]),2)) for k in idx])
    for hi in (3,4,6,10):
        try:
            on=sdh_onset(R,B,b_hi=hi,r_full_scale=5000)
            print(fid,'hi',hi,on.summary())
            for t in on.tones[:2]: axs[1,0].plot(t.b_centers,t.snr,'.-',label=f'hi {hi} f {t.freq:.1f}')
        except ValueError as e: print(e)
    axs[1,1].plot(B,r.col('sr1_P'),'.-',ms=2); axs[1,1].set(xlabel='B (T)',ylabel='sr1 phase (deg)')
    axs[0,1].set(xlim=(0,45),xlabel='Frequency (T)',ylabel='Normalized FFT'); axs[0,1].legend(fontsize=7)
    axs[1,0].set(xlabel='B (T)',ylabel='Tone SNR'); axs[1,0].legend(fontsize=7)
    fig.suptitle(f'Run {fid}: B_1-B_2 spot check'); fig.tight_layout(); fig.savefig(out/f'spot_{fid}_review.png'); plt.close(fig)
