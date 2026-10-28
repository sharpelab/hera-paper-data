from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
root=Path.cwd()
# Raw channels precede any reduction.
rawfig, rawax=plt.subplots(4,2,figsize=(12,10))
for j,rid in enumerate((6,7)):
 r=open_run(root/"data"/str(rid)); b=r.col("magnet_field")
 for a,col in zip(rawax[:,j],["sr1_X","sr0_X","sr1_P","T_sample"]):
  a.plot(b,r.col(col),lw=.7); a.set(xlabel="B (T)",ylabel=col,title=f"Raw data/{rid}")
rawfig.tight_layout(); rawfig.savefig(root/"hera_scratch"/"spots_raw_6_7.png",dpi=120); plt.show()
fig,axs=plt.subplots(3,2,figsize=(13,10))
for j,rid in enumerate((6,7)):
 r=open_run(root/'data'/str(rid)); ch=resolve_channels(r.meta); ic=current_channel(ch); vc=next(c for c in ch if c.cid=='sr1')
 I=r.col(ic.col)/ic.gain; R=r.col(vc.col)/vc.gain/I; B=r.col('magnet_field'); order=np.argsort(B); B=B[order]; R=R[order]
 dt=np.diff(r.col('time')); dB=np.abs(np.diff(r.col('magnet_field')))
 print('RUN',rid,'rows',r.rows,'wall min',(r.meta['end_time']-r.meta['start_time'])/60,'R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 print('median overhead after bare ramp',np.median(dt-dB*7.3*60),'dt',np.quantile(dt,[.1,.5,.9]))
 for c in ['k_2400_tg_curr','k_2400_bg_curr']: print(c, 'pA range',np.min(r.col(c))*1e12,np.max(r.col(c))*1e12)
 axs[0,j].plot(B,R,lw=.8); axs[0,j].set(xlabel='B (T)',ylabel='Signed V/I (ohm)',title=f'Raw run {rid}: B_1 - B_2')
 axs[1,j].plot(r.col('magnet_field'),I*1e9); axs[1,j].set(xlabel='B (T)',ylabel='Measured current (nA)')
 for lo in [1.5,2.,3.]:
  f,spec=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=4096,bg_degree=3,log=False)
  a=spec[0]; p,_=find_peaks(a); p=[p0 for p0 in p if 3<f[p0]<70]; pk=sorted(p,key=lambda p0:-a[p0])[:5]
  print('FFT',lo,'peaks',[(round(float(f[k]),2),round(float(a[k]),2)) for k in pk],'resolution',1/(1/lo-1/10))
  axs[2,j].plot(f,a/a.max(),label=f'{lo}-10 T')
 try:
  onset=sdh_onset(R,B,b_hi=10,b_lo=.5,r_full_scale=5000,bg_degree=3)
  print(onset.summary())
 except ValueError as exc: print('ONSET UNRESOLVED',exc)
 axs[2,j].set(xlim=(0,60),xlabel='Frequency (T)',ylabel='Normalized FFT'); axs[2,j].legend()
fig.tight_layout(); fig.savefig(root/'hera_scratch'/'spots_6_7.png',dpi=150)
plt.show()
# Timing calibration for gate scans; includes actual fast settling and gate writes.
for rid in [0,1,2,3,5]:
 r=open_run(root/'data'/str(rid)); dt=np.diff(r.col('time'))
 print('TIMING',rid,'rows',r.rows,'wall min',(r.meta['end_time']-r.meta['start_time'])/60,'delay',r.meta.get('delay',r.meta.get('fast_delay')),'dt quantiles',np.quantile(dt,[.1,.5,.9]))
