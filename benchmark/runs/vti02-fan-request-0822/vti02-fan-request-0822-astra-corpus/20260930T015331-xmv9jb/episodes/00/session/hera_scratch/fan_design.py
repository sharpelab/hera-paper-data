import sys,json
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import h,e
from hera.analysis import open_run,sdh_onset
from sharpelab_nb.gates import calc_gate_voltages,calc_nD
sys.path.insert(0,'/home/hera/measurement_env/hera/models/tetralayer_fs_count')
from fs_count_b0 import abab_fs
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
on=sdh_onset(R,B,b_lo=.3,b_hi=4,bg_degree=5,r_full_scale=5000)
print(on.summary()); blo=on.onset_b
for n in [2.5,2.8,3.0,3.2]:
 fs=[x[0] for x in abab_fs(n*1e16)[1]]
 print(n,fs,'Bhi for 5period',1/(1/blo-5/fs[0]) if 1/blo>5/fs[0] else None)
fig,axs=plt.subplots(2,1,figsize=(10,7))
for hi in [4,10]:
 sel=(B>=.3)&(B<=hi); bg=np.polynomial.Polynomial.fit(B[sel],R[sel],5)(B[sel]); axs[0].plot(B[sel],R[sel]-bg,label=f'background fit .3-{hi} T')
axs[0].set(xlim=(.3,2.5),ylim=(-20,20),xlabel='B (T)',ylabel='Delta R (Ohm)');axs[0].legend()
for t in on.tones:
 if hasattr(t,'snr'): axs[1].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
axs[1].axhline(5,color='k',ls=':');axs[1].set(xlim=(.3,3),ylim=(0,25),xlabel='Window center B (T)',ylabel='SNR');axs[1].legend(ncol=4); fig.tight_layout();fig.savefig('hera_scratch/onset_diagnostic.png')
