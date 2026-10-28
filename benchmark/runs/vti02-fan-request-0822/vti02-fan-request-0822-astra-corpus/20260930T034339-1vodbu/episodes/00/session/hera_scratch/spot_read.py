from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, sdh_onset, sdh_fft, resolve_channels, current_channel
for fid in (6,7):
    r=open_run(f'data/{fid}')
    fig=plot_raw(r); fig.savefig(f'hera_scratch/raw_spot_{fid}.png',dpi=150); plt.show()
    channels=resolve_channels(r.meta); cur=current_channel(channels); v=next(c for c in channels if c.cid=='sr1')
    R=(r.col(v.col)/v.gain)/(r.col(cur.col)/cur.gain); B=r.col('magnet_field')
    print('RUN',fid,'completed',r.complete,'interrupted',r.interrupted)
    for blo in ([.3,1.] if fid==6 else [.3]):
        on=sdh_onset(R,B,b_lo=blo,r_full_scale=5000); print(on.summary())
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for degree in (3,5,7):
        f,sp=sdh_fft(R[:,None],B,b_range=(1,8),nfft=4096,bg_degree=degree,log=False)
        axes[0].plot(f,sp[0]/sp[0].max(),label=f'B=1–8, degree {degree}')
    for lo in (1,1.3,1.6,2):
        f,sp=sdh_fft(R[:,None],B,b_range=(lo,8),nfft=4096,log=False)
        axes[1].plot(f,sp[0]/sp[0].max(),label=f'B={lo}–8')
    for ax in axes:
        ax.set(xlim=(0,65),xlabel='Frequency (T)',ylabel='Normalized spectral magnitude'); ax.legend()
    fig.suptitle(f'Run {fid}: window/background stability (positive B only; no even-B symmetrization)')
    fig.tight_layout(); fig.savefig(f'hera_scratch/fft_spot_{fid}.png',dpi=150); plt.show()
