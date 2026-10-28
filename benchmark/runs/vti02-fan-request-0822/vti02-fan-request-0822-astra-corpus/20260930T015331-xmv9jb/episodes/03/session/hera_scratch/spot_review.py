from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset
from scipy.signal import find_peaks
root=Path.cwd()
fig,ax=plt.subplots(2,3,figsize=(15,8))
for j,rid in enumerate((6,7)):
 r=open_run(root/'data'/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/I
 ax[j,0].plot(B,R,'.-',ms=2); ax[j,0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {rid}: raw signed Rxx, B1-B2')
 ax[j,1].plot(B,R,'.-',ms=2); ax[j,1].set(xlim=(0,3),ylim=(-40,180),xlabel='B (T)',ylabel='Rxx (ohm)',title='Low-field raw zoom')
 for lo in (1.,1.5,2.,3.):
  f,s=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=3,nfft=4096,log=False)
  pk,_=find_peaks(s[0]); pk=[p for p in pk if 3<f[p]<55]; pk=sorted(pk,key=lambda p:-s[0,p])[:6]
  print(rid,lo,[(round(f[p],2),round(s[0,p],1)) for p in pk])
  ax[j,2].plot(f,s[0]/s.max(),label=f'{lo}-10 T')
 ax[j,2].set(xlim=(0,55),xlabel='Frequency (T)',ylabel='normalized amplitude',title='B-polynomial degree 3; Hann FFT'); ax[j,2].legend()
 print('QUALITY',rid,'Rrange',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'leak pA',*[np.max(np.abs(r.col(c)))*1e12 for c in ('k_2400_tg_curr','k_2400_bg_curr')], 'T',r.col('T_sample').min(),r.col('T_sample').max())
fig.tight_layout(); fig.savefig(root/'hera_scratch/spot_review.png',dpi=150)
