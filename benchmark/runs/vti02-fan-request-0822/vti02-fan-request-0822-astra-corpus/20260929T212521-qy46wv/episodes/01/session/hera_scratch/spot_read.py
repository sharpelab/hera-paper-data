import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
from scipy.signal import find_peaks
import json
fig, ax = plt.subplots(2, 3, figsize=(15,8))
results={}
for j,(fid,n) in enumerate([(6,3.2),(7,-1.2)]):
 r=open_run(f'data/{fid}'); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 ax[j,0].plot(B,R); ax[j,0].set(xlabel='B (T)',ylabel='Signed Rxx (Ohm)',title=f'Run {fid}: n={n}, D=0, B1-B2')
 print('RUN',fid,'interrupted',r.interrupted,'points',len(B),'R',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')))
 print('timing',np.quantile(np.diff(r.col('time')),[.1,.5,.9]),'duration',np.ptp(r.col('time')))
 try:
  on=sdh_onset(R,B,r_full_scale=5000)
  print(on.summary()); results[str(fid)]={'onset':on.onset_b,'tones':[{'freq':t.freq,'onset':t.onset_b,'censored':t.censored,'marginal':t.marginal} for t in on.tones]}
  for t in on.tones: ax[j,1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
  ax[j,1].axhline(5,color='k',ls=':'); ax[j,1].legend(); ax[j,1].set(xlabel='B (T)',ylabel='matched-filter SNR')
  for deg in [3,5,7]:
   f,sp=sdh_fft(R[:,None],B,b_range=(on.onset_b,10),bg_degree=deg,log=False,nfft=4096)
   peaks,_=find_peaks(sp[0]); peaks=sorted(peaks,key=lambda k:sp[0,k],reverse=True)[:6]
   print('FFT',deg,[(round(f[k],2),round(sp[0,k],1)) for k in peaks])
   ax[j,2].plot(f,sp[0]/max(sp[0]),label=f'degree {deg}')
  ax[j,2].axvline(10.339*n if n>0 else -10.339*n,color='k',ls='--',label='F_L'); ax[j,2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT'); ax[j,2].legend()
 except SdhOnsetError as e: print('ONSET FAILED',e)
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png',dpi=140)
with open('hera_scratch/spot_read.json','w') as f: json.dump(results,f,indent=2)
plt.show()
