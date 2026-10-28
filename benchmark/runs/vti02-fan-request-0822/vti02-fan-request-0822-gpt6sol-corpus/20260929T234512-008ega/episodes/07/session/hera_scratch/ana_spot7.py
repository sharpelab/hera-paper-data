from hera.analysis import sdh_onset

r7 = run(7)
print(summarize_run(r7))
B7 = r7.col('magnet_field')
I7 = r7.col('sr0_X') / r7.meta['measurement_config']['sr0_gain']
R7 = np.abs(r7.col('sr1_X') / I7)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(B7, R7, lw=1); ax[0].set(xlabel='B (T)', ylabel='|Rxx| (Ohm)', title='Run 7: raw measured-current Rxx')
ax[1].plot(B7, I7 * 1e9, lw=1); ax[1].set(xlabel='B (T)', ylabel='drain current (nA)', title='Run 7: raw drain current')
fig.tight_layout(); plt.show()
print('raw: Rmax = %.0f Ohm, |I_tg|max = %.0f pA, |I_bg|max = %.0f pA, T = %.3f–%.3f K' %
      (R7.max(), np.max(np.abs(r7.col('k_2400_tg_curr'))) * 1e12,
       np.max(np.abs(r7.col('k_2400_bg_curr'))) * 1e12,
       r7.col('T_sample').min(), r7.col('T_sample').max()))

o7 = sdh_onset(R7, B7, b_lo=0.3, r_full_scale=5000)
print(o7.summary())
fig, ax = plt.subplots(figsize=(8, 4))
for blo in (1.5, 2.5, 3.5):
    f, spec = sdh_fft(R7[:, None], B7, b_range=(blo, 10), nfft=4096, bg_degree=5, log=False)
    ax.plot(f, spec[0] / spec[0].max(), label=f'B = {blo}–10 T')
ax.axvline(cst.h/(4*cst.e)*1.2e16, color='k', ls='--', label='F_L (geometry scale)')
ax.set(xlim=(0, 40), xlabel='F (T)', ylabel='FFT / peak', title='Run 7: window sensitivity')
ax.legend(); fig.tight_layout(); plt.show()
