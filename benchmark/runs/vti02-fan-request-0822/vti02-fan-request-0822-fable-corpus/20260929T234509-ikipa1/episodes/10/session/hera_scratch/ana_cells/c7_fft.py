# Run 7 — onset + 1/B FFT, hole side n = -1.2e12 (F_L = 12.4 T).
FL7 = luttinger_frequency(1.2e16)
on7 = sdh_onset(R7, B7, r_full_scale=50e-6 / I7)
print(f"F_L(g=4) = {FL7:.1f} T")
print(on7.summary())

fig, ax = plt.subplots(figsize=(10, 3.6))
for cut in (0.75, 0.9, 1.1):
    freqs, spec = sdh_fft(R7[:, None], B7, b_range=(cut, B7.max()), bg_degree=5)
    ax.plot(freqs, spec[0] / spec[0].max(), lw=0.8, label=f"cut {cut:.2f} T")
ax.axvline(FL7, color="k", ls="--", label=f"F_L = {FL7:.1f} T")
ax.set(xlim=(0, 40), xlabel="F (T)", ylabel="FFT (norm)",
       title="run 7 FFT in 1/B (B >= cut): dominant ~7 T + ~2x/3x comb; low tone 2-3 T wanders with cut")
ax.legend(fontsize=7)
plt.show()
