import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft
fig,axs=plt.subplots(2,3,figsize=(15,8))
for row,rid in enumerate([6,7]):
 r=open_run(f'data/{rid}'); ch={c.cid:c for c in resolve_channels(r.meta)}
 print(summarize_run(r)); print('columns',r.cols); print('config',r.meta['measurement_config'])
 B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain; R=r.col('sr1_X')/ch['sr1'].gain/I
 print('stats',{'R_range': [R.min(),R.max()], 'I_nA':[I.min()*1e9,I.max()*1e9], 'T':[r.col('T_sample').min(),r.col('T_sample').max()], 'max_gate_pA':[np.max(np.abs(r.col(c)))*1e12 for c in ['k_2400_tg_curr','k_2400_bg_curr']], 'duration_min':(r.data[-1,0]-r.data[0,0])/60, 'median_dt':np.median(np.diff(r.data[:,0]))})
 axs[row,0].plot(B,r.col('sr1_X')*1e6,label='sr1 X (uV)');axs[row,0].plot(B,I*1e9,label='drain (nA)');axs[row,0].legend();axs[row,0].set_title(f'run {rid}: raw');axs[row,0].set_xlabel('B (T)')
 axs[row,1].plot(B,R);axs[row,1].set_ylabel('Rxx (Ohm)');axs[row,1].set_xlabel('B (T)')
 try:
  onset=sdh_onset(R,B,r_full_scale=5000);print(onset.summary())
 except Exception as exc:print(type(exc).__name__,str(exc))
 f,s=sdh_fft(R[:,None],B,b_range=(1,10),log=False)
 axs[row,2].plot(f,s[0]);axs[row,2].set_xlim(0,60);axs[row,2].set_xlabel('frequency (T)');axs[row,2].set_title('1-10 T FFT; resolution ~1.1 T')
fig.tight_layout();fig.savefig('hera_scratch/spot_read.png',dpi=140)
for rid in [0,5,6,7]:
 r=open_run(f'data/{rid}');dt=np.diff(r.data[:,0]);print('TIMING',rid,'n',r.rows,'elapsed_min',(r.data[-1,0]-r.data[0,0])/60,'dt_q',np.quantile(dt,[0.1,0.5,0.9,0.99]))
 if rid==5:print('delay',r.meta.get('fast_delay'),r.meta.get('slow_delay'))
