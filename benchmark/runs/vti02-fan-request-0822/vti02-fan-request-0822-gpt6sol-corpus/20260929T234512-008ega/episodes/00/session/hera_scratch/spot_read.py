from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, sdh_onset

fig, axs = plt.subplots(2, 3, figsize=(15, 8))
for row, rid in enumerate((6, 7)):
    g = open_run(Path('data') / str(rid))
    B = g.col('magnet_field')
    R = g.col('sr1_X') / (g.col('sr0_X') / -1e6)
    ii = np.argsort(B); B, R = B[ii], R[ii]
    print(f'run {rid}: R range {R.min():.1f}..{R.max():.1f} ohm; R(10T) {R[-1]:.1f}; T {g.col("T_sample").min():.3f}..{g.col("T_sample").max():.3f} K')
    axs[row, 0].plot(B, R); axs[row, 0].set(xlabel='B (T)', ylabel='Rxx (ohm)', title=f'run {rid} raw')
    for col, low in enumerate((0.8, 1.5), start=1):
        freq, spec = sdh_fft(R[:,None], B, b_range=(low, 10), nfft=4096, bg_degree=5, log=False)
        y=spec[0]; p,_=find_peaks(y, prominence=0.06*y.max(), distance=40)
        p=[j for j in p if 1.0<freq[j]<40]
        print(f'  low {low}: peaks ' + ', '.join(f'{freq[j]:.2f}T ({y[j]/y.max():.2f})' for j in sorted(p,key=lambda j:-y[j])[:12]))
        axs[row,col].plot(freq,y); axs[row,col].set(xlim=(0,40),xlabel='F (T)',ylabel='FFT amplitude',title=f'{low}–10T, degree 5')
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png',dpi=150)
