from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
for rid, n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}'); fig=plot_raw(r); fig.savefig(f'hera_scratch/spot{rid}_raw.png'); plt.show()
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col(ch['sr0'].col)/ch['sr0'].gain
 R=r.col(ch['sr1'].col)/ch['sr1'].gain/I
 B=r.col('magnet_field'); order=np.argsort(B); B,R=B[order],R[order]
 print(f'run {rid}: R {R.min():.2f}..{R.max():.2f} Ohm, I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K; duration {(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min')
 for c in ['k_2400_tg_curr','k_2400_bg_curr']: print(c,np.percentile(r.col(c)*1e12,[0,50,100]))
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 fig,ax=plt.subplots(1,2,figsize=(12,4))
 for t in on.tones: ax[0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
 ax[0].axhline(5,color='k',ls=':'); ax[0].set(xlabel='B (T)',ylabel='Matched filter SNR'); ax[0].legend()
 for lo in [on.onset_b,1.5,2,2.5]:
  for degree in [3,5]:
   if lo>=10: continue
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=degree,log=False,nfft=4096)
   p,_=find_peaks(sp[0]); p=sorted([p for p in p if 3<f[p]<60],key=lambda p:-sp[0,p])[:5]
   print('FFT',rid,lo,degree,[(round(f[j],2),round(sp[0,j],2)) for j in p])
   ax[1].plot(f,sp[0]/sp[0].max(),label=f'B>{lo:.2f},deg{degree}')
 ax[1].axvline(float(luttinger_frequency(n*1e16)),color='k',ls=':'); ax[1].set(xlim=(0,60),xlabel='F (T)',ylabel='Normalized FFT'); ax[1].legend(fontsize=7)
 fig.suptitle(f'Run {rid}: n={n}e12, D=0 (run-5 calibration), B_1-B_2'); fig.tight_layout(); fig.savefig(f'hera_scratch/spot{rid}_fft.png'); plt.show()
