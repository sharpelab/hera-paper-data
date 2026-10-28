import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, plot_raw
from scipy.signal import find_peaks
import json
out={}
for rid,n in [(6,3.2),(7,-1.2)]:
 r=open_run(f'data/{rid}')
 print(summarize_run(r))
 print('channels',resolve_channels(r.meta))
 print('meta times', {k:v for k,v in r.meta.items() if 'time' in k or 'delay' in k})
 B=r.col('magnet_field'); I=r.col('sr0_X')/-1e6; R=r.col('sr1_X')/I
 print('I nA',np.percentile(I*1e9,[0,50,100]),'R',np.percentile(R,[0,50,100]))
 print('dt',np.percentile(np.diff(r.col('time')),[0,50,90,100]))
 fig=plot_raw(r); plt.savefig(f'hera_scratch/spot_{rid}_raw.png'); plt.close('all')
 on=sdh_onset(R,B,r_full_scale=5000)
 print(on.summary())
 fig,axes=plt.subplots(1,3,figsize=(15,4))
 axes[0].plot(B,R);axes[0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'Run {rid}: n={n}e12, D=0')
 for t in on.tones:
  axes[1].semilogy(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
 axes[1].axhline(5,color='k',ls=':');axes[1].set(xlabel='B (T)',ylabel='matched-filter SNR');axes[1].legend()
 for lo in [on.onset_b,2,3,4]:
  f,a=sdh_fft(R[:,None],B,b_range=(lo,9.99),log=False,nfft=2048)
  peaks,_=find_peaks(a[0]);peaks=sorted(peaks,key=lambda j:a[0,j],reverse=True)[:6]
  print('FFT',lo,[(round(f[j],2),round(a[0,j],2)) for j in peaks])
  axes[2].plot(f,a[0]/a[0].max(),label=f'B>{lo:.2f}')
 axes[2].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT'); axes[2].legend()
 fig.tight_layout();fig.savefig(f'hera_scratch/spot_{rid}_analysis.png');plt.close(fig)
 out[str(rid)]={'onset_b':on.onset_b,'summary':on.summary(),'max_R':float(R.max())}
json.dump(out,open('hera_scratch/spots_summary.json','w'),indent=2)
