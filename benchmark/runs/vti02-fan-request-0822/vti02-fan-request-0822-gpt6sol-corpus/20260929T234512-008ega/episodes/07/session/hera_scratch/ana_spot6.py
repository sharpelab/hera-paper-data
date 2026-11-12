from hera.analysis import sdh_onset, resolve_channels
from scipy.signal import find_peaks

r6 = run(6)
print(summarize_run(r6))
B6 = r6.col('magnet_field')
I6 = r6.col('sr0_X') / r6.meta['measurement_config']['sr0_gain']
R6 = np.abs(r6.col('sr1_X') / I6)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(B6, R6, lw=1); ax[0].set(xlabel='B (T)', ylabel='|Rxx| (Ohm)', title='Run 6: raw measured-current Rxx')
ax[1].plot(B6, I6 * 1e9, lw=1); ax[1].set(xlabel='B (T)', ylabel='drain current (nA)', title='Run 6: raw drain current')
fig.tight_layout(); plt.show()
print('raw: Rmax = %.0f Ohm, |I_tg|max = %.0f pA, |I_bg|max = %.0f pA, T = %.3f–%.3f K' %
      (R6.max(), np.max(np.abs(r6.col('k_2400_tg_curr'))) * 1e12,
       np.max(np.abs(r6.col('k_2400_bg_curr'))) * 1e12,
       r6.col('T_sample').min(), r6.col('T_sample').max()))

o6 = sdh_onset(R6, B6, b_lo=0.3, r_full_scale=5000)
print(o6.summary())
fig, ax = plt.subplots(figsize=(8, 4))
for blo in (1.5, 2.5, 3.5):
    f, spec = sdh_fft(R6[:, None], B6, b_range=(blo, 10), nfft=4096, bg_degree=5, log=False)
    ax.plot(f, spec[0] / spec[0].max(), label=f'B = {blo}–10 T')
ax.axvline(cst.h/(4*cst.e)*3.2e16, color='k', ls='--', label='F_L (geometry scale)')
ax.set(xlim=(0, 45), xlabel='F (T)', ylabel='FFT / peak', title='Run 6: window sensitivity')
ax.legend(); fig.tight_layout(); plt.show()
