from hera.analysis import open_run, resolve_channels, current_channel
import matplotlib.pyplot as plt
import numpy as np

fig, axs=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
for j,rid in enumerate((6,7)):
    r=open_run(f'data/{rid}')
    cs=resolve_channels(r.meta)
    c=current_channel(cs)
    v=next(x for x in cs if x.cid=='sr1')
    B=r.col('magnet_field')
    R=np.abs((r.col(v.col)/v.gain)/(r.col(c.col)/c.gain))
    o=np.argsort(B)
    axs[j,0].plot(B[o],R[o],lw=.6)
    axs[j,0].set(xlabel='B (T)',ylabel='|Rxx| (ohm)',title=f'run {rid} raw')
    m=(B[o]>1)
    axs[j,1].plot(1/B[o][m],R[o][m],lw=.6)
    axs[j,1].set(xlabel='1/B (1/T)',ylabel='|Rxx| (ohm)',title=f'run {rid} raw vs 1/B')
fig.savefig('hera_scratch/spot_raw.png',dpi=160)
