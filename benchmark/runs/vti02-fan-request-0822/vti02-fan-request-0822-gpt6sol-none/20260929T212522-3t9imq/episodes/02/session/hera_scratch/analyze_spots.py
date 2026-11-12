import numpy as np
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft
from scipy.signal import find_peaks
for rid in (6,7):
 r=open_run(f'data/{rid}')
 B=r.col('magnet_field'); t=r.col('time'); T=r.col('T_sample')
 mc=r.meta['measurement_config']; ch=resolve_channels(r.meta)
 cur=current_channel(ch); v=next(c for c in ch if c.n==1)
 I=r.col(cur.col)/cur.gain; V=r.col(v.col)/v.gain; R=V/I
 print(f'RUN {rid}: B {B[0]:.2f}->{B[-1]:.2f} T, T {T.min():.3f}-{T.max():.3f} K, I {np.percentile(I,[1,50,99])*1e9} nA, |R| percentile {np.percentile(abs(R),[0,1,50,99,100])} Ohm, max |V|/50uV {np.max(abs(V))/50e-6:.3f}, leak tg/bg max pA {np.max(abs(r.col("k_2400_tg_curr")))*1e12:.1f}/{np.max(abs(r.col("k_2400_bg_curr")))*1e12:.1f}')
 try:
  out=sdh_onset(abs(R), B, b_hi=9.9, b_lo=0.4, r_full_scale=50e-6/1e-8)
  print(out.summary())
 except Exception as e: print('ONSET ERROR:',type(e).__name__,e)
 for lo,hi in ((2,10),(4,10)):
  try:
   f,s=sdh_fft(abs(R)[:,None],B,b_range=(lo,hi),nfft=4096,bg_degree=5,log=False)
   p,_=find_peaks(s[0]); p=sorted((i for i in p if 2<f[i]<60),key=lambda i:s[0,i],reverse=True)[:8]
   print(f'FFT B {lo}-{hi}:',[(round(f[i],2),round(s[0,i],2)) for i in p])
  except Exception as e: print('FFT ERROR',e)
