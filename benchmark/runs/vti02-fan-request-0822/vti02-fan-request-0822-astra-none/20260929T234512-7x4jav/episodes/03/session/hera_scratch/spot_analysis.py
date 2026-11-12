from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft
root = Path.cwd()
fig, ax = plt.subplots(3,2,figsize=(12,9))
traces=[]
for j,rid in enumerate((6,7)):
 r=open_run(root/'data'/str(rid)); cs=resolve_channels(r.meta); ci=current_channel(cs); cv=next(c for c in cs if c.cid=='sr1')
 B=r.col('magnet_field'); I=r.col(ci.col)/ci.gain; R=(r.col(cv.col)/cv.gain)/I
 ax[0,j].plot(B,r.col(cv.col)*1e6); ax[0,j].set_ylabel('raw sr1 X (uV)')
 ax[1,j].plot(B,I*1e9); ax[1,j].set_ylabel('drain I (nA)')
 for c in ('k_2400_tg_curr','k_2400_bg_curr'): ax[2,j].plot(B,r.col(c)*1e12,label=c)
 ax[2,j].legend(fontsize=7); ax[2,j].set_ylabel('gate I (pA)'); ax[2,j].set_xlabel('B (T)'); ax[0,j].set_title(f'data/{rid}')
 print(f'RUN {rid}: R signed {R.min():.2f}..{R.max():.2f} Ohm, current {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K; max gate {max(np.max(np.abs(r.col(c))) for c in ("k_2400_tg_curr","k_2400_bg_curr"))*1e12:.1f} pA')
 traces.append((rid,B,R))
fig.tight_layout(); fig.savefig(root/'hera_scratch/spot_raw.png',dpi=140); plt.show()
fig,ax=plt.subplots(2,2,figsize=(12,7))
for j,(rid,B,R) in enumerate(traces):
 ax[0,j].plot(B,R,lw=0.8); ax[0,j].set(xlabel='B (T)',ylabel='signed V/I (Ohm)',title=f'data/{rid}')
 for lo in (1,2,3):
  f,spec=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,nfft=4096,bg_degree=3)
  ax[1,j].plot(f,spec[0]/spec[0].max(),label=f'{lo}-10 T')
 ax[1,j].set(xlim=(0,65),xlabel='F (T)',ylabel='normalized FFT'); ax[1,j].legend()
 try:
  onset=sdh_onset(R,B,r_full_scale=5000,b_lo=0.3)
  print(f'RUN {rid} onset:\n{onset.summary()}')
 except ValueError as e: print(f'RUN {rid} onset unresolved: {e}')
fig.tight_layout(); fig.savefig(root/'hera_scratch/spot_sdh.png',dpi=140); plt.show()
r=open_run(root/'data/5'); times=r.col('time').reshape(63,66); inner=np.diff(times,axis=1); turn=times[1:,0]-times[:-1,-1]
print('Run 5 timing: within-row median / p95',np.quantile(inner,[.5,.95]),'turn median / p95',np.quantile(turn,[.5,.95]))
