from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
out={}
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(Path('data')/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col(ch['sr0'].col)/ch['sr0'].gain; R=(r.col(ch['sr1'].col)/ch['sr1'].gain)/I
 print('RUN',rid,'complete',r.complete,'interrupted',r.interrupted,'R',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9)
 print('time',r.meta['end_time']-r.meta['start_time'],'T',r.col('T_sample').min(),r.col('T_sample').max())
 fig,axs=plt.subplots(3,1,figsize=(10,8)); axs[0].plot(B,R); axs[0].set(ylabel='signed Rxx (ohm)',title=f'Run {rid}: n={n}e12 cm-2, D~0, B1-B2')
 axs[1].plot(B,r.col('k_2400_tg_curr')*1e12,label='TG');axs[1].plot(B,r.col('k_2400_bg_curr')*1e12,label='BG');axs[1].legend();axs[1].set(ylabel='gate current (pA)')
 axs[2].plot(B,I*1e9);axs[2].set(xlabel='B (T)',ylabel='drain current (nA)');fig.tight_layout();fig.savefig(f'hera_scratch/spot{rid}_raw.png');plt.show()
 on=sdh_onset(R,B,r_full_scale=5000); print(on.summary());out[str(rid)]={'onset':on.onset_b,'tones':[dict(freq=t.freq,onset=t.onset_b,censored=t.censored) for t in on.tones]}
 fig,axs=plt.subplots(1,2,figsize=(12,4))
 for t in on.tones:axs[0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
 axs[0].axhline(5,c='k',ls=':');axs[0].set(xlabel='B (T)',ylabel='matched-filter SNR');axs[0].legend()
 for lo in [on.onset_b, max(1.5,on.onset_b),max(2.,on.onset_b)]:
  for deg in [3,5]:
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=deg,nfft=4096,log=False)
   pk,_=find_peaks(sp[0],prominence=max(sp[0])*0.05); pk=sorted(pk,key=lambda p:-sp[0,p])[:8]
   print('FFT',rid,lo,deg,[(round(f[p],2),round(sp[0,p],2)) for p in pk]);axs[1].plot(f,sp[0],label=f'lo {lo:.2f}, deg {deg}')
 axs[1].set(xlim=(0,70),xlabel='F (T)',ylabel='FFT amplitude');axs[1].legend(fontsize=7);fig.tight_layout();fig.savefig(f'hera_scratch/spot{rid}_fft.png');plt.show()
json.dump(out,open('hera_scratch/spot_onsets.json','w'),indent=2)
# Onset stability: strong 8-10 T MR biases low-frequency tracking in full-span fits.
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
for upper in [4.,5.,6.]:
 on=sdh_onset(R,B,b_hi=upper,r_full_scale=5000)
 print(f'Localized onset, upper={upper} T:\n{on.summary()}')
