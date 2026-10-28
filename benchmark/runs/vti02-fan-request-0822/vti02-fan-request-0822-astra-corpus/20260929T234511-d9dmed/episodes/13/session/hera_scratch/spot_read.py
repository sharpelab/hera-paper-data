from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft, resolve_channels
out={}
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}')
 plot_raw(r); plt.gcf().savefig(f'hera_scratch/spot{rid}_raw.png',dpi=130); plt.show()
 ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 ix=np.argsort(B); B=B[ix]; R=R[ix]
 print('RUN',rid,'complete',r.complete,'interrupted',r.interrupted,'R',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',r.col('T_sample').min(),r.col('T_sample').max())
 dt=np.diff(r.col('time')); print('timing median sec',np.median(dt),'wall sec',np.ptp(r.col('time')))
 on=sdh_onset(R,B,b_lo=0.6,b_hi=5.0,r_full_scale=5000)
 print(on.summary())
 out[str(rid)]={'onset':float(on.onset_b),'tones':[{'f':float(t.freq),'onset':float(t.onset_b),'censored':bool(t.censored)} for t in on.tones]}
 fig,axs=plt.subplots(1,2,figsize=(12,4))
 axs[0].plot(B,R); axs[0].axvline(on.onset_b,color='red'); axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'run {rid}, n={n}, onset={on.onset_b:.3f} T')
 for lo in [1.0,1.5,2.0]:
  for deg in [3,5,7]:
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
   p,_=find_peaks(sp[0]); p=[k for k in p if 3<f[k]<55]; p=sorted(p,key=lambda k:sp[0,k],reverse=True)[:6]
   print('FFT',rid,'lo',round(lo,3),'degree',deg,'peaks',[(round(f[k],2),round(sp[0,k],3)) for k in p])
   axs[1].plot(f,sp[0],label=f'B>{lo:.2f}, deg {deg}',alpha=.6)
 axs[1].set(xlim=(0,55),xlabel='F (T)',ylabel='FFT amplitude'); axs[1].axvline(10.33916924*abs(n),color='black',ls='--',label='F_L'); axs[1].legend(fontsize=6)
 fig.tight_layout(); fig.savefig(f'hera_scratch/spot{rid}_fft.png',dpi=130); plt.show()
Path('hera_scratch/spot_summary.json').write_text(json.dumps(out,indent=2))
