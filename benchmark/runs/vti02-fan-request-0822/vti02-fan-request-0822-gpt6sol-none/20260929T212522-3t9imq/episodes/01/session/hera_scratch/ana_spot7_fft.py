f7, sp7 = sdh_fft(R7[:, None], B7, b_range=(1.5, 10), bg_degree=5, log=False)
p7, _ = find_peaks(sp7[0], prominence=.1*sp7[0].max())
p7 = sorted(p7, key=lambda i: sp7[0,i], reverse=True)[:6]
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(f7, sp7[0]); ax.axvline(float(luttinger_frequency(1.2e16)), color='r', ls='--', label='full-density F=12.4 T')
ax.set(xlim=(0, 40), xlabel='SdH frequency (T)', ylabel='FFT magnitude', title='data/7: 1.5–10 T, polynomial background removed')
ax.legend(); fig.tight_layout(); plt.show()
print('FFT peaks (T, relative amplitude):', [(round(float(f7[i]), 2), round(float(sp7[0,i]/sp7[0].max()), 2)) for i in p7])
