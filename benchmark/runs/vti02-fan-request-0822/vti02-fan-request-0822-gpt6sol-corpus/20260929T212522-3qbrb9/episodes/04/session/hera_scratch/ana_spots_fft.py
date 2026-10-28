# FFT after raw inspection. The lower cutoff is varied to expose sensitivity
# to the MR background; no stacking classification is made on these spectra.
from hera.analysis import sdh_onset, sdh_fft
import numpy as np
import matplotlib.pyplot as plt

fig, axs = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
for row, (fid, n, bmin) in enumerate(((6, +3.2, 0.05), (7, -1.2, 0.30))):
    q = run(fid)
    B = q.col('magnet_field')
    R = q.col('sr1_X') / (q.col('sr0_X') / -1e6)
    on = sdh_onset(R, B, b_lo=bmin, f_min=5, r_full_scale=5000)
    print(f'run {fid}: {on.summary()}')
    for cut in (1.0, 1.5, 2.0):
        f, S = sdh_fft(R[:, None], B, b_range=(cut, 10.0), log=False, nfft=4096)
        axs[row].plot(f, S[0] / np.nanmax(S[0]), label=f'B ≥ {cut:.1f} T')
    FL = luttinger_frequency(abs(n) * 1e16)  # n listed in 1e12 cm^-2; helper takes m^-2
    axs[row].axvline(FL, color='k', lw=1, ls=':', label=f'F_L={FL:.1f} T')
    axs[row].set(ylabel='normalized FFT amplitude', title=f'run {fid}: n={n:+.1f}e12')
    axs[row].legend(fontsize=8)
axs[-1].set(xlim=(0, 65), xlabel='frequency (T)')
fig.tight_layout(); plt.show()
