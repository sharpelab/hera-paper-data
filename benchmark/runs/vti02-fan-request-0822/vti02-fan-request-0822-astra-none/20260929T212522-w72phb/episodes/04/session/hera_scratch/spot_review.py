from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
fig, ax = plt.subplots(3, 2, figsize=(12,10))
for j,rid in enumerate((6,7)):
    r=open_run(Path('data')/str(rid)); ch={c.cid:c for c in resolve_channels(r.meta)}
    B=r.col('magnet_field'); I=r.col('sr0_X')/ch['sr0'].gain
    R=r.col('sr1_X')/ch['sr1'].gain/I
    ix=np.argsort(B); B=B[ix]; R=R[ix]
    print(f'Run {rid}: {r.rows} pts, R signed {R.min():.2f}..{R.max():.2f} Ohm, I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K, sr1 peak fraction {np.max(abs(r.col("sr1_X")))/50e-6:.3f}')
    print('gate max abs pA',*[np.max(abs(r.col(k)))*1e12 for k in ('k_2400_tg_curr','k_2400_bg_curr')])
    ax[0,j].plot(B,R,lw=.8); ax[0,j].set(title=f'Run {rid}: raw signed V/I',xlabel='B (T)',ylabel='R (Ohm)')
    ax[1,j].plot(r.col('magnet_field'),r.col('sr1_P'),label='voltage'); ax[1,j].plot(r.col('magnet_field'),r.col('sr0_P'),label='current'); ax[1,j].set(xlabel='B (T)',ylabel='Phase (degree)');ax[1,j].legend()
    try:
        o=sdh_onset(R,B,r_full_scale=5000)
        print(o.summary())
    except ValueError as e: print('ONSET unresolved:',e)
    for lo in (1.5,2,2.5):
        f,a=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=4096,log=False,bg_degree=3)
        ax[2,j].plot(f,a[0]/max(a[0]),label=f'{lo}-10 T')
    ax[2,j].set(xlim=(0,65),xlabel='F (T)',ylabel='FFT normalized');ax[2,j].legend()
fig.tight_layout();fig.savefig('hera_scratch/spot_review.png',dpi=150)
plt.show()
# Timing: within-row point intervals exclude flyback and slow moves.
r=open_run('data/5'); dt=np.diff(r.col('time'));same=np.diff(r.col('k_2400_bg_volt'))==0
print('run 5 within-row median/mean s',np.median(dt[same]),np.mean(dt[same]),'row boundary median',np.median(dt[~same]))
for rid in (6,7):
    r=open_run(f'data/{rid}'); dt=np.diff(r.col('time'));db=abs(np.diff(r.col('magnet_field')))
    print(rid,'non-ramp overhead median s',np.median(dt-db*7.3*60))
