from hera.analysis import open_run, sdh_fft, sdh_onset
from pathlib import Path
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt
r = open_run(str(Path.cwd() / 'data' / '7'))
B = r.col('magnet_field')
I = r.col('sr0_X') / r.meta['measurement_config']['sr0_gain']
R = r.col('sr1_X') / I
order = np.argsort(B); B, R = B[order], R[order]
print(f'run 7: {r.rows} rows, Rxx {R.min():.1f}..{R.max():.1f} Ω, I_med {np.median(I)*1e9:.3f} nA; sample T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
fig, ax = plt.subplots(1,2,figsize=(11,4))
ax[0].plot(B,R,lw=.8); ax[0].set(xlabel='B (T)',ylabel='Rxx (Ω)',title='run 7 raw TSV')
print(sdh_onset(R,B,r_full_scale=5000).summary())
for lo in (1.0,1.5,2.0,2.5):
    f,s = sdh_fft(R[:,None],B,b_range=(lo,10),log=False,nfft=2048,bg_degree=5)
    q=s[0]; peaks,_=find_peaks(q,prominence=q.max()*.05)
    peaks=peaks[(f[peaks]>2)&(f[peaks]<40)]
    peaks=peaks[np.argsort(q[peaks])[-5:][::-1]]
    print(f'FFT {lo:.1f}..10 T: '+', '.join(f'{f[p]:.1f} T' for p in peaks))
    ax[1].plot(f,q/q.max(),label=f'B>{lo:g}')
ax[1].axvline(12.4,color='k',ls=':',lw=1,label='F_L prior')
ax[1].set(xlim=(0,32),xlabel='F (T)',ylabel='normalized amplitude',title='1/B FFT, degree-5 B detrend');ax[1].legend(fontsize=8)
fig.tight_layout();plt.show()
