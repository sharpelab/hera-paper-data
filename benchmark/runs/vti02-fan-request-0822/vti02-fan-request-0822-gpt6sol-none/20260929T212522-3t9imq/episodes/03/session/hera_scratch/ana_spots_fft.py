from scipy.signal import find_peaks
fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
for row, rid in enumerate((6, 7)):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / (r.col('sr0_X') / ch['sr0'].gain))
    for lo in (1.5, 2.0, 3.0):
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, 10.0), nfft=2048, bg_degree=3, log=False)
        y = spec[0]; ax[row].plot(f, y / np.max(y), label=f'{lo:g}–10 T')
        if lo == 2.0:
            peaks, _ = find_peaks(y)
            peaks = sorted((k for k in peaks if 3 < f[k] < 40), key=lambda k: y[k], reverse=True)[:4]
            print(f'data/{rid} FFT 2–10 T local maxima:', [(round(float(f[k]), 1), round(float(y[k]/np.max(y)), 2)) for k in peaks])
    ax[row].set(xlim=(0, 45), ylabel='normalized FFT', title=f'data/{rid}: detrended Rxx, 1/B FFT')
    ax[row].legend(); ax[row].grid(alpha=.2)
ax[-1].set_xlabel('frequency (T)'); fig.tight_layout(); plt.show()
