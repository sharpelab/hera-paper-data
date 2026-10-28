from hera.analysis import resolve_channels, sdh_onset

rid = 7
r = run(rid)
ch = {x.cid: x for x in resolve_channels(r.meta)}
B = r.col('magnet_field')
I = r.col('sr0_X') / ch['sr0'].gain
V = r.col('sr1_X') / ch['sr1'].gain
R = np.abs(V / I)
f, sp = sdh_fft(R[:, None], B, b_range=(2, 10), nfft=4096,
                bg_degree=5, log=False)
o = sdh_onset(R, B, b_hi=10, b_lo=1.0, r_full_scale=5000)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(B, R, '.', ms=2)
ax[0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'Run {rid}: measured-current Rxx')
ax[1].plot(f, sp[0])
ax[1].set(xlim=(0, 80), xlabel='1/B frequency (T)', ylabel='FFT magnitude (a.u.)',
          title='B=2–10 T, polynomial background removed')
fig.tight_layout(); plt.show()
print('R max %.1f Ω, max |V| / sensitivity %.3f, I median %.3f nA' %
      (R.max(), np.abs(V).max() / 50e-6, np.median(I) * 1e9))
print(o.summary())
