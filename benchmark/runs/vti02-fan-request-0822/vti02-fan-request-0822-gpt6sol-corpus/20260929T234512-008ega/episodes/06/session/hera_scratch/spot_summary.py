import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency

fig, axs = plt.subplots(2, 2, figsize=(12, 7))
for j, (rid, n) in enumerate(((6, 3.2), (7, -1.2))):
    run = open_run(Path('data') / str(rid))
    order = np.argsort(run.col('magnet_field'))
    b = run.col('magnet_field')[order]
    r = run.col('sr1_X')[order] / 1e-8
    i0 = run.col('sr0_X')[order] / -1e6
    ax = axs[j, 0]
    ax.plot(b, r, lw=.8, label='Rxx')
    ax.set(xlabel='B (T)', ylabel='Rxx (Ω)', title=f'Run {rid}: n={n:+.1f}×10¹² cm⁻², D≈0')
    ax.grid(alpha=.2)
    ax.text(.02,.96,f'Ibias 10 nA; drain {np.median(i0)*1e9:.2f} nA\nT {run.col("T_sample").min():.3f}–{run.col("T_sample").max():.3f} K',transform=ax.transAxes,va='top',fontsize=8)
    ax=axs[j,1]
    for cutoff, style in [(1.5,'-'),(2.0,'--')]:
        f, sp = sdh_fft(r[:,None],b,b_range=(cutoff,10),bg_degree=5,log=False,nfft=4096)
        sp=sp[0]
        m=(f>2)&(f<50)
        ax.plot(f[m],sp[m]/max(sp[m]),style,label=f'B≥{cutoff} T')
    fl=float(luttinger_frequency(n*1e16))
    ax.axvline(fl,color='k',lw=1,alpha=.5,label=f'F_L={fl:.1f} T')
    ax.set(xlabel='frequency (T)',ylabel='relative FFT amplitude',xlim=(0,50),title='FFT (B detrend, Hann)')
    ax.legend(fontsize=8)
    ax.grid(alpha=.2)
fig.tight_layout()
fig.savefig('hera_scratch/spot_runs6_7.png',dpi=150)
print('saved hera_scratch/spot_runs6_7.png')
