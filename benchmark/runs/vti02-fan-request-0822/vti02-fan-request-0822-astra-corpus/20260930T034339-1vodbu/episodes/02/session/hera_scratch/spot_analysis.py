from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft, SdhOnsetError
OUT=Path('hera_scratch')
spot_results={}
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}');print(summarize_run(r))
 plot_raw(r);plt.savefig(OUT/f'spot_{rid}_raw.png',dpi=140);plt.show()
 channels=resolve_channels(r.meta);cur=current_channel(channels);v=next(c for c in channels if c.cid=='sr1')
 I=r.col(cur.col)/cur.gain;R=r.col(v.col)/v.gain/I;B=r.col('magnet_field');ix=np.argsort(B);B,R=B[ix],R[ix]
 print('R Ohm min/median/max',np.quantile(R,[0,.5,1]),'I nA',np.quantile(I,[0,.5,1])*1e9)
 for name in ['T_sample','k_2400_tg_curr','k_2400_bg_curr','sr1_P']:
  print(name,np.quantile(r.col(name),[0,.5,1]))
 dt=np.diff(r.col('time'));print('dt median, duration',np.median(dt),r.meta['end_time']-r.meta['start_time'])
 try:
  on=sdh_onset(R,B,b_lo=1.0 if rid==6 else 0.75,r_full_scale=5000);print(on.summary());spot_results[rid]=on
 except SdhOnsetError as e: print('ONSET FAIL',e);continue
 fig,axs=plt.subplots(1,2,figsize=(12,4))
 for tone in on.tones:axs[0].plot(tone.b_centers,tone.snr,label=f'{tone.freq:.1f} T')
 axs[0].axhline(5,color='k',ls=':');axs[0].set(xlabel='B (T)',ylabel='Matched-filter SNR',yscale='log');axs[0].legend()
 for cutoff in [on.onset_b,1.5,2.0,3.0]:
  for degree in [3,5]:
   f,a=sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=degree,nfft=4096,log=False)
   a=a[0];axs[1].plot(f,a,label=f'B>={cutoff:.2f}, p{degree}')
   pk,_=find_peaks(a);pk=[p for p in pk if 3<f[p]<60];pk=sorted(pk,key=lambda p:-a[p])[:5]
   print('FFT',rid,cutoff,degree,[(round(f[p],2),round(a[p],2)) for p in pk])
 axs[1].set(xlim=(0,60),xlabel='Frequency (T)',ylabel='FFT amplitude');axs[1].legend(fontsize=6)
 fig.tight_layout();fig.savefig(OUT/f'spot_{rid}_analysis.png',dpi=140);plt.show()
