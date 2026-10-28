from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
root=Path.cwd()
results={}
fig,axs=plt.subplots(2,3,figsize=(15,8))
for row,(rid,n) in enumerate([(6,3.2),(7,-1.2)]):
 r=open_run(root/'data'/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/1e-8
 print('RUN',rid,'rows',r.rows,'complete',r.complete,'interrupted',r.interrupted,'R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'seconds',r.meta['end_time']-r.meta['start_time'])
 print('T',np.min(r.col('T_sample')),np.max(r.col('T_sample')),'gate max pA',[np.max(np.abs(r.col(c)))*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']])
 axs[row,0].plot(B,R); axs[row,0].set(xlabel='B (T)',ylabel='signed Rxx (Ohm)',title=f'run {rid}: n={n}, D~0; raw')
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 results[str(rid)]={'onset':on.onset_b,'tone':on.onset_freq,'censored':next(t.censored for t in on.tones if t.freq==on.onset_freq)}
 for t in on.tones:
  axs[row,1].semilogy(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
 axs[row,1].axhline(5,color='k',ls=':');axs[row,1].set(xlabel='B (T)',ylabel='onset SNR');axs[row,1].legend()
 for blo in [on.onset_b,max(on.onset_b,1.0),max(on.onset_b,1.5)]:
  for deg in [3,5,7]:
   f,s=sdh_fft(R[:,None],B,b_range=(blo,10),bg_degree=deg,nfft=4096,log=False)
   p,_=find_peaks(s[0]); p=[j for j in p if 2<f[j]<65];p=sorted(p,key=lambda j:-s[0,j])[:6]
   print('FFT',rid,'B_lo',blo,'deg',deg,'peaks',[(round(f[j],2),round(s[0,j],2)) for j in p])
   axs[row,2].plot(f,s[0]/max(s[0]),label=f'lo={blo:.2f},deg={deg}')
 axs[row,2].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT');axs[row,2].axvline(abs(n)*10.33917,color='k',ls='--');axs[row,2].legend(fontsize=6)
fig.tight_layout();fig.savefig(root/'hera_scratch/spot_fan_design.png',dpi=150)
(root/'hera_scratch/spot_onsets.json').write_text(json.dumps(results,indent=2))
for rid in [5,6,7]:
 r=open_run(root/'data'/str(rid)); dt=np.diff(r.col('time'))
 print('TIMING',rid, 'dt percentiles',np.percentile(dt,[10,50,90,99]),'delay',r.meta.get('fast_delay',r.meta.get('delay')))
