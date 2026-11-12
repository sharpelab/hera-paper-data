from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, plot_raw, sdh_onset, sdh_fft, SdhOnsetError
out=Path('hera_scratch')
results={}
for fid in (6,7):
 r=open_run(f'data/{fid}')
 print(summarize_run(r))
 fig=plot_raw(r); fig.savefig(out/f'spot_{fid}_raw.png'); plt.close(fig)
 ch=resolve_channels(r.meta); cur=current_channel(ch); v=next(c for c in ch if c.cid=='sr1')
 I=r.col(cur.col)/cur.gain; R=r.col(v.col)/v.gain/I; B=r.col('magnet_field')
 order=np.argsort(B); B,R=B[order],R[order]
 dt=np.diff(r.col('time')); dB=np.abs(np.diff(r.col('magnet_field')))
 print('R range',R.min(),R.max(),'I nA',np.min(I)*1e9,np.max(I)*1e9,'duration min',np.ptp(r.col('time'))/60,'overhead s',np.median(dt-dB*60*7.3))
 print('T',np.min(r.col('T_sample')),np.max(r.col('T_sample')),'leak max',*[np.max(np.abs(r.col(c))) for c in ('k_2400_tg_curr','k_2400_bg_curr')])
 try:
  on=sdh_onset(R,B,r_full_scale=5000)
  print(on.summary())
  results[str(fid)]={'onset':on.onset_b,'summary':on.summary()}
 except SdhOnsetError as e:
  print('ONSET ERROR',e); results[str(fid)]={'error':str(e)}
 fig,axes=plt.subplots(2,2,figsize=(12,8))
 for ax,lo in zip(axes.flat,[1.,1.5,2.,2.5]):
  for deg in (3,5,7):
   f,s=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
   ax.plot(f,s[0],label=f'deg {deg}')
   peaks,_=find_peaks(s[0]); peaks=sorted([p for p in peaks if 3<f[p]<65],key=lambda p:s[0,p],reverse=True)[:6]
   print(fid,'FFT',lo,deg,[(round(f[p],2),round(s[0,p],3)) for p in peaks])
  ax.set(xlim=(0,65),title=f'B {lo}-10 T',xlabel='F (T)'); ax.legend()
 fig.tight_layout(); fig.savefig(out/f'spot_{fid}_fft.png'); plt.close(fig)
(out/'spot_read.json').write_text(json.dumps(results,indent=2))
