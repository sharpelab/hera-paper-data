from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run,sdh_onset
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].plot(B,R); ax[0].set(xlabel='B (T)',ylabel='Raw signed Rxx (Ohm)',xlim=(0,5))
for hi in [4.,5.]:
 for deg in [3,4,5]:
  on=sdh_onset(R,B,b_hi=hi,bg_degree=deg,r_full_scale=5000)
  tone=min(on.tones,key=lambda t:abs(t.freq-7))
  print(f'B_hi={hi}, degree={deg}: headline onset {on.onset_b:.4f}; tracked {tone.freq:.3f} T tone onset {tone.onset_b:.4f}, censored={tone.censored}, marginal={tone.marginal}')
  ax[1].plot(tone.b_centers,tone.snr,label=f'hi={hi}, deg={deg}')
on=sdh_onset(R,B,b_hi=5.,r_full_scale=5000); print(on.summary())
ax[0].axvline(on.onset_b,color='r',ls='--'); ax[1].axhline(5,color='k',ls='--'); ax[1].set(xlabel='B center (T)',ylabel='~7 T tone matched-filter SNR',xlim=(0,5)); ax[1].legend(fontsize=7)
fig.tight_layout(); plt.show()
