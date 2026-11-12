from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks

file_path = str(Path.cwd() / 'data')
assert (Path(file_path) / '6' / 'metadata.json').is_file(), file_path
out=[]
for rid,ns in [(6,3.2),(7,-1.2)]:
 r=open_run(Path(file_path)/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
 R=(r.col('sr1_X')/ch['sr1'].gain)/I
 print(f'run {rid}: {r.rows} points, interrupted {r.interrupted}, B {B[0]:.3f}->{B[-1]:.3f}, elapsed {(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min')
 print('R range',np.percentile(R,[0,50,100]),'I nA',np.percentile(I*1e9,[0,50,100]),'T',np.percentile(r.col('T_sample'),[0,50,100]))
 print('gate-current pA',[(k,np.percentile(r.col(k)*1e12,[0,50,100]).round(2).tolist()) for k in ['k_2400_tg_curr','k_2400_bg_curr']])
 print('point dt',np.percentile(np.diff(r.col('time')),[5,50,95,100]),'nominal full-density F',float(luttinger_frequency(ns*1e16)))
 fig,ax=plt.subplots(2,3,figsize=(13,7))
 ax[0,0].plot(B,r.col('sr1_X')*1e6);ax[0,0].set_ylabel('raw sr1 X (uV)')
 ax[0,1].plot(B,I*1e9);ax[0,1].set_ylabel('drain I (nA)')
 for k in ['k_2400_tg_curr','k_2400_bg_curr']:ax[0,2].plot(B,r.col(k)*1e12,label=k)
 ax[0,2].set_ylabel('gate I (pA)');ax[0,2].legend(fontsize=7)
 ax[1,0].plot(B,R);ax[1,0].set_ylabel('Rxx = V/I (Ohm)')
 ax[1,1].plot(B,r.col('sr0_P'),label='sr0');ax[1,1].plot(B,r.col('sr1_P'),label='sr1');ax[1,1].set_ylabel('phase (deg)');ax[1,1].legend()
 for br in [(1,4),(2,6),(3,10)]:
  f,spec=sdh_fft(R[:,None],B,b_range=br,nfft=4096,log=False,bg_degree=3)
  a=spec[0];p,_=find_peaks(a);p=sorted([p0 for p0 in p if 2<f[p0]<70],key=lambda p0:-a[p0])[:6]
  print('FFT',br,[(round(f[j],2),round(a[j],2)) for j in p])
  ax[1,2].plot(f,a/max(a),label=str(br))
 ax[1,2].set_xlim(0,70);ax[1,2].set_xlabel('frequency (T)');ax[1,2].legend()
 for a in ax.flat:
  if a!=ax[1,2]:a.set_xlabel('B (T)')
 fig.suptitle(f'Run {rid}: raw channels then Rxx and FFT; nominal n={ns}, D=0, scale provisional')
 fig.tight_layout();plt.show()
 try:
  o=sdh_onset(R,B,r_full_scale=5000)
  print(o.summary());out.append({'run':rid,'onset':o.onset_b,'freq':o.onset_freq,'summary':o.summary()})
 except ValueError as e:print('onset unresolved:',e)

r=open_run(Path(file_path)/'5');dt=np.diff(r.col('time'));idx=np.arange(1,r.rows)
print('run 5 within-row seconds',np.percentile(dt[idx%66!=0],[5,50,95]),'turnarounds',np.percentile(dt[idx%66==0],[5,50,95]))
