from pathlib import Path
import json, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft
out = Path('hera_scratch')
results = {}
for i,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{i}')
 plot_raw(r); plt.savefig(out/f'spot_{i}_raw.png',dpi=150); plt.show()
 B=r.col('magnet_field'); I=r.col('sr0_X')/-1e6; R=r.col('sr1_X')/I
 order=np.argsort(B); B=B[order]; R=R[order]
 print('RUN',i,'R min/max',R.min(),R.max(),'I nA',np.percentile(I,[0,50,100])*1e9,'T',np.percentile(r.col('T_sample'),[0,100]))
 print('leak pA',*[np.percentile(r.col(c),[0,50,100])*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 results[str(i)]={'onset':on.onset_b,'summary':on.summary(),'Rmax':float(R.max())}
 fig,ax=plt.subplots(1,2,figsize=(12,4)); ax[0].plot(B,R); ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {i}, n={n:+g}')
 for cut in [on.onset_b,1.5,2.,3.]:
  for deg in [3,5]:
   f,p=sdh_fft(R[:,None],B,b_range=(cut,10),bg_degree=deg,nfft=4096,log=False)
   peaks,_=find_peaks(p[0]); peaks=sorted(peaks,key=lambda k:p[0,k],reverse=True)
   print('FFT',i,cut,deg,[(round(float(f[k]),2),round(float(p[0,k]),3)) for k in peaks[:6]])
   ax[1].plot(f,p[0],label=f'{cut:.2f}-10T deg{deg}')
 ax[1].set(xlim=(0,70),xlabel='F (T)',ylabel='FFT amplitude'); ax[1].legend(fontsize=7); fig.tight_layout(); fig.savefig(out/f'spot_{i}_fft.png',dpi=150); plt.show()
json.dump(results,open(out/'spot_results.json','w'),indent=2)
