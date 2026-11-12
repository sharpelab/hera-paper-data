import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft, resolve_channels, SdhOnsetError
from scipy.signal import find_peaks
for fid in (6,7):
 r=open_run(f'data/{fid}')
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col('sr0_X')/ch['sr0'].gain
 R=r.col('sr1_X')/ch['sr1'].gain/I
 B=r.col('magnet_field')
 fig=plot_raw(r); fig.savefig(f'hera_scratch/spot{fid}_raw.png',dpi=130)
 print('RUN',fid,'R',np.min(R),np.max(R),'I nA',np.min(I)*1e9,np.max(I)*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 print('gate max pA',*[np.max(np.abs(r.col(c)))*1e12 for c in ('k_2400_tg_curr','k_2400_bg_curr')])
 try:
  on=sdh_onset(R,B,r_full_scale=5000)
  print(on.summary())
 except SdhOnsetError as e:
  print('ONSET ERROR',e); continue
 fig,ax=plt.subplots(1,2,figsize=(12,4))
 order=np.argsort(B); bs=B[order]; rs=R[order]
 residual=rs-np.polynomial.Polynomial.fit(bs,rs,5)(bs)
 ax[0].plot(bs,residual); ax[0].set(xlabel='B (T)',ylabel='R minus B-polynomial (Ohm)')
 for lo in (on.onset_b,1.0,1.5,2.):
  for degree in (3,5):
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=degree,nfft=4096,log=False)
   p,_=find_peaks(sp[0],prominence=max(sp[0])*0.03)
   p=sorted(p,key=lambda j:sp[0,j],reverse=True)[:8]
   print('FFT',fid,lo,degree,[(round(f[j],3),round(sp[0,j],3)) for j in p])
   ax[1].plot(f,sp[0]/max(sp[0]),label=f'lo={lo:.2f},deg={degree}')
 ax[1].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT'); ax[1].legend(fontsize=6)
 fig.tight_layout(); fig.savefig(f'hera_scratch/spot{fid}_fft.png',dpi=130)
for fid in (5,6,7):
 r=open_run(f'data/{fid}')
 dt=np.diff(r.col('time'))
 print('TIMING',fid,'duration',r.meta['end_time']-r.meta['start_time'],'dt percentiles',np.percentile(dt,[10,50,90,99]))
 if fid==5:
  same=np.diff(r.col('k_2400_bg_volt'))==0
  print('within-row',np.percentile(dt[same],[10,50,90]),'turnaround',np.percentile(dt[~same],[10,50,90]))
