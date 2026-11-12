from hera.analysis import resolve_channels

rid = SPOT_RUN
r = run(rid)
B = r.col('magnet_field')
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(B, r.col('sr1_X') * 1e6, '.', ms=2)
ax[0].set(ylabel='sr1 X (µV)', title=f'Run {rid}: raw lock-in output')
ax[1].plot(B, r.col('sr0_X') * 1e3, '.', ms=2)
ax[1].set(xlabel='B (T)', ylabel='sr0 X (mV)')
fig.tight_layout(); plt.show()
print(summarize_run(r))
print('raw gate currents: max |TG| = %.0f pA, max |BG| = %.0f pA' %
      (np.max(np.abs(r.col('k_2400_tg_curr'))) * 1e12,
       np.max(np.abs(r.col('k_2400_bg_curr'))) * 1e12))
