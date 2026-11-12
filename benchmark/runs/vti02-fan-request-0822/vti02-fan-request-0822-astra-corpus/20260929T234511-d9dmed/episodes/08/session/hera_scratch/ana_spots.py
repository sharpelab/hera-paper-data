from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
root = Path(file_path) if 'file_path' in globals() else Path.cwd()/'data'
for rid in (6,7):
    r = open_run(root/str(rid))
    plot_raw(r); plt.show()
    cs=resolve_channels(r.meta); cur=current_channel(cs); v=next(c for c in cs if c.cid=='sr1')
    I=r.col(cur.col)/cur.gain; R=(r.col(v.col)/v.gain)/I; B=r.col('magnet_field')
    print(f'Run {rid}: complete={r.complete}, elapsed={(r.meta["end_time"]-r.meta["start_time"])/60:.2f} min')
    print('R min/max',R.min(),R.max(),'I nA',I.min()*1e9,I.max()*1e9)
    full=sdh_onset(R,B,r_full_scale=5000); print('Full-record diagnostic:'); print(full.summary())
    on=sdh_onset(R,B,b_hi=5,r_full_scale=5000) if rid==6 else full
    print('Design-window diagnostic:'); print(on.summary())
    fig,ax=plt.subplots(1,2,figsize=(12,4))
    for t in on.tones:
        ax[0].plot(t.b_centers,t.snr,label=f'{t.freq:.1f} T')
    ax[0].axhline(5,color='k',ls=':');ax[0].set(xlabel='B (T)',ylabel='SNR',yscale='log');ax[0].legend(fontsize=7)
    for lo in [on.onset_b,1.5,2.0]:
        for deg in [3,5,7]:
            f,p=sdh_fft(R[:,None],B,b_range=(lo,10),log=False,bg_degree=deg,nfft=2048)
            ax[1].plot(f,p[0]/p[0].max(),label=f'{lo:.2f}–10 T / degree {deg}',alpha=.6)
    ax[1].set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT');ax[1].legend(fontsize=6)
    fig.suptitle(f'Run {rid} — signed R; positive-B only');fig.tight_layout();plt.show()
