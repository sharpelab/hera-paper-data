from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset
from scipy.signal import find_peaks
root=Path.cwd()
if not (root/'data'/'6').is_dir():
    root=Path(file_path).parent
fig,axs=plt.subplots(2,3,figsize=(14,7))
traces=[]
for row,rid in enumerate([6,7]):
 r=open_run(root/'data'/str(rid)); cs={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/cs['sr0'].gain
 R=r.col('sr1_X')/cs['sr1'].gain/I
 axs[row,0].plot(B,r.col('sr1_X')*1e6,label='sr1 X (uV)')
 axs[row,0].plot(B,r.col('sr0_X')*1e3,label='sr0 X (mV)');axs[row,0].legend();axs[row,0].set_title(f'run {rid}: raw lock-in X')
 axs[row,1].plot(B,R);axs[row,1].set_ylabel('signed X/I (Ohm)')
 axs[row,2].plot(B,r.col('k_2400_tg_curr')*1e12,label='TG')
 axs[row,2].plot(B,r.col('k_2400_bg_curr')*1e12,label='BG');axs[row,2].set_ylabel('pA');axs[row,2].legend()
 for ax in axs[row]: ax.set_xlabel('B (T)')
 print(f'run {rid}: signed R [{R.min():.2f},{R.max():.2f}] Ohm; negative points {sum(R<0)}/{len(R)}; I [{I.min()*1e9:.3f},{I.max()*1e9:.3f}] nA; duration {(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min')
 traces.append((rid,B,R))
fig.tight_layout();fig.savefig(root/'hera_scratch'/'spots_raw.png',dpi=140);plt.show()
fig,axs=plt.subplots(2,2,figsize=(12,7))
for row,(rid,B,R) in enumerate(traces):
 for blo,bhi in [(1,4),(1.5,6),(2,8),(2,10)]:
  f,sp=sdh_fft(R[:,None],B,b_range=(blo,bhi),nfft=4096,bg_degree=3,log=False)
  sp=sp[0]; axs[row,0].plot(f,sp/sp.max(),label=f'{blo}-{bhi} T')
  pk,_=find_peaks(sp);pk=sorted([p for p in pk if 3<f[p]<60],key=lambda p:-sp[p])[:5]
  print(f'run {rid}, B {blo}-{bhi} T, nominal resolution {1/(1/blo-1/bhi):.2f} T; FFT peaks',[(round(f[p],2),round(sp[p]/sp.max(),2)) for p in pk])
 axs[row,0].set_xlim(0,60);axs[row,0].set_xlabel('F (T)');axs[row,0].legend();axs[row,0].set_title(f'run {rid}: signed R, linear FFT, cubic background')
 sel=(B>=1)&(B<=6);axs[row,1].plot(1/B[sel],R[sel]);axs[row,1].set_xlabel('1/B (1/T)');axs[row,1].set_ylabel('signed R (Ohm)')
fig.tight_layout();fig.savefig(root/'hera_scratch'/'spots_fft.png',dpi=140);plt.show()
