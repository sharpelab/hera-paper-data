import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
from scipy.signal import find_peaks
for fid,n in [(6,3.2),(7,-1.2)]:
    r=open_run(f'data/{fid}'); ch={c.cid:c for c in resolve_channels(r.meta)}
    B=r.col('magnet_field'); R=r.col('sr1_X')/ch['sr1'].gain/1e-8
    I=r.col('sr0_X')/ch['sr0'].gain
    print('RUN',fid,'complete',r.complete,'interrupted',r.interrupted,'rows',r.rows)
    print('R range',np.min(R),np.max(R),'I nA',np.min(I)*1e9,np.max(I)*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
    print('gate abs max pA',*[np.max(np.abs(r.col(k)))*1e12 for k in ['k_2400_tg_curr','k_2400_bg_curr']])
    dt=np.diff(r.col('time')); db=np.abs(np.diff(B)); print('timing median dt',np.median(dt),'non-ramp seconds',np.quantile(dt-db*438,[.1,.5,.9]))
    fig,ax=plt.subplots(3,1,figsize=(10,8)); ax[0].plot(B,R); ax[0].set_ylabel('Raw Rxx (ohm), nominal 10 nA'); ax[1].plot(B,I*1e9); ax[1].set_ylabel('Drain current (nA)')
    for k in ['k_2400_tg_curr','k_2400_bg_curr']: ax[2].plot(B,r.col(k)*1e12,label=k)
    ax[2].legend(); ax[2].set(xlabel='B (T)',ylabel='Gate current (pA)'); fig.suptitle(f'Run {fid}: n={n}, D~0; sr1 B_1-B_2'); fig.tight_layout(); fig.savefig(f'hera_scratch/spot{fid}_raw.png'); plt.show()
    try:
        on=sdh_onset(R,B,r_full_scale=5000)
        print(on.summary())
        print('ONSET',on.onset_b, 'CLIP',on.clip_high_b)
    except SdhOnsetError as ex:
        print('ONSET ERROR',ex); continue
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    for lo in [on.onset_b,2,3,4]:
        for deg in [3,5]:
            f,spec=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
            y=spec[0]; peaks,_=find_peaks(y); peaks=sorted([k for k in peaks if 3<f[k]<70],key=lambda k:y[k],reverse=True)[:6]
            print('FFT',fid,lo,deg,[(round(float(f[k]),2),round(float(y[k]),3)) for k in peaks])
            axs[0].plot(f,y,label=f'B>{lo:.2f}, deg{deg}')
    axs[0].set(xlim=(0,60),xlabel='F (T)',ylabel='FFT amplitude'); axs[0].legend(fontsize=7)
    order=np.argsort(B); bs=B[order]; rr=R[order]; m=bs>=on.onset_b; residual=rr[m]-np.polynomial.Polynomial.fit(bs[m],rr[m],5)(bs[m]); axs[1].plot(bs[m],residual); axs[1].set(xlabel='B (T)',ylabel='Rxx minus degree-5 background')
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot{fid}_fft.png'); plt.show()
