from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run,plot_raw,sdh_fft,sdh_onset
out=Path('hera_scratch')
for i in [6,7]:
 r=open_run(f'data/{i}');plot_raw(r);plt.savefig(out/f'spot_{i}_raw.png',dpi=140);plt.close('all')
 B=r.col('magnet_field');R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
 fig,ax=plt.subplots(2,1,figsize=(12,8));ax[0].plot(B,R,'.-',ms=2);ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {i}: raw Rxx; B1-B2')
 for lo in [1,1.5,2,3]:
  f,sp=sdh_fft(R[:,None],B,b_range=(lo,8),log=False,nfft=4096,bg_degree=3)
  sp=sp[0];ax[1].plot(f,sp/sp.max(),label=f'{lo}-8 T')
  p,_=find_peaks(sp);p=[x for x in p if 3<f[x]<55];p=sorted(p,key=lambda x:sp[x],reverse=True)[:5]
  print(i,lo,'peaks',[(round(f[x],2),round(sp[x]/sp.max(),3)) for x in p])
 ax[1].set(xlim=(0,55),xlabel='F (T)',ylabel='Normalized FFT, linear R, degree 3');ax[1].legend();fig.tight_layout();fig.savefig(out/f'spot_{i}_fft.png',dpi=140);plt.close(fig)
