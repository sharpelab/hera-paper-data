# Runs 6 and 7: 2-10 T oscillation spectra; tones are exploratory, not a stacking call.
from scipy.signal import find_peaks
from hera.analysis import sdh_fft, sdh_onset, SdhOnsetError

fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for row, rid in enumerate((6, 7)):
    r = open_run(Path('data') / str(rid))
    ch = resolve_channels(r.meta); ci = current_channel(ch)
    cv = next(c for c in ch if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain
    R = (r.col(cv.col) / cv.gain) / I
    B = r.col('magnet_field'); order = np.argsort(B)
    B, R = B[order], R[order]
    f, spectrum = sdh_fft(R[:, None], B, b_range=(2.0, 10.0), log=False, nfft=2048, bg_degree=5)
    a = spectrum[0]
    peaks, _ = find_peaks(a)
    peaks = sorted((p for p in peaks if 3 < f[p] < 40), key=lambda p: a[p], reverse=True)[:5]
    print(f'run {rid} FFT peaks in 2-10 T window: ' + ', '.join(f'{f[p]:.1f} T' for p in peaks))
    try:
        onset = sdh_onset(R, B, b_lo=1.0, b_hi=10.0, r_full_scale=5000, f_min=3.0)
        print(onset.summary())
    except SdhOnsetError as exc:
        print(f'run {rid} onset unresolved: {exc}')
    ax[row].plot(f, a)
    ax[row].set_ylabel('FFT magnitude')
    ax[row].set_title(f'run {rid}: 2–10 T, B-polynomial detrended')
ax[-1].set_xlabel('SdH frequency (T)')
ax[-1].set_xlim(0, 40)
fig.tight_layout()
plt.show()
