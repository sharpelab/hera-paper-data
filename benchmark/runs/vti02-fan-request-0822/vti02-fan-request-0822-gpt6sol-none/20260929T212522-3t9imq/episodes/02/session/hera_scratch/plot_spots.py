import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run,resolve_channels,current_channel
fig,ax=plt.subplots(2,2,figsize=(12,8))
for k,rid in enumerate((6,7)):
 r=open_run(f'data/{rid}'); B=r.col('magnet_field'); ch=resolve_channels(r.meta); cur=current_channel(ch); v=next(c for c in ch if c.n==1)
 R=np.abs((r.col(v.col)/v.gain)/(r.col(cur.col)/cur.gain)); m=np.argsort(B)
 ax[k,0].plot(B[m],R[m],lw=.7); ax[k,0].set(xlabel='B (T)',ylabel='|Rxx| (Ohm)',title=f'run {rid} raw')
 ax[k,1].plot(1/B[m][B[m]>0.5],R[m][B[m]>0.5],lw=.7);ax[k,1].set(xlabel='1/B (1/T)',ylabel='|Rxx| (Ohm)',title=f'run {rid} raw vs 1/B')
fig.tight_layout();fig.savefig('hera_scratch/spots_raw.png',dpi=160)
