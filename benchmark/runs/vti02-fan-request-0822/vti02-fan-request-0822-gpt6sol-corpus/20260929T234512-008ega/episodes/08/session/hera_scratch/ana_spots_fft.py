from hera.analysis import open_run, sdh_onset, sdh_fft
import numpy as np
import matplotlib.pyplot as plt

fig, axs = plt.subplots(1, 2, figsize=(11, 3.5), constrained_layout=True)
for ax, (fid, n) in zip(axs, ((6, 3.2), (7, -1.2))):
    run = open_run(f'data/{fid}')
    b, rxx = run.col('magnet_field'), run.col('sr1_X') / 1e-8
    onset = sdh_onset(rxx, b, b_lo=0.3, r_full_scale=5000)
    print(f'Run {fid}:', onset.summary())
    for cutoff in (1.5, 2.0, 2.5):
        f, spec = sdh_fft(rxx[:,None], b, b_range=(cutoff, 10), log=False)
        ax.plot(f, spec[0]/np.max(spec[0]), label=f'{cutoff:g}-10 T')
    ax.axvline(10.339*abs(n), color='k', ls='--', lw=1, label='F_L')
    ax.set(xlim=(0, 50), xlabel='F (T)', ylabel='normalized FFT amplitude', title=f'Run {fid}: n={n:+.2f}e12')
    ax.legend(fontsize=8)
plt.show()
