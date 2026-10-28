import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for fid in (6,7):
 r=open_run(f'data/{fid}')
 plot_raw(r, channels=['sr0','sr1'])
 plt.savefig(f'hera_scratch/spot{fid}_raw.png'); plt.close('all')
 B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
 print('RUN',fid,'interrupted',r.interrupted,'Rrange', [R.min(),R.max()], 'T', [r.col('T_sample').min(),r.col('T_sample').max()])
 print('timing median',np.median(np.diff(r.col('time'))),'duration',r.col('time')[-1]-r.col('time')[0])
 onset=sdh_onset(R,B,r_full_scale=5000)
 print('ONSET',onset)
 fig,ax=plt.subplots(1,2,figsize=(12,4)); ax[0].plot(B,R); ax[0].axvline(onset.onset_b,c='r'); ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)')
 for low in [onset.onset_b,0.7,1.0,1.5]:
  f,a=sdh_fft(R[:,None],B,b_range=(low,10),nfft=4096,log=False)
  pp,_=find_peaks(a[0]); pp=sorted([p for p in pp if 3<f[p]<60],key=lambda p:a[0,p],reverse=True)[:6]
  print('FFT',fid,low,[(round(f[p],2),round(a[0,p],1)) for p in pp]); ax[1].plot(f,a[0]/a[0].max(),label=f'B>{low:.2f}')
 ax[1].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT'); ax[1].legend();fig.tight_layout(); fig.savefig(f'hera_scratch/spot{fid}_fft.png');plt.close(fig)
