import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
for fid in (6,7):
    r=open_run(f'data/{fid}')
    plot_raw(r)
    plt.show()
    cs=resolve_channels(r.meta); ci=current_channel(cs); cv=next(c for c in cs if c.cid=='sr1')
    R=(r.col(cv.col)/cv.gain)/(r.col(ci.col)/ci.gain)
    B=r.col('magnet_field')
    print(f'run {fid}:', sdh_onset(R,B,r_full_scale=5000).summary())
    if fid==6:
        print('Adequately sampled portion:',sdh_onset(R,B,b_lo=1,r_full_scale=5000).summary())
    fig,axs=plt.subplots(1,3,figsize=(13,3.5))
    for ax,low in zip(axs,(1,1.5,2)):
        for degree in (3,5,7):
            f,sp=sdh_fft(R[:,None],B,b_range=(low,10),bg_degree=degree,log=False,nfft=4096)
            ax.plot(f,sp[0]/max(sp[0]),label=f'degree {degree}')
        ax.set(xlim=(0,65),xlabel='F (T)',ylabel='Normalized FFT',title=f'run {fid}: B {low}–10 T')
        ax.legend()
    plt.tight_layout(); plt.show()
