import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
from scipy.signal import find_peaks
for fid in (6,7):
    r=open_run(f'data/{fid}'); plot_raw(r).savefig(f'hera_scratch/raw_spot_{fid}.png',dpi=120)
    ch={c.cid:c for c in resolve_channels(r.meta)}
    I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I; B=r.col('magnet_field')
    print('\nRUN',fid,'complete',r.complete,'interrupted',r.interrupted,'R min/max',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9)
    for col in ('T_sample','k_2400_tg_curr','k_2400_bg_curr'):
        print(col, np.percentile(r.col(col),[0,50,100]))
    dt=np.diff(r.col('time')); db=np.abs(np.diff(B)); print('duration min',np.ptp(r.col('time'))/60,'point overhead after ramp s',np.percentile(dt-db*438,[10,50,90]))
    try:
        on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
    except SdhOnsetError as e: print('ONSET ERROR',str(e)); continue
    fig,ax=plt.subplots(1,2,figsize=(12,4))
    for t in on.tones: ax[0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
    ax[0].set_yscale('log'); ax[0].set_xlabel('B (T)'); ax[0].set_ylabel('matched SNR'); ax[0].legend()
    for lo in (on.onset_b,1.5,2,2.5,3):
        if lo>=9: continue
        for deg in (3,5,7):
            f,p=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
            peaks,_=find_peaks(p[0]); peaks=sorted([k for k in peaks if 3<f[k]<80],key=lambda k:p[0,k],reverse=True)[:5]
            print('FFT',lo,deg,[(round(float(f[k]),2),round(float(p[0,k]),2)) for k in peaks])
            if deg==5: ax[1].plot(f,p[0]/np.max(p),label=f'B>{lo:.2f}')
    ax[1].set_xlim(0,80); ax[1].set_xlabel('F (T)'); ax[1].legend(); fig.tight_layout(); fig.savefig(f'hera_scratch/spot_fft_{fid}.png',dpi=120)
plt.close('all')
