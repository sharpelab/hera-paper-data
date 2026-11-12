from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

fig, axs = plt.subplots(2, 2, figsize=(12, 7))
for j, (rid, n) in enumerate(((6, 3.2), (7, -1.2))):
    rr = open_run(Path('/home/hera/measurements/zack/20260822-vti-02/data') / str(rid))
    order = np.argsort(rr.col('magnet_field'))
    b = rr.col('magnet_field')[order]
    rxx = rr.col('sr1_X')[order] / 1e-8  # sr1 unity, I_bias = 10 nA
    drain = rr.col('sr0_X')[order] / -1e6
    ax = axs[j, 0]
    ax.plot(b, rxx, lw=.8)
    ax.set(xlabel='B (T)', ylabel='Rxx (Ω)', title=f'Run {rid}: n={n:+.1f}×10¹² cm⁻², D≈0')
    ax.grid(alpha=.2)
    ax.text(.02,.96,f'drain {np.median(drain)*1e9:.2f} nA; T {rr.col("T_sample").min():.3f}–{rr.col("T_sample").max():.3f} K',transform=ax.transAxes,va='top',fontsize=8)
    ax = axs[j,1]
    for cutoff, style in ((1.5,'-'),(2.0,'--')):
        f, sp = sdh_fft(rxx[:,None],b,b_range=(cutoff,10),bg_degree=5,log=False,nfft=4096)
        sp = sp[0]
        mask = (f>2)&(f<50)
        ax.plot(f[mask],sp[mask]/sp[mask].max(),style,label=f'B≥{cutoff} T')
    fl = float(luttinger_frequency(n*1e16))
    ax.axvline(fl,color='k',lw=1,alpha=.5,label=f'F_L={fl:.1f} T')
    ax.set(xlabel='frequency (T)',ylabel='relative FFT amplitude',xlim=(0,50),title='FFT (B detrend, Hann)')
    ax.legend(fontsize=8)
    ax.grid(alpha=.2)
fig.tight_layout()
plt.show()
