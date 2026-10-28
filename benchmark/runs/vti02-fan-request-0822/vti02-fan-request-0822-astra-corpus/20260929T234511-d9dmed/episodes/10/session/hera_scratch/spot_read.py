import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, summarize_run, resolve_channels, sdh_onset, SdhOnsetError, sdh_fft
from scipy.signal import find_peaks
for fid in (6,7):
 r=open_run(f'data/{fid}')
 print(summarize_run(r))
 fig=plot_raw(r); fig.savefig(f'hera_scratch/spot_{fid}_raw.png'); plt.show()
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col(ch['sr0'].col)/ch['sr0'].gain
 R=r.col(ch['sr1'].col)/ch['sr1'].gain/I
 B=r.col('magnet_field')
 print('R range',R.min(),R.max(),'T range',r.col('T_sample').min(),r.col('T_sample').max())
 print('elapsed_s',np.ptp(r.col('time')),'dt median',np.median(np.diff(r.col('time'))))
 try:
  on=sdh_onset(R,B,r_full_scale=5000)
  print(on.summary())
 except SdhOnsetError as e:
  print('ONSET FAILED:',e); continue
 fig,ax=plt.subplots(1,2,figsize=(12,4))
 for low in (on.onset_b,1.,1.5,2.):
  for degree in (3,5):
   f,sp=sdh_fft(R[:,None],B,b_range=(low,8),bg_degree=degree,log=False,nfft=4096)
   ix,_=find_peaks(sp[0],prominence=sp[0].max()*.08)
   ix=sorted(ix,key=lambda j:sp[0,j],reverse=True)[:7]
   print(fid,'FFT',low,8,degree,[(round(f[j],2),round(sp[0,j],1)) for j in ix])
   ax[0].plot(f,sp[0]/sp[0].max(),label=f'{low:.2f}-8T p{degree}')
 for t in on.tones:
  ax[1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f}T')
 ax[0].set(xlim=(0,60),xlabel='Frequency (T)',ylabel='Normalized FFT amplitude')
 ax[1].set(xlabel='B (T)',ylabel='Tone SNR',yscale='log')
 for a in ax:a.legend(fontsize=6)
 fig.suptitle(f'run {fid}: signed R, polynomial detrend in B, Hann FFT');fig.tight_layout();fig.savefig(f'hera_scratch/spot_{fid}_fft.png');plt.show()
