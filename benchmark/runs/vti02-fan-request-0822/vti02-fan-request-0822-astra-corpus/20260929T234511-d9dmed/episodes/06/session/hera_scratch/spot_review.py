from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft, resolve_channels
out=Path('hera_scratch')
for rid in [6,7]:
 r=open_run(f'data/{rid}')
 plot_raw(r,channels=['sr0','sr1']); plt.savefig(out/f'spot{rid}_raw.png'); plt.close('all')
 print('channels',resolve_channels(r.meta))
 B=r.col('magnet_field'); R=r.col('sr1_X')/1e-8
 order=np.argsort(B); B,R=B[order],R[order]
 print('RUN',rid,'time diffs',np.percentile(np.diff(r.col('time')),[10,50,90]))
 print('T/current',[(c,float(r.col(c).min()),float(r.col(c).max())) for c in ['T_sample','k_2400_tg_curr','k_2400_bg_curr']])
 for low in [1.,1.2,1.5,2.]:
  on=sdh_onset(R,B,b_lo=low,r_full_scale=5000)
  print('low',low,on.summary())
 fig,axs=plt.subplots(2,1,figsize=(11,8)); axs[0].plot(B,R); axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)')
 for low in [1.,1.5,2.,2.5]:
  f,spec=sdh_fft(R[:,None],B,b_range=(low,10),nfft=4096,log=False)
  p,_=find_peaks(spec[0],prominence=max(spec[0])*.03)
  print('FFT',rid,low,[(round(f[j],2),round(spec[0,j],2)) for j in p if 3<f[j]<60])
  axs[1].plot(f,spec[0]/max(spec[0]),label=f'{low}-10 T')
 axs[1].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized amplitude'); axs[1].legend(); fig.tight_layout(); fig.savefig(out/f'spot{rid}_fft.png'); plt.close(fig)
