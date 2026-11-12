from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft

fig, axs = plt.subplots(2, 2, figsize=(12, 7))
for row, rid in enumerate((6, 7)):
    r = open_run(Path('data')/str(rid))
    c = {ch.cid: ch for ch in resolve_channels(r.meta)}
    b = r.col('magnet_field'); I = r.col('sr0_X') / c['sr0'].gain
    R = np.abs(r.col('sr1_X') / c['sr1'].gain / I)
    axs[row,0].plot(b,R,lw=.8); axs[row,0].set(xlabel='B (T)',ylabel='|Rxx| (Ω)',title=f'run {rid}: raw Rxx')
    axs[row,0].grid(alpha=.2)
    for lo,hi in ((.8,10),(1.5,10),(2,10)):
        f,s=sdh_fft(R[:,None],b,b_range=(lo,hi),nfft=2048,bg_degree=3,log=False)
        axs[row,1].plot(f,s[0]/s[0].max(),label=f'{lo}-{hi} T')
    axs[row,1].set(xlim=(0,50),xlabel='F (T)',ylabel='normalized FFT',title=f'run {rid}: SdH spectra')
    axs[row,1].legend()
fig.tight_layout(); fig.savefig('hera_scratch/spot_runs6_7.png',dpi=150)
