from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run,plot_raw,sdh_onset,sdh_fft,resolve_channels,current_channel
ROOT=Path.cwd()
for rid in [6,7]:
 r=open_run(ROOT/'data'/str(rid)); channels=resolve_channels(r.meta); cur=current_channel(channels); v=next(c for c in channels if c.cid=='sr1')
 B=r.col('magnet_field'); I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I
 plot_raw(r); plt.savefig(ROOT/f'hera_scratch/spot{rid}_raw.png'); plt.close('all')
 fig,axs=plt.subplots(2,2,figsize=(12,7))
 axs[0,0].plot(B,R); axs[0,0].set(xlabel='B (T)',ylabel='Signed Rxx (Ohm)')
 axs[0,1].plot(B,R); axs[0,1].set(xlim=(0,3),ylim=(-40,160),xlabel='B (T)',ylabel='Signed Rxx (Ohm)')
 for deg in [3,5,7]:
  on=sdh_onset(R,B,r_full_scale=5000,bg_degree=deg)
  print(f'RUN {rid} degree {deg}\n{on.summary()}')
  for ax,cut in zip(axs[1],[1.5,2.0]):
   f,a=sdh_fft(R[:,None],B,b_range=(cut,10),bg_degree=deg,log=False,nfft=4096)
   ax.plot(f,a[0]/max(a[0]),label=f'deg {deg}'); ax.set(xlim=(0,55),xlabel='F (T)',title=f'B={cut}-10 T')
   pk,_=find_peaks(a[0]); pk=[p for p in pk if 3<f[p]<55]; pk=sorted(pk,key=lambda p:-a[0,p])[:5]
   print('FFT',cut,[(round(float(f[p]),2),round(float(a[0,p]/max(a[0])),2)) for p in pk])
 for ax in axs[1]: ax.legend()
 fig.tight_layout();fig.savefig(ROOT/f'hera_scratch/spot{rid}_review.png');plt.close(fig)
