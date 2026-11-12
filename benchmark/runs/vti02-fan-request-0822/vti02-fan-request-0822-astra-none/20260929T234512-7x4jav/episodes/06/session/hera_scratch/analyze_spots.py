from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft
from scipy.signal import find_peaks
root=Path.cwd()
fig,axes=plt.subplots(2,3,figsize=(15,8))
for row,rid in enumerate((6,7)):
 r=open_run(root/'data'/str(rid)); ch=resolve_channels(r.meta); ci=current_channel(ch); cv=next(c for c in ch if c.cid=='sr1')
 B=r.col('magnet_field'); I=r.col(ci.col)/ci.gain; V=r.col(cv.col)/cv.gain; R=V/I
 order=np.argsort(B); B,R=B[order],R[order]
 print('RUN',rid,'R range',R.min(),R.max(),'I nA',np.percentile(I*1e9,[0,50,100]),'T',np.percentile(r.col('T_sample'),[0,50,100]))
 print('leak pA',[(c,np.percentile(r.col(c)*1e12,[0,50,100]).tolist()) for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 print('raw V fraction of 50uV',np.max(np.abs(V))/50e-6,'phases',[(c,np.percentile(r.col(c),[0,50,100]).tolist()) for c in ['sr0_P','sr1_P']])
 axes[row,0].plot(B,R);axes[row,0].set(xlabel='B (T)',ylabel='Vxx / measured I (ohm)',title=f'Run {rid} raw resistance')
 axes[row,1].plot(r.col('magnet_field'),I*1e9);axes[row,1].set(xlabel='B (T)',ylabel='Drain current (nA)',title='Measured current')
 try:
  o=sdh_onset(R,B,r_full_scale=5000); print(o.summary())
 except ValueError as e: print('ONSET FAIL',e)
 for lo in [1,1.5,2,3]:
  f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=2048)
  p,_=find_peaks(sp[0]);p=sorted([p0 for p0 in p if f[p0]>3],key=lambda p0:-sp[0,p0])[:5]
  print('FFT',lo,[(round(float(f[j]),2),round(float(sp[0,j]),4)) for j in p],'resolution',1/(1/lo-1/10))
  axes[row,2].plot(f,sp[0]/max(sp[0]),label=f'{lo}-10 T')
 axes[row,2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized spectrum',title='Detrended log-R spectra');axes[row,2].legend()
fig.tight_layout();fig.savefig(root/'hera_scratch/spot_analysis.png',dpi=130)
