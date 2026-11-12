from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, plot_raw, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for rid in (6,7):
 r=open_run(Path('data')/str(rid)); print(summarize_run(r)); print('cols',r.cols)
 plot_raw(r); plt.savefig(f'hera_scratch/spot{rid}_raw.png'); plt.close('all')
 cs=resolve_channels(r.meta); ic=current_channel(cs); vc=next(c for c in cs if c.cid=='sr1')
 I=r.col(ic.col)/ic.gain; R=(r.col(vc.col)/vc.gain)/I; B=r.col('magnet_field')
 print('R range',np.min(R),np.max(R),'I nA',np.min(I)*1e9,np.max(I)*1e9)
 for c in ['k_2400_tg_curr','k_2400_bg_curr','T_sample']:
  if c in r.cols: print(c,np.min(r.col(c)),np.max(r.col(c)))
 try:
  on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 except Exception as e: print(type(e).__name__,str(e)); continue
 fig,ax=plt.subplots(1,2,figsize=(12,4)); ax[0].plot(B,R); ax[0].set(xlabel='B (T)',ylabel='Rxx (Ohm)')
 for lo in [on.onset_b,1.0,1.5,2.,3.]:
  if lo>=B.max():continue
  f,sp=sdh_fft(R[:,None],B,b_range=(lo,float(B.max())),nfft=4096,log=False)
  pk,_=find_peaks(sp[0]); pk=sorted([j for j in pk if 3<f[j]<70],key=lambda j:sp[0,j],reverse=True)[:6]
  print('FFT',rid,lo,[(round(f[j],3),round(sp[0,j],3)) for j in pk]); ax[1].plot(f,sp[0]/max(sp[0]),label=f'B>{lo:.2f}')
 ax[1].set(xlim=(0,70),xlabel='F (T)',ylabel='normalized FFT');ax[1].legend();fig.tight_layout();fig.savefig(f'hera_scratch/spot{rid}_fft.png');plt.close(fig)
