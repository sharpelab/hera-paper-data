from pathlib import Path
import sys, json, warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.constants import h,e
from hera.analysis import open_run, plot_raw, sdh_fft, sdh_onset
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs
fig, axs=plt.subplots(2,2,figsize=(12,8))
for row,(i,n) in enumerate([(6,3.2),(7,-1.2)]):
 r=open_run(f'data/{i}'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
 axs[row,0].plot(B,R); axs[row,0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'Run {i}, n={n}e12, raw B_1-B_2')
 for lo,hi,deg in [(1,5,3),(1,5,5),(1.5,5,3),(2,7,3)]:
  f,S=sdh_fft(R[:,None],B,b_range=(lo,hi),nfft=4096,bg_degree=deg,log=False)
  inds,_=find_peaks(S[0],prominence=S.max()*.025); inds=sorted(inds,key=lambda k:S[0,k],reverse=True)[:9]
  print('FFT',i,(lo,hi,deg),[(round(f[k],2),round(S[0,k]/S.max(),3)) for k in inds if f[k]<150])
  axs[row,1].plot(f,S[0]/S.max(),label=f'{lo}-{hi} T deg {deg}')
 axs[row,1].axvline(h/(4*e)*abs(n)*1e16,c='k',ls='--',label='F_L prior')
 axs[row,1].set(xlim=(0,100),xlabel='F (T)',ylabel='normalized magnitude'); axs[row,1].legend(fontsize=8)
 o=sdh_onset(R,B,b_lo=.3,b_hi=5 if i==6 else 4,bg_degree=5,r_full_scale=5000)
 print('ONSET',i,o.onset_b,[(round(t.freq,3),round(t.onset_b,3),t.censored,t.marginal) for t in o.tones])
for n in [2.4,2.6,2.8,3.0,3.2,-1.2]:
 print('MODEL',n,[round(p[0],4) for p in abab_fs(n*1e16)[1]])
fig.tight_layout(); fig.savefig('hera_scratch/spot_fan_design.png',dpi=140)
plt.show()
