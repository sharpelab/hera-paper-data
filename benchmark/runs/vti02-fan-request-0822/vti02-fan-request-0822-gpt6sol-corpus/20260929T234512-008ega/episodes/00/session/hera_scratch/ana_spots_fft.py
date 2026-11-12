from hera.analysis import sdh_onset
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
for k, rid in enumerate((6, 7)):
    q = run(rid)
    B = q.col('magnet_field'); R = q.col('sr1_X') / (q.col('sr0_X') / -1e6)
    order = np.argsort(B); B, R = B[order], R[order]
    on = sdh_onset(R, B, b_lo=1.0 if rid == 6 else 0.3, r_full_scale=5000)
    print(f'run {rid}: {on.summary()}')
    for lo, style in ((1.0, '-'), (1.5, '--')):
        F, S = sdh_fft(R[:, None], B, b_range=(lo, 8.0), nfft=4096, bg_degree=5, log=False)
        y = S[0] / max(S[0])
        ax[k].plot(F, y, style, label=f'{lo}–8 T')
    ax[k].set_xlim(0, 42); ax[k].set_ylabel('FFT amplitude / max')
    ax[k].set_title(f'run {rid}: B detrended, resampled in 1/B')
    ax[k].legend()
ax[-1].set_xlabel('frequency F (T)')
fig.tight_layout(); plt.show()
