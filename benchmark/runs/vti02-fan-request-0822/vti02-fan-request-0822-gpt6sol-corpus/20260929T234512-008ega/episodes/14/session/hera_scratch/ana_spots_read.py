from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
from scipy.signal import find_peaks

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for k, rid in enumerate((6,7)):
    r=open_run(Path('data')/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
    B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
    R=(r.col('sr1_X')/ch['sr1'].gain)/I
    on=sdh_onset(R,B,r_full_scale=5000.)
    print(f'run {rid}:\n{on.summary()}')
    for lo,style in ((1.0,'-'),(1.5,'--')):
        f,S=sdh_fft(R[:,None],B,b_range=(lo,10.),bg_degree=5,log=False)
        y=S[0]; norm=np.median(y[f>3]); pk,_=find_peaks(y,prominence=3*norm)
        pk=sorted((i for i in pk if f[i]>3),key=lambda i:-y[i])[:6]
        print(f'  FFT {lo:.1f}–10 T: ΔF={f[1]-f[0]:.2f} T; peaks '+str([(round(f[i],1),round(y[i]/norm,1)) for i in pk]))
        ax[k].plot(f,y/norm,style,lw=1,label=f'{lo:g}–10 T')
    FL=10.339*(3.2 if rid==6 else 1.2)
    ax[k].axvline(FL,color='k',ls=':',lw=1,label=f'F_L={FL:.1f} T')
    ax[k].set_xlim(0,45); ax[k].set_yscale('log');ax[k].set_xlabel('frequency (T)');ax[k].set_ylabel('FFT / median floor')
    ax[k].set_title(f'run {rid} '+('electron' if rid==6 else 'hole'));ax[k].legend(fontsize=8)
fig.tight_layout();plt.show()
