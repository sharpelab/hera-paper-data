from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
for rid in (6,7):
 r=open_run(Path('data')/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
 B=r.col('magnet_field'); R=r.col('sr1_X')/ch['sr1'].gain/1e-8
 print('RUN',rid,'R range',R.min(),R.max(),'time',r.col('time')[-1]-r.col('time')[0])
 try:
  on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 except SdhOnsetError as e: print(e)
 for cutoff in (0.8,1.0,1.5,2.0):
  f,sp=sdh_fft(R[:,None],B,b_range=(cutoff,9.99),nfft=4096,log=False)
  pk,_=find_peaks(sp[0]); pk=sorted([p for p in pk if 3<f[p]<60],key=lambda p:-sp[0,p])[:6]
  print('cut',cutoff,'peaks',[(round(f[p],2),round(sp[0,p],1)) for p in pk])
 plot_raw(r); plt.savefig(f'hera_scratch/spot_{rid}_raw.png'); plt.close('all')
