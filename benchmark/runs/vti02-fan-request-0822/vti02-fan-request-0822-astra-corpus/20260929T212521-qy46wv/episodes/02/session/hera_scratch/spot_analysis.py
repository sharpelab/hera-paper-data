from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, plot_raw, sdh_onset, sdh_fft, SdhOnsetError, summarize_run
out = {}
for rid in (6,7):
 r=open_run(Path('data')/str(rid)); print(summarize_run(r))
 ch={c.cid:c for c in resolve_channels(r.meta)}
 I=r.col('sr0_X')/ch['sr0'].gain
 R=(r.col('sr1_X')/ch['sr1'].gain)/I
 B=r.col('magnet_field'); ix=np.argsort(B); B,R=B[ix],R[ix]
 fig=plot_raw(r); plt.savefig(f'hera_scratch/spot_{rid}_raw.png'); plt.show()
 dt=np.diff(r.col('time')); db=np.abs(np.diff(r.col('magnet_field')))
 print('QUALITY',rid,'R range',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9,'T',np.min(r.col('T_sample')),np.max(r.col('T_sample')),'leak pA',[(c,float(np.max(np.abs(r.col(c))))*1e12) for c in ('k_2400_tg_curr','k_2400_bg_curr')])
 print('TIMING seconds', np.sum(dt), 'step median', np.median(dt),'over bare ramp median',np.median(dt-db*438))
 try:
  on=sdh_onset(R,B,r_full_scale=5000); print(on.summary())
 except SdhOnsetError as e:
  print('ONSET ERROR',e); continue
 out[rid]={'onset':on.onset_b,'tones':[{'freq':t.freq,'onset':t.onset_b,'censored':bool(t.censored)} for t in on.tones]}
 fig,axs=plt.subplots(2,1,figsize=(10,7))
 axs[0].plot(B,R); axs[0].axvline(on.onset_b,color='r'); axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)')
 for lo in sorted(set([on.onset_b,1.,1.5,2.,3.])):
  for degree in (3,5,7):
   f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),bg_degree=degree,log=False,nfft=4096)
   pk,_=find_peaks(sp[0]); pk=sorted([p for p in pk if 3<f[p]<60],key=lambda p:-sp[0,p])[:6]
   print('FFT',rid,'lo',round(lo,3),'degree',degree,'peaks',[(round(float(f[p]),2),round(float(sp[0,p]),2)) for p in pk])
   if degree==5: axs[1].plot(f,sp[0],label=f'B>{lo:.2f}')
 axs[1].set(xlim=(0,60),xlabel='frequency (T)',ylabel='FFT amplitude'); axs[1].legend(); fig.tight_layout(); fig.savefig(f'hera_scratch/spot_{rid}_fft.png'); plt.show()
json.dump(out,open('hera_scratch/spot_results.json','w'),indent=2)
# Local-background onset audit: avoid the large 8-10 T MR bend driving
# the low-field polynomial residual. Keep the full-window result above.
r=open_run('data/6'); ch={c.cid:c for c in resolve_channels(r.meta)}
B=r.col('magnet_field'); R=(r.col('sr1_X')/ch['sr1'].gain)/(r.col('sr0_X')/ch['sr0'].gain)
for hi in (3.,4.,5.):
 for deg in (3,5):
  local=sdh_onset(R,B,b_lo=.3,b_hi=hi,bg_degree=deg,r_full_scale=5000)
  print(f'LOCAL ONSET AUDIT B<= {hi}, degree {deg}:\n{local.summary()}')
local=sdh_onset(R,B,b_lo=.3,b_hi=5,bg_degree=5,r_full_scale=5000)
json.dump({'B_lo':local.onset_b,'B_hi_fit':5.,'degree':5,'run':6,'qualification':'local-background design onset; full-range fit is censored and detrend-sensitive'},open('hera_scratch/fan_onset.json','w'),indent=2)
import sys
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs,bernal_fs,ABA_TRI
ns=np.linspace(2.8,3.2,21)
ab=np.array([[q[0] for q in abab_fs(n*1e16)[1]] for n in ns])
tri=np.array([[q[0] for q in bernal_fs(n*1e16,seq='ABA',p=ABA_TRI)[1]] for n in ns])
fig,ax=plt.subplots(figsize=(8,5))
for j in range(2):
 ax.plot(ns,ab[:,j],color='C0',label='ABAB model' if j==0 else None)
 ax.plot(ns,tri[:,j],'--',color='C1',label='ABA adjacent-N model' if j==0 else None)
ax.plot(ns,10.33916924*ns,color='C2',label='ABCA / Luttinger g=4')
ax.scatter([3.2]*4,[7.1,14.1,22.1,29.5],color='k',marker='x',label='run 6 candidate tones, not assigned')
ax.set(xlabel='n_A (10^12 cm^-2), geometry scale',ylabel='F (T)',title='Fan design: candidate tones vs model branches (scale 1, not a fit)'); ax.legend(); fig.tight_layout(); fig.savefig('hera_scratch/fan_design_overlay.png'); plt.show()
print('Model limits ABAB',ab[[0,-1]],'ABA',tri[[0,-1]])
