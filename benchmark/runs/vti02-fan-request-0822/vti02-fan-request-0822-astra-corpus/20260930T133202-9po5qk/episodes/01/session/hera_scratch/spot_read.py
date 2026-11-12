import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}'); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 ix=np.argsort(B); B,I,R=B[ix],I[ix],R[ix]
 print('RUN',rid,'R',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'elapsed min',(r.meta['end_time']-r.meta['start_time'])/60)
 for k in ['T_sample','k_2400_tg_curr','k_2400_bg_curr']: print(k,np.min(r.col(k)),np.max(r.col(k)))
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 fig,ax=plt.subplots(2,2,figsize=(12,8)); ax[0,0].plot(B,R); ax[0,0].set(xlabel='B (T)',ylabel='Raw Rxx (ohm)',title=f'Run {rid}, n={n}, D=0; positive B only')
 ax[0,1].plot(B,I*1e9); ax[0,1].set(xlabel='B (T)',ylabel='Drain current (nA)')
 for cutoff in [on.onset_b,1.0,1.5,2.0]:
  for deg in [3,5]:
   f,sp=sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=deg,nfft=4096,log=False)
   p,_=find_peaks(sp[0]); p=sorted([j for j in p if 3<f[j]<60],key=lambda j:sp[0,j],reverse=True)[:6]
   print('FFT',cutoff,deg,[(round(f[j],2),round(sp[0,j],4)) for j in p])
   ax[1,0].plot(f,sp[0]/max(sp[0]),label=f'{cutoff:.2f}-10T deg{deg}')
 ax[1,0].set(xlim=(0,60),xlabel='F (T)',ylabel='Normalized FFT'); ax[1,0].legend(fontsize=7)
 ax[1,1].plot(B,R-np.polyval(np.polyfit(B,R,5),B)); ax[1,1].set(xlabel='B (T)',ylabel='R minus degree-5 background (ohm)')
 fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{rid}.png',dpi=120)
 plt.close(fig)
