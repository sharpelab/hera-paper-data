from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft

fig, axs = plt.subplots(2, 2, figsize=(12, 7))
for row, rid in enumerate((6, 7)):
    run = open_run(Path('data') / str(rid))
    print(summarize_run(run))
    B = run.col('magnet_field')
    current = run.col('sr0_X') / run.meta['measurement_config']['sr0_gain']
    R = np.abs(run.col('sr1_X') / current)
    T = run.col('T_sample')
    print(f'run {rid}: R {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm, I {np.nanmin(current)*1e9:.2f}..{np.nanmax(current)*1e9:.2f} nA, T {T.min():.3f}..{T.max():.3f} K, B {B.min():.3f}..{B.max():.3f} T')
    axs[row,0].plot(B,R,'.',ms=1.5)
    axs[row,0].set(xlabel='B (T)',ylabel='|Rxx| (Ohm)',title=f'run {rid} raw')
    order = np.argsort(B)
    try:
        onset = sdh_onset(R[order],B[order],b_lo=1.0,b_hi=9.5,r_full_scale=5000)
        print(f'run {rid} onset:',onset.summary())
    except Exception as exc:
        print(f'run {rid} onset error:',type(exc).__name__,str(exc))
    mask = (B[order]>=2.5)&(B[order]<=9.5)
    f,spec=sdh_fft(R[order][mask,None],B[order][mask],b_range=(2.5,9.5),nfft=1024,bg_degree=5)
    ix=np.argsort(spec[0][(f>2)&(f<60)])[-8:]
    ff=f[(f>2)&(f<60)][ix]; ss=spec[0][(f>2)&(f<60)][ix]
    print('top FFT',list(zip(np.round(ff,2),np.round(ss,1))))
    axs[row,1].plot(f,spec[0]); axs[row,1].set(xlim=(0,60),xlabel='F (T)',ylabel='FFT amplitude',title=f'run {rid}, 2.5-9.5 T')
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png',dpi=140)
