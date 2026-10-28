r7 = run(7)
print(summarize_run(r7))
B7 = r7.col('magnet_field')
I7 = r7.col('sr0_X') / -1e6
R7 = r7.col('sr1_X') / I7
ix7 = np.argsort(B7); B7, R7 = B7[ix7], R7[ix7]
print(f"T = {np.nanmin(r7.col('T_sample')):.3f}..{np.nanmax(r7.col('T_sample')):.3f} K; R = {np.nanmin(R7):.1f}..{np.nanmax(R7):.1f} ohm; I = {np.nanmin(I7)*1e9:.2f}..{np.nanmax(I7)*1e9:.2f} nA")
plt.figure(figsize=(8, 3)); plt.plot(B7, R7, lw=.8); plt.xlabel('B (T)'); plt.ylabel('raw Rxx (ohm)'); plt.title('run 7 — hole raw'); plt.tight_layout(); plt.show()
on7 = sdh_onset(R7, B7, r_full_scale=5000)
print(on7.summary())
fig, ax = plt.subplots(figsize=(8, 3))
for lo in (1.0, 1.5, 2.0, 2.5):
    f, spec = sdh_fft(R7[:, None], B7, b_range=(lo, 10), log=False, nfft=4096)
    y = spec[0]
    peaks, _ = find_peaks(y, prominence=np.max(y)*.04)
    peaks = sorted((p for p in peaks if 2 < f[p] < 45), key=lambda p: y[p], reverse=True)[:5]
    print(f"B>{lo:.1f} T: " + ', '.join(f'{f[p]:.1f} T' for p in peaks))
    ax.plot(f, y/y.max(), label=f'B>{lo:.1f} T')
ax.set(xlim=(0, 45), xlabel='F (T)', ylabel='FFT / max', title='run 7 — cutoff stability'); ax.legend(); fig.tight_layout(); plt.show()
