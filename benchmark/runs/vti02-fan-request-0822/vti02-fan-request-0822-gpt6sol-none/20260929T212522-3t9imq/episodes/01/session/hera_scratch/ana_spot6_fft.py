from scipy.signal import find_peaks
f6, sp6 = sdh_fft(R6[:, None], B6, b_range=(1.5, 10), bg_degree=5, log=False)
p6, _ = find_peaks(sp6[0], prominence=.1*sp6[0].max())
p6 = sorted(p6, key=lambda i: sp6[0,i], reverse=True)[:6]
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(f6, sp6[0]); ax.axvline(float(luttinger_frequency(3.2e16)), color='r', ls='--', label='full-density F=33.1 T')
ax.set(xlim=(0, 50), xlabel='SdH frequency (T)', ylabel='FFT magnitude', title='data/6: 1.5–10 T, polynomial background removed')
ax.legend(); fig.tight_layout(); plt.show()
print('FFT peaks (T, relative amplitude):', [(round(float(f6[i]), 2), round(float(sp6[0,i]/sp6[0].max()), 2)) for i in p6])
