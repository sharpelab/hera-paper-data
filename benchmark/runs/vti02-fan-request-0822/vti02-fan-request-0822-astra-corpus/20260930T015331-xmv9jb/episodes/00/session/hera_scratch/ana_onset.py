from hera.analysis import open_run,sdh_onset
import numpy as np
import matplotlib.pyplot as plt
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/r.meta['measurement_config']['sr0_gain'])
on=sdh_onset(R,B,b_hi=4,bg_degree=5,r_full_scale=5000)
print(on.summary())
fig,ax=plt.subplots(2,1,figsize=(10,7))
for hi in (4,10):
 sel=(B>=.3)&(B<=hi)
 bg=np.polynomial.Polynomial.fit(B[sel],R[sel],5)(B[sel])
 ax[0].plot(B[sel],R[sel]-bg,label=f'fit 0.3–{hi} T')
ax[0].set(xlim=(.3,2.5),ylim=(-25,25),xlabel='B (T)',ylabel='Residual Rxx (Ohm)'); ax[0].legend()
for t in on.tones:
 ax[1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
ax[1].axhline(5,color='k',ls=':'); ax[1].set(xlim=(.3,3),ylim=(0,25),xlabel='Window center B (T)',ylabel='SNR'); ax[1].legend(ncol=4)
fig.tight_layout(); plt.show()
