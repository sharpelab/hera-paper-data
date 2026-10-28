import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, summarize_run
from scipy.signal import find_peaks
fig, axes=plt.subplots(2,3,figsize=(14,8))
for j,rid in enumerate([6,7]):
 r=open_run(f'data/{rid}'); print(summarize_run(r))
 ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 ix=np.argsort(B); B,R=B[ix],R[ix]
 print('R range',R.min(),R.max(),'Idrain nA',np.min(I)*1e9,np.max(I)*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 print('leak pA',[(c,np.min(r.col(c))*1e12,np.max(r.col(c))*1e12) for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 dt=np.diff(r.col('time')); print('dt median',np.median(dt),'overhead after ramp',np.median(dt-np.abs(np.diff(r.col('magnet_field')))*438))
 axes[j,0].plot(B,R); axes[j,0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'run {rid}: raw B_1-B_2')
 axes[j,1].plot(r.col('magnet_field'),I*1e9); axes[j,1].set(xlabel='B (T)',ylabel='drain current (nA)')
 try:
  on=sdh_onset(R,B,r_full_scale=5000); print(on.summary()); print('ONSET',on.onset_b)
 except Exception as e: print(type(e).__name__,str(e)); continue
 for cut in [on.onset_b,2,3]:
  f,p=sdh_fft(R[:,None],B,b_range=(cut,10),nfft=4096,log=False)
  peaks,_=find_peaks(p[0]); peaks=sorted(peaks,key=lambda k:p[0,k],reverse=True)[:6]
  print('cut',cut,'peaks',[(round(f[k],2),round(p[0,k],3)) for k in peaks])
  axes[j,2].plot(f,p[0],label=f'B>{cut:.2f}')
 axes[j,2].set(xlim=(0,65),xlabel='F (T)',ylabel='FFT amplitude'); axes[j,2].legend()
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png',dpi=140)
