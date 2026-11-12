# Run 6 — sdh-spot-check, electron side: n = +3.2e12 cm^-2, D = 0, B 0 -> 10 T.
# Raw first, then onset + 1/B FFT vs F_L and the fs_count model.
from hera.analysis import sdh_onset, SdhOnsetError

run6 = run(6)
print(summarize_run(run6))
I_BIAS, SENS6 = 10e-9, 50e-6
B6 = run6.col("magnet_field"); R6 = run6.col("sr1_X") / I_BIAS
T6 = run6.col("T_sample")
FL6 = luttinger_frequency(3.2e16)   # (h/4e) n, n in m^-2 = 33.1 T
print(f"complete: {not run6.interrupted}; T {T6.min():.3f}-{T6.max():.3f} K; "
      f"R(0) = {R6[0]:.0f}, Rmax = {R6.max():.0f} Ohm ({R6.max()/(SENS6/I_BIAS)*100:.0f}% of 5 kOhm FS); F_L = {FL6:.1f} T")

on6 = sdh_onset(R6, B6, r_full_scale=SENS6 / I_BIAS)
print(on6.summary())

fig, ax = plt.subplots(3, 1, figsize=(9.5, 10))
ax[0].plot(B6, R6, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title="run 6 RAW: Rxx(B), n = +3.2e12, D = 0, T = 1.2 K")
m = B6 >= 0.9
p = np.polyfit(B6[m], R6[m], 5)
ax[1].plot(B6[m], R6[m] - np.polyval(p, B6[m]), lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="MR background removed (deg-5 in B, B > 0.9 T)")
for cut in (1.0, 1.5, 2.0):
    freqs, spec = sdh_fft(R6[:, None], B6, b_range=(cut, 10.0), bg_degree=5)
    ax[2].plot(freqs, spec[0] / spec[0].max(), lw=0.9, label=f"cutoff {cut:.1f} T")
ax[2].axvline(FL6, color="k", ls="--", lw=1, label=f"F_L = {FL6:.1f} T")
for f, lab in [(7.3, "ABAB light (model)"), (25.8, "ABAB heavy (model)")]:
    ax[2].axvline(f, color="tab:red", ls=":", lw=1)
    ax[2].text(f, 0.98, lab, rotation=90, fontsize=7, va="top", color="tab:red")
for k in (2, 3, 4):
    ax[2].axvline(k * 7.1, color="gray", ls=":", lw=0.7)
    ax[2].text(k * 7.1, 0.65, f"{k}x7.1", rotation=90, fontsize=6, va="top", color="gray")
ax[2].set(xlabel="F (T)", ylabel="norm. FFT amp", xlim=(0, 55),
          title="1/B FFT: tones vs F_L, model ABAB pair (red), harmonics of 7.1 T (gray)")
ax[2].legend(fontsize=8, loc="upper right")
fig.tight_layout()
dF6 = 1.0 / (1.0 / on6.onset_b - 1.0 / B6.max())
print(f"record resolution dF = {dF6:.2f} T (onset {on6.onset_b:.2f} T [censored: record low edge] -> 10 T)")
