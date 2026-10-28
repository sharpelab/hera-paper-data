from hera.analysis import sdh_onset
from scipy.signal import find_peaks
ix = np.argsort(B6); b, r = B6[ix], R6[ix]
on6 = sdh_onset(r, b, b_lo=0.3, r_full_scale=5000)
print(on6.summary())
fig, ax = plt.subplots(figsize=(10, 4))
for cut in (0.7, 1.0, 1.5, 2.0):
    f, sp = sdh_fft(r[:, None], b, b_range=(cut, 10.0), nfft=4096, log=False)
    y = sp[0]; y /= np.max(y)
    ax.plot(f, y, label=f'B={cut}–10 T')
    pk, _ = find_peaks(y, prominence=0.10)
    print('cut', cut, 'peaks >10% prominence', [(round(float(f[j]),1), round(float(y[j]),2)) for j in pk if 3 < f[j] < 40])
ax.axvline(33.1, color='k', ls=':', label='F_L=33.1 T (geometry scale)')
ax.set(xlim=(0, 42), xlabel='F (T)', ylabel='normalized FFT amplitude', title='Run 6: 1/B FFT vs low-B cutoff')
ax.legend(ncol=2); fig.tight_layout(); plt.show()
