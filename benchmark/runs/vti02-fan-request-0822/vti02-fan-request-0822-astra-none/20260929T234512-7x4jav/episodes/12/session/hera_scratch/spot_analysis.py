from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft

for rid in (6,7):
 r=open_run(Path('data')/str(rid)); cs=resolve_channels(r.meta); ci=current_channel(cs); cv=next(c for c in cs if c.cid=='sr1')
 b=r.col('magnet_field'); I=r.col(ci.col)/ci.gain; V=r.col(cv.col)/cv.gain; R=V/I
 print(f'RUN {rid}: R {R.min():.2f}..{R.max():.2f} Ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; X max {max(abs(V))*1e6:.2f} uV; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
 for col in ('k_2400_tg_curr','k_2400_bg_curr'): print(col, np.quantile(r.col(col)*1e12,[0,.5,1]))
 fig,ax=plt.subplots(2,2,figsize=(11,6));ax[0,0].plot(b,V*1e6);ax[0,0].set_ylabel('raw sr1 X (uV)');ax[0,1].plot(b,I*1e9);ax[0,1].set_ylabel('drain current (nA)');ax[1,0].plot(b,R);ax[1,0].set_ylabel('Rxx (Ohm)');ax[1,1].plot(b,r.col('sr1_P'));ax[1,1].set_ylabel('sr1 phase (deg)')
 for a in ax.flat:a.set_xlabel('B (T)')
 fig.suptitle(f'Run {rid}: raw channels then Rxx');fig.tight_layout();fig.savefig(f'hera_scratch/spot_{rid}_raw.png');plt.show()
 try:
  onset=sdh_onset(R,b,r_full_scale=5000);print(onset.summary())
 except ValueError as exc:print('ONSET UNRESOLVED:',exc)
 fig,ax=plt.subplots(figsize=(8,4))
 for lo in (1,2,3):
  f,sp=sdh_fft(R[:,None],b,b_range=(lo,10),nfft=4096,log=False)
  ax.plot(f,sp[0]/max(sp[0]),label=f'{lo}..10 T')
 ax.set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT');ax.legend();ax.set_title(f'Run {rid}: window robustness, no band assignment');fig.tight_layout();fig.savefig(f'hera_scratch/spot_{rid}_fft.png');plt.show()
