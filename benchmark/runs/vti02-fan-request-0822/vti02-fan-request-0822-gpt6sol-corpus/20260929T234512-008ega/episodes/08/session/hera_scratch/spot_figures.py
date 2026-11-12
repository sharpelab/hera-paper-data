import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft

fig, ax = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
for row, (fid,n) in enumerate([(6,3.2),(7,-1.2)]):
    run=open_run(f'data/{fid}')
    b=run.col('magnet_field'); r=run.col('sr1_X')/1e-8
    ix=np.argsort(b); b=b[ix]; r=r[ix]
    ax[row,0].plot(b,r,linewidth=.7)
    ax[row,0].set(xlabel='B (T)',ylabel='Rxx B1-B2 (ohm)',title=f'Raw run {fid}: n={n:+.2f}e12, D=0')
    for lo in (1.5,2.,2.5):
        f,s=sdh_fft(r[:,None],b,b_range=(lo,10),log=False)
        ax[row,1].plot(f,s[0]/np.max(s[0]),label=f'{lo:g}–10 T')
    ax[row,1].axvline(10.339*abs(n),c='k',ls='--',lw=1,label='F_L')
    ax[row,1].set(xlim=(0,50),xlabel='F (T)',ylabel='normalized FFT amplitude',title=f'Run {fid}: window stability')
    ax[row,1].legend(fontsize=8)
fig.savefig('hera_scratch/spot_runs6_7.png',dpi=160)
