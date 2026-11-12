from hera.analysis import sdh_onset
from scipy.signal import find_peaks
r6 = run(6)
print(summarize_run(r6))
B6 = r6.col('magnet_field')
I6 = r6.col('sr0_X') / -1e6
R6 = r6.col('sr1_X') / I6
print(f"T = {np.nanmin(r6.col('T_sample')):.3f}..{np.nanmax(r6.col('T_sample')):.3f} K; R = {np.nanmin(R6):.1f}..{np.nanmax(R6):.1f} ohm; I = {np.nanmin(I6)*1e9:.2f}..{np.nanmax(I6)*1e9:.2f} nA")
plt.figure(figsize=(8, 3)); plt.plot(B6, R6, lw=.8); plt.xlabel('B (T)'); plt.ylabel('raw Rxx (ohm)'); plt.title('run 6 — electron raw'); plt.tight_layout(); plt.show()
on6 = sdh_onset(R6, B6, r_full_scale=5000)
print(on6.summary())
fig, ax = plt.subplots(figsize=(8, 3))
for lo in (1.0, 1.5, 2.0, 2.5):
    f, spec = sdh_fft(R6[:, None], B6, b_range=(lo, 10), log=False, nfft=4096)
    y = spec[0]
    peaks, _ = find_peaks(y, prominence=np.max(y)*.04)
    peaks = sorted((p for p in peaks if 2 < f[p] < 45), key=lambda p: y[p], reverse=True)[:5]
    print(f"B>{lo:.1f} T: " + ', '.join(f'{f[p]:.1f} T' for p in peaks))
    ax.plot(f, y/y.max(), label=f'B>{lo:.1f} T')
ax.set(xlim=(0, 45), xlabel='F (T)', ylabel='FFT / max', title='run 6 — cutoff stability'); ax.legend(); fig.tight_layout(); plt.show()
