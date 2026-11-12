ch7 = {c.cid: c for c in resolve_channels(r7.meta)}
B7 = r7.col("magnet_field")
I7 = r7.col("sr0_X") / ch7["sr0"].gain
R7 = (r7.col("sr1_X") / ch7["sr1"].gain) / I7
print("run 7: I_drain nA median/range", np.median(I7)*1e9, np.min(I7)*1e9, np.max(I7)*1e9)
print("Rxx signed Ohm p1/p50/p99", np.percentile(R7, [1, 50, 99]))
fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].plot(B7, R7, lw=0.8)
ax[0].set(xlabel="B (T)", ylabel="signed Rxx (Ohm)", title="run 7: hole spot")
for lo in (2.0, 3.0):
    f, spec = sdh_fft(R7[:, None], B7, b_range=(lo, 9.8), nfft=2048, bg_degree=5, log=False)
    peaks, _ = find_peaks(spec[0]); peaks = sorted((p for p in peaks if 3 < f[p] < 100), key=lambda p: -spec[0, p])[:5]
    print(f"FFT B={lo:.1f}–9.8 T top peaks (T):", [(round(float(f[p]), 2), round(float(spec[0,p]))) for p in peaks])
    ax[1].plot(f, spec[0], label=f"{lo:.1f}–9.8 T")
ax[1].set(xlim=(0, 70), xlabel="SdH frequency (T)", ylabel="FFT magnitude (a.u.)", title="window dependence")
ax[1].legend()
fig.tight_layout(); plt.show()
