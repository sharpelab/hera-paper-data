from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft
root=Path.cwd()
fig,axs=plt.subplots(2,3,figsize=(15,8))
for row,i in enumerate((6,7)):
 r=open_run(root/'data'/str(i)); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
 order=np.argsort(B); B=B[order];R=R[order]
 axs[row,0].plot(B,R,'.-',ms=2);axs[row,0].set(title=f'Run {i} raw Rxx',xlabel='B (T)',ylabel='Ohm')
 axs[row,1].plot(B,R,'.-',ms=3);axs[row,1].set(xlim=(0,2),ylim=(R[B<2].min()-2,R[B<2].max()+2),title='Low-field raw',xlabel='B (T)')
 for lo in (0.7,1,1.5,2):
  f,s=sdh_fft(R[:,None],B,b_range=(lo,8),nfft=4096,bg_degree=3,log=False)
  axs[row,2].plot(f,s[0]/s[0].max(),label=f'{lo}-8 T')
  p,_=find_peaks(s[0]);p=sorted([j for j in p if 3<f[j]<50],key=lambda j:s[0,j],reverse=True)[:5]
  print(i,lo,[(round(f[j],2),round(s[0,j],2)) for j in p])
 axs[row,2].set(xlim=(0,50),xlabel='F (T)',title='FFT, degree 3, normalized');axs[row,2].legend()
fig.tight_layout();fig.savefig(root/'hera_scratch/spot_handoff.png',dpi=150)
for i in (6,7):
 r=open_run(root/'data'/str(i)); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
 print(f'Run {i}: onset on adequately sampled B>=1 T segment')
 print(sdh_onset(R,r.col('magnet_field'),b_lo=1.0,r_full_scale=5000).summary())
plt.show()
