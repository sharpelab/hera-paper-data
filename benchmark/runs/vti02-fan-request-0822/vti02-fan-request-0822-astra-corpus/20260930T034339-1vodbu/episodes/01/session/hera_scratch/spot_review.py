from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, summarize_run
fig,axs=plt.subplots(2,3,figsize=(14,8))
for row,i in enumerate((6,7)):
 r=open_run(f'data/{i}'); B=r.col('magnet_field'); I=r.col('sr0_X')/-1e6; R=r.col('sr1_X')/I
 print(summarize_run(r))
 axs[row,0].plot(B,R); axs[row,0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {i}: raw, measured-current normalization')
 axs[row,1].plot(B,I*1e9,label='drain nA')
 axs[row,1].plot(B,r.col('k_2400_tg_curr')*1e12,label='TG pA'); axs[row,1].plot(B,r.col('k_2400_bg_curr')*1e12,label='BG pA');axs[row,1].legend()
 for lo in ([1.,1.2,1.5,2.] if i==6 else [0.75,1.,1.5,2.]):
  on=sdh_onset(R,B,b_lo=lo,r_full_scale=5000)
  print('LOW',lo,on.summary())
  f,a=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,nfft=4096)
  peaks=find_peaks(a[0])[0]; peaks=sorted([j for j in peaks if 3<f[j]<60],key=lambda j:-a[0,j])[:6]
  print('FFT peaks',[(round(f[j],2),round(a[0,j],2)) for j in peaks])
  axs[row,2].plot(f,a[0]/max(a[0]),label=f'{lo}-10 T')
 axs[row,2].set(xlim=(0,60),xlabel='Frequency (T)',ylabel='normalized FFT');axs[row,2].legend()
 print('T',r.col('T_sample').min(),r.col('T_sample').max(),'I nA',np.min(I)*1e9,np.max(I)*1e9)
fig.tight_layout(); fig.savefig('hera_scratch/spot_review.png',dpi=140)
