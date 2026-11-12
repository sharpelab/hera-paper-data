fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
for j, rid in enumerate((6, 7)):
    r = run(rid); B = r.col('magnet_field')
    I = r.col('sr0_X') / r.meta['measurement_config']['sr0_gain']
    R = np.abs(r.col('sr1_X') / I)
    ix = np.argsort(B); B, R = B[ix], R[ix]
    m = (B >= 2.5) & (B <= 9.5)
    f, a = sdh_fft(R[m, None], B[m], b_range=(2.5, 9.5), nfft=1024, bg_degree=5)
    ax[j].plot(f, a[0]); ax[j].set(xlim=(0, 45), xlabel='F (T)', ylabel='FFT magnitude', title=f'data/{rid}: 2.5–9.5 T')
    o = sdh_onset(R, B, b_lo=1.0, b_hi=9.5, r_full_scale=5000)
    print(f'data/{rid}: ' + o.summary())
fig.tight_layout(); plt.show()
