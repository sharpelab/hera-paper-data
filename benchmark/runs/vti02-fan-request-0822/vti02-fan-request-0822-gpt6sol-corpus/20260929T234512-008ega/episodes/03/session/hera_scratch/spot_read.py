from hera.analysis import open_run,sdh_fft,sdh_onset,resolve_channels,current_channel
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
fig,axs=plt.subplots(2,2,figsize=(13,8))
for row,i in enumerate((6,7)):
 r=open_run(f'data/{i}');ch=resolve_channels(r.meta);ci=current_channel(ch)
 I=r.col(ci.col)/ci.gain; R=r.col('sr1_X')/I; B=r.col('magnet_field')
 z=np.argsort(B);B=B[z];R=R[z]
 print('RUN',i,'I',np.median(I)*1e9,'nA','R',np.nanmin(R),np.nanmedian(R),np.nanmax(R),'temp',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 for blo in (0.8,1.2,1.5,2.0):
  try:
   o=sdh_onset(R,B,b_lo=blo,r_full_scale=5000)
   print('onset',blo,o.onset_b,[(round(t.freq,1),round(t.onset_b,2) if t.onset_b else None) for t in o.tones])
  except Exception as e: print('onset error',blo,str(e))
 axs[row,0].plot(B,R,lw=0.8);axs[row,0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'run {i} raw')
 for lo in (1.2,1.5,2):
  f,s=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,nfft=4096)
  axs[row,1].plot(f,s[0]/np.max(s[0]),label=f'{lo}-10 T')
  p,_=find_peaks(s[0],prominence=np.max(s[0])*0.12)
  print('fft',lo,[(round(float(f[j]),1),round(float(s[0,j]/np.max(s[0])),2)) for j in sorted(p,key=lambda k:s[0,k],reverse=True)[:8]])
 axs[row,1].set(xlim=(0,45),xlabel='F (T)',ylabel='norm FFT',title=f'run {i} FFT');axs[row,1].legend()
fig.tight_layout();fig.savefig('hera_scratch/spot_runs6_7.png',dpi=130)
