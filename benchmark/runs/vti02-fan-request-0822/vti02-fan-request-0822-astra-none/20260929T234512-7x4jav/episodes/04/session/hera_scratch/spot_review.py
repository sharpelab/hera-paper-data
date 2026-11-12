from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
root=Path(file_path).parent if "file_path" in globals() else Path.cwd()
fig, ax=plt.subplots(2,3,figsize=(15,8))
for j,i in enumerate([6,7]):
 r=open_run(root/'data'/str(i)); cc=resolve_channels(r.meta); ic=current_channel(cc); vc=next(c for c in cc if c.cid=='sr1')
 I=r.col(ic.col)/ic.gain; R=(r.col(vc.col)/vc.gain)/I; B=r.col('magnet_field')
 ax[j,0].plot(B,r.col(vc.col)*1e6,label='raw sr1 X (uV)'); ap=ax[j,0].twinx(); ap.plot(B,r.col('sr1_P'),color='tab:orange',alpha=.4); ap.set_ylabel('phase (deg)'); ax[j,0].set_ylabel('raw X (uV)'); ax[j,0].legend(); ax[j,0].set_title(f'run {i}: raw'); ax[j,0].set_xlabel('B (T)')
 ax[j,1].plot(B,R); ax[j,1].set_xlabel('B (T)'); ax[j,1].set_ylabel('signed V/I (ohm)')
 print(f'run {i}: signed R {R.min():.2f}..{R.max():.2f} ohm; negative points {np.sum(R<0)}; current {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
 for lo in [1.5,2,3]:
  f,sp=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=2048,log=False,bg_degree=3)
  ax[j,2].plot(f,sp[0]/sp[0].max(),label=f'{lo}..10 T')
 ax[j,2].set_xlim(0,60); ax[j,2].set_xlabel('F (T)'); ax[j,2].legend()
 try: print(sdh_onset(R,B,b_lo=1.5,r_full_scale=5000).summary())
 except ValueError as e: print(e)
fig.tight_layout(); fig.savefig(root/'hera_scratch/spot_review.png',dpi=140)
plt.show()
