from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, plot_raw
from scipy.signal import find_peaks
fig,axs=plt.subplots(2,3,figsize=(15,8))
for j,rid in enumerate([6,7]):
 r=open_run(f'data/{rid}'); cs=resolve_channels(r.meta); ci=current_channel(cs); cv=next(c for c in cs if c.cid=='sr1'); I=r.col(ci.col)/ci.gain; R=r.col(cv.col)/cv.gain/I; B=r.col('magnet_field'); ix=np.argsort(B); B,R=B[ix],R[ix]
 axs[j,0].plot(B,R,'.-',ms=2); axs[j,0].set(title=f'run {rid}: raw B1-B2',xlabel='B (T)',ylabel='Rxx (ohm)')
 axs[j,1].plot(B,R,'.-',ms=3); axs[j,1].set(xlim=(0,2.5),ylim=(0,200) if rid==6 else (50,350),xlabel='B (T)',ylabel='Rxx (ohm)',title='Raw low-field zoom')
 for low,high in [(1,4),(1.5,6),(2,8),(2,10)]:
  f,s=sdh_fft(R[:,None],B,b_range=(low,high),nfft=4096,log=False,bg_degree=3)
  mask=(f>3)&(f<55); sp=s[0]; peaks,_=find_peaks(sp); peaks=[p for p in peaks if 3<f[p]<55]; peaks=sorted(peaks,key=lambda p:-sp[p])[:5]; print(rid,(low,high),'peaks',[(round(f[p],2),round(sp[p],2)) for p in peaks]); axs[j,2].plot(f,sp/max(sp[mask]),label=f'{low}-{high} T')
 axs[j,2].set(xlim=(0,55),ylim=(0,1.1),xlabel='frequency (T)',title='B-polynomial degree 3; linear R FFT'); axs[j,2].legend()
 print('RUN',rid,'T',np.percentile(r.col('T_sample'),[0,50,100]),'leak',[(c,np.percentile(r.col(c),[0,50,100]).tolist()) for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 for hi in [3,4,6]:
  try: print('onset hi',hi,sdh_onset(R,B,b_hi=hi,b_lo=1 if rid==6 else .6,r_full_scale=5000).summary())
  except Exception as e: print(type(e).__name__,str(e))
fig.tight_layout(); fig.savefig('hera_scratch/spot_analysis.png',dpi=150)
