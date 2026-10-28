from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, summarize_run

fig, ax = plt.subplots(2, 3, figsize=(14,7))
records = {}
for j, rid in enumerate([6,7]):
    r = open_run(Path('data')/str(rid))
    print(summarize_run(r))
    ch = {c.cid:c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field'); I = r.col('sr0_X')/ch['sr0'].gain
    R = r.col('sr1_X')/ch['sr1'].gain/I
    order = np.argsort(B); B,R = B[order],R[order]
    print('channels',ch)
    print('R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9, 'T',r.col('T_sample').min(),r.col('T_sample').max())
    print('leak pA',[(k, np.min(r.col(k))*1e12,np.max(r.col(k))*1e12) for k in ['k_2400_tg_curr','k_2400_bg_curr']])
    dt=np.diff(r.col('time')); print('duration min',(r.col('time')[-1]-r.col('time')[0])/60,'median dt',np.median(dt))
    ax[j,0].plot(B,R); ax[j,0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {rid}: raw B1–B2')
    ax[j,1].plot(r.col('magnet_field'),I*1e9,label='drain'); ax[j,1].set(xlabel='B (T)',ylabel='I drain (nA)')
    on=sdh_onset(R,B,r_full_scale=50e-6/np.median(I))
    print(on.summary())
    for cut in [on.onset_b,1.5,2,3]:
        f,spec=sdh_fft(R[:,None],B,b_range=(cut,10),nfft=4096,log=False)
        pk,_=find_peaks(spec[0]); pk=[k for k in pk if 3<f[k]<65]
        pk=sorted(pk,key=lambda k:-spec[0,k])[:7]
        print('cut',cut,'peaks',[(round(f[k],2),round(spec[0,k],3)) for k in pk])
        ax[j,2].plot(f,spec[0],label=f'B≥{cut:.2f}')
    ax[j,2].set(xlim=(0,65),xlabel='F (T)',ylabel='FFT amplitude'); ax[j,2].legend()
    records[rid]=(B,R,on)
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png',dpi=130)
plt.show()
