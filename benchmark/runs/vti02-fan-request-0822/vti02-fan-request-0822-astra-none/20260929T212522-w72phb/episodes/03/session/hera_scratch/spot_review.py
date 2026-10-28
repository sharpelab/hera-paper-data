from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
from scipy.signal import find_peaks
fig,axs=plt.subplots(2,3,figsize=(14,7))
for row,rid in enumerate([6,7]):
 r=open_run(Path('data')/str(rid)); cs=resolve_channels(r.meta); ic=current_channel(cs); vc=next(c for c in cs if not c.is_current)
 B=r.col('magnet_field'); I=r.col(ic.col)/ic.gain; V=r.col(vc.col)/vc.gain; R=np.abs(V/I)
 ix=np.argsort(B); B,I,V,R=[x[ix] for x in (B,I,V,R)]
 axs[row,0].plot(B,V*1e6,label='Vxx (uV)'); axs[row,0].plot(B,I*1e9,label='Idrain (nA)');axs[row,0].legend();axs[row,0].set_title(f'run {rid}: raw signals');axs[row,0].set_xlabel('B (T)')
 axs[row,1].plot(B,R,lw=.8);axs[row,1].set(xlabel='B (T)',ylabel='|Vxx/Idrain| (ohm)')
 for br in [(1.5,4),(2,6),(3,10)]:
  f,a=sdh_fft(R[:,None],B,b_range=br,nfft=4096,log=False,bg_degree=3)
  y=a[0]; axs[row,2].plot(f,y/y.max(),label=str(br))
  pk,_=find_peaks(y,prominence=.10*y.max()); pk=sorted(pk,key=lambda k:y[k],reverse=True)
  print('run',rid,'window',br,'FFT peaks T',np.round(f[pk[:6]],2),'resolution',1/(1/br[0]-1/br[1]))
 axs[row,2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT');axs[row,2].legend()
 print('run',rid,'R range',R.min(),R.max(),'max V uV',abs(V).max()*1e6,'current nA',I.min()*1e9,I.max()*1e9)
fig.tight_layout();fig.savefig('hera_scratch/spot_review.png',dpi=140)
plt.show()
