import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, resolve_channels, plot_raw, sdh_onset, sdh_fft
results={}
for fid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{fid}'); print(summarize_run(r)); plot_raw(r); plt.savefig(f'hera_scratch/spot_{fid}_raw.png'); plt.show()
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I; B=r.col('magnet_field')
 print('range R,I,T,leak',[(float(np.min(v)),float(np.max(v))) for v in [R,I,r.col('T_sample'),r.col('k_2400_tg_curr'),r.col('k_2400_bg_curr')]])
 dt=np.diff(r.col('time')); db=np.abs(np.diff(B)); print('timing elapsed,dt median, overhead:',r.col('time')[-1]-r.col('time')[0],np.median(dt),np.median(dt-db*438))
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary()); print('onset',on.onset_b,'clip',on.clip_high_b)
 fig,ax=plt.subplots(1,2,figsize=(12,4)); ax[0].plot(B,R); ax[0].axvline(on.onset_b,color='r'); ax[0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'Run {fid}, n={n}e12')
 peaks_out={}
 for lo in [on.onset_b,1.5,2.,2.5,3.]:
  for deg in [3,5,7]:
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=8192,log=False)
   ix,_=find_peaks(sp[0]); ix=ix[(f[ix]>3)&(f[ix]<60)]; ix=ix[np.argsort(sp[0,ix])[-6:][::-1]]
   print('FFT',fid,round(lo,3),deg,[(round(f[j],2),round(sp[0,j],2)) for j in ix]); peaks_out[f'{lo:.3f}/{deg}']=[float(f[j]) for j in ix]
   if deg==5: ax[1].plot(f,sp[0]/sp[0].max(),label=f'B>{lo:.2f}')
 ax[1].set(xlim=(0,50),xlabel='Frequency (T)',ylabel='FFT normalized'); ax[1].legend(); fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{fid}_fft.png'); plt.show()
 results[fid]={'n':n,'onset':on.onset_b,'summary':on.summary(),'peaks':peaks_out}
Path('hera_scratch/spot_results.json').write_text(json.dumps(results,indent=2))
