from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
out = Path('hera_scratch')
results={}
for rid, n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}')
 ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
 R=r.col('sr1_X')/ch['sr1'].gain/I
 idx=np.argsort(B); B=B[idx]; R=R[idx]
 fig,ax=plt.subplots(2,2,figsize=(11,7))
 ax[0,0].plot(B,R); ax[0,0].set(xlabel='B (T)',ylabel='signed Rxx (ohm)',title=f'Raw run {rid}, n={n:+.1f}, D=0')
 ax[0,1].plot(r.col('magnet_field'),I*1e9); ax[0,1].set(xlabel='B (T)',ylabel='drain current (nA)')
 ax[1,0].plot(r.col('magnet_field'),r.col('k_2400_tg_curr')*1e12,label='TG'); ax[1,0].plot(r.col('magnet_field'),r.col('k_2400_bg_curr')*1e12,label='BG');ax[1,0].legend();ax[1,0].set(xlabel='B (T)',ylabel='gate current (pA)')
 ax[1,1].plot(r.col('magnet_field'),r.col('T_sample'));ax[1,1].set(xlabel='B (T)',ylabel='sample T (K)')
 fig.tight_layout();fig.savefig(out/f'spot_{rid}_raw.png');plt.show()
 print('RUN',rid,'interrupted',r.interrupted,'R',R.min(),R.max(),'duration_min',np.ptp(r.col('time'))/60,'median_dt',np.median(np.diff(r.col('time'))))
 try:
  on=sdh_onset(R,B,r_full_scale=5000)
  print(on.summary()); results[str(rid)]={'onset':float(on.onset_b),'summary':on.summary()}
 except SdhOnsetError as e:
  print('ONSET ERROR',str(e));results[str(rid)]={'error':str(e)};continue
 fig,ax=plt.subplots(figsize=(10,4))
 for lo in [on.onset_b,max(on.onset_b,1),max(on.onset_b,1.5),max(on.onset_b,2)]:
  for deg in [3,5]:
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
   pk,_=find_peaks(sp[0]);pk=sorted([p for p in pk if 3<f[p]<60],key=lambda p:-sp[0,p])[:5]
   print('FFT',rid,'lo',round(lo,3),'degree',deg,[(round(float(f[p]),2),round(float(sp[0,p]),3)) for p in pk])
   ax.plot(f,sp[0],label=f'B>{lo:.2f}, degree={deg}')
 ax.axvline(10.33916924*abs(n),color='k',ls='--',label='F_L geometry prior')
 ax.set(xlim=(0,60),xlabel='F (T)',ylabel='FFT amplitude',title=f'Run {rid}: extraction stability (positive B only; no even-B symmetrization)');ax.legend(fontsize=7)
 fig.tight_layout();fig.savefig(out/f'spot_{rid}_fft.png');plt.show()
json.dump(results,open(out/'spot_results.json','w'),indent=2)
# measured gate-map acquisition cost, excluding row flyback
r=open_run('data/5');dt=np.diff(r.col('time'));print('RUN5 dt percentiles',np.percentile(dt,[10,50,90,99]),'duration_min',np.ptp(r.col('time'))/60)
