import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
from scipy.signal import find_peaks
fig, ax = plt.subplots(3, 2, figsize=(12, 10))
for j, rid in enumerate((6,7)):
    r = open_run(f'data/{rid}')
    ch = resolve_channels(r.meta); ci = current_channel(ch); cv = next(c for c in ch if c.cid=='sr1')
    I = r.col(ci.col)/ci.gain; V = r.col(cv.col)/cv.gain; R = V/I; B=r.col('magnet_field')
    ax[0,j].plot(B,V*1e6); ax[0,j].set(xlabel='B (T)',ylabel='Raw sr1 X (uV)',title=f'Run {rid}')
    ax[1,j].plot(B,R); ax[1,j].set(xlabel='B (T)',ylabel='Signed V/I (ohm)')
    for low in (1.5,2,3):
        f,a=sdh_fft(R[:,None],B,b_range=(low,10),log=False,nfft=4096,bg_degree=3)
        peaks,_=find_peaks(a[0]); peaks=sorted([p for p in peaks if 3<f[p]<70],key=lambda p:a[0,p],reverse=True)[:5]
        print('FFT',rid,'window',low,10,'resolution',1/(1/low-1/10),'peaks',[(round(f[p],2),round(a[0,p],1)) for p in peaks])
        ax[2,j].plot(f,a[0]/max(a[0]),label=f'{low}-10 T')
    ax[2,j].set(xlim=(0,70),xlabel='F (T)',ylabel='FFT normalized'); ax[2,j].legend()
    print('RUN',rid,'rows',r.rows,'interrupted',r.interrupted,'minutes',(r.meta['end_time']-r.meta['start_time'])/60,'R range',R.min(),R.max(),'I nA',np.min(I)*1e9,np.max(I)*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')),'leak pA',[(x,np.max(np.abs(r.col(x)))*1e12) for x in ['k_2400_tg_curr','k_2400_bg_curr']])
    try: print('ONSET',rid,sdh_onset(R,B,b_lo=0.7,r_full_scale=5000).summary())
    except ValueError as e: print('ONSET unassigned',rid,str(e))
fig.tight_layout(); fig.savefig('hera_scratch/spot_review.png',dpi=150)
for rid in (0,1,2,3,5,6,7):
    r=open_run(f'data/{rid}'); dt=np.diff(r.col('time')); print('TIMING',rid,'duration min',(r.meta['end_time']-r.meta['start_time'])/60,'median dt',np.median(dt),'p90',np.quantile(dt,.9),'delay',r.meta.get('delay',r.meta.get('fast_delay')))
plt.show()
