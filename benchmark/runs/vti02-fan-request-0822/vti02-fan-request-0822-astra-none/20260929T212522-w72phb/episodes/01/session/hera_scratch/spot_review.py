from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
root = Path.cwd()
fig, ax = plt.subplots(2, 3, figsize=(14, 7))
for j, rid in enumerate([6,7]):
 r = open_run(root/'data'/str(rid)); ch = resolve_channels(r.meta); ic = current_channel(ch); vc = next(c for c in ch if c.cid=='sr1')
 B=r.col('magnet_field'); I=r.col(ic.col)/ic.gain; V=r.col(vc.col)/vc.gain; R=V/I
 order=np.argsort(B); B=B[order]; R=R[order]
 print('RUN',rid,'rows',r.rows,'interrupted',r.interrupted,'elapsed_min',(r.data[-1,0]-r.data[0,0])/60,'columns',r.cols)
 print('current_nA',np.min(I)*1e9,np.max(I)*1e9,'signed R',np.min(R),np.max(R),'metadata',r.meta['measurement_config'])
 ax[j,0].plot(r.col('magnet_field'),V*1e6); ax[j,0].set(xlabel='B (T)',ylabel='raw sr1 X (uV)',title=f'Run {rid}: raw voltage')
 ax[j,1].plot(B,R); ax[j,1].set(xlabel='B (T)',ylabel='signed V/I (ohm)',title='Measured-current normalization')
 for lo in [1.5,2,3]:
  f,a=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=3,log=False,nfft=2048)
  a=a[0]; pk,_=find_peaks(a); pk=sorted([p for p in pk if 3<f[p]<65],key=lambda p:-a[p])[:5]
  print('FFT',lo,[(round(f[p],2),round(a[p],1)) for p in pk], 'resolution',1/(1/lo-.1))
  ax[j,2].plot(f,a/a.max(),label=f'{lo}-10 T')
 try:
  o=sdh_onset(R,B,b_lo=0.5,r_full_scale=5000,bg_degree=3); print(o.summary())
 except Exception as e: print('onset unresolved:',e)
 ax[j,2].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT',title='Window dependence; no stacking assignment'); ax[j,2].legend()
fig.tight_layout(); fig.savefig(root/'hera_scratch/spot_review.png',dpi=140); plt.show()
for rid in [5,6,7]:
 r=open_run(root/'data'/str(rid)); dt=np.diff(r.data[:,0]); print('TIMING',rid,'median_dt',np.median(dt),'p90',np.quantile(dt,.9),'elapsed',(r.data[-1,0]-r.data[0,0])/60)
