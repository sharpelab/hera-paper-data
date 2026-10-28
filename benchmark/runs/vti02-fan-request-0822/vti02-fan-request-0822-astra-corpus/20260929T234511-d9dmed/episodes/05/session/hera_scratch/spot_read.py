from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_fft, sdh_onset
for rid in (6,7):
 r=open_run(f'data/{rid}')
 fig=plot_raw(r); fig.savefig(f'hera_scratch/spot_raw_{rid}.png'); plt.close(fig)
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col('sr0_X')/ch['sr0'].gain
 R=r.col('sr1_X')/ch['sr1'].gain/I; B=r.col('magnet_field')
 fig,ax=plt.subplots(2,2,figsize=(12,8))
 ax[0,0].plot(B,R); ax[0,0].set_xlim(0,2); ax[0,0].set_ylim(0,180)
 for lo in (0.3,0.5,0.8,1,1.3,1.5,2):
  f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=4096,bg_degree=3,log=False)
  pk,_=find_peaks(sp[0]); pk=sorted([p for p in pk if 3<f[p]<60],key=lambda p:sp[0,p],reverse=True)[:6]
  print(rid,lo,[(round(float(f[p]),2),round(float(sp[0,p]),2)) for p in pk])
  ax[0,1].plot(f,sp[0]/sp[0].max(),label=str(lo))
 ax[0,1].set_xlim(0,60); ax[0,1].legend()
 for lo,hi in ((0.3,1),(1,3)):
  m=(B>=lo)&(B<=hi); ax[1,0 if lo<1 else 1].plot(1/B[m],R[m],'.-')
 fig.suptitle(f'Run {rid}: raw low-field + FFT cutoff stability'); fig.tight_layout(); fig.savefig(f'hera_scratch/spot_detail_{rid}.png'); plt.close(fig)
