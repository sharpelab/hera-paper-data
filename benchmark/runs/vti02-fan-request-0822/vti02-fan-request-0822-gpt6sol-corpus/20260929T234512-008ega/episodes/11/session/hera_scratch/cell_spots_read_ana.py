from hera.analysis import sdh_onset, sdh_fft
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for a, r, label in zip(ax, (r6, r7), ('electron +3.2', 'hole -1.2')):
    B = r.col('magnet_field')
    I = r.col('sr0_X') / -1e6
    R = r.col('sr1_X') / I
    on = sdh_onset(R, B, r_full_scale=50e-6 / 1e-8)
    print(f'run {r.path.name}: {on.summary()}')
    print(f'Rxx {np.nanmin(R):.1f}–{np.nanmax(R):.1f} Ω; I {np.nanmin(I)*1e9:.3f}–{np.nanmax(I)*1e9:.3f} nA; '
          f'T {np.nanmin(r.col("T_sample")):.3f}–{np.nanmax(r.col("T_sample")):.3f} K')
    for cutoff in (1., 1.5, 2., 2.5):
        f, S = sdh_fft(R[:, None], B, b_range=(cutoff, 10), nfft=1024, bg_degree=5, log=False)
        a.plot(f, S[0]/np.nanmax(S[0]), label=f'{cutoff:g}–10 T')
    a.set(xlim=(0, 45), ylim=(0, 1.1), xlabel='FFT frequency (T)', title=label)
    a.legend(fontsize=8)
ax[0].set_ylabel('normalized amplitude')
fig.tight_layout()
display(fig)
plt.close(fig)
