from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError
import numpy as np
from scipy.signal import find_peaks
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, axs = plt.subplots(2,2,figsize=(12,7))
for row,i in enumerate((6,7)):
    run=open_run(f'data/{i}')
    B=run.col('magnet_field')
    I=run.col('sr0_X')/run.meta['measurement_config']['sr0_gain']
    R=(run.col('sr1_X')/1)/I
    order=np.argsort(B); B=B[order]; R=R[order]
    print(f'run {i}: B {B.min():.2f}-{B.max():.2f}, I {np.median(I)*1e9:.3f}nA, R {R.min():.1f}-{R.max():.1f}ohm, T {np.min(run.col("T_sample")):.3f}-{np.max(run.col("T_sample")):.3f}K')
    axs[row,0].plot(B,R,lw=.7); axs[row,0].set(xlabel='B (T)',ylabel='Rxx (Ohm)',title=f'run {i} raw')
    try:
        on=sdh_onset(R,B,r_full_scale=5000)
        print(on.summary())
    except SdhOnsetError as e:
        print('ONSET ERROR:',e)
    for blo in ((1.5,2,2.5,3) if i==6 else (1,1.5,2,2.5)):
        f,s=sdh_fft(R[:,None],B,b_range=(blo,10),log=False,nfft=2048,bg_degree=5)
        sp=s[0]; peaks,_=find_peaks(sp,prominence=np.max(sp)*.05)
        peaks=peaks[(f[peaks]>2)&(f[peaks]<50)]
        peaks=peaks[np.argsort(sp[peaks])[-6:][::-1]]
        print(f'  FFT B {blo}-10: '+', '.join(f'{f[p]:.2f}T({sp[p]:.2g})' for p in peaks))
        axs[row,1].plot(f,sp/np.max(sp),label=f'B>{blo}')
    axs[row,1].set(xlim=(0,50),xlabel='F (T)',ylabel='FFT normalized',title=f'run {i} FFT');axs[row,1].legend()
fig.tight_layout();fig.savefig('hera_scratch/spot_runs6_7.png',dpi=150)
