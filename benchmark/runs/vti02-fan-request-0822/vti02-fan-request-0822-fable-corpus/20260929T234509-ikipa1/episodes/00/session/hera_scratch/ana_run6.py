# === Run 6 — sdh-spot-check, electron side: n = +3.2e12 cm^-2, D = 0, B 0 -> 10 T ===
from hera.analysis import sdh_onset, SdhOnsetError

r6 = run(6)
_o = np.argsort(r6.col("magnet_field"))
B6 = r6.col("magnet_field")[_o]
I6 = (r6.col("sr0_X") / r6.metadata["measurement_config"]["sr0_gain"])[_o]  # measured drain current
R6 = r6.col("sr1_X")[_o] / I6                                               # sr1 gain 1 (device card)

fig, ax = plt.subplots(1, 3, figsize=(15, 3.6))
ax[0].plot(B6, R6, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title="run 6 raw: n=+3.2e12, D=0 (10 mT grid above 1 T)")

m6 = B6 >= 1.0  # fine-grid leg; the 50 mT leg below 1 T undersamples the 7.1 T tone below ~0.85 T
dR6 = R6[m6] - np.polyval(np.polyfit(B6[m6], R6[m6], 5), B6[m6])
ax[1].plot(B6[m6], dR6, lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="bg-subtracted (deg-5 in B, B >= 1 T)")

on6 = sdh_onset(R6, B6, r_full_scale=50e-6 / np.median(np.abs(I6)))
print(on6.summary())

f6, s6 = sdh_fft(R6[m6][:, None], B6[m6], bg_degree=5, log=False)
ax[2].plot(f6, s6[0] / s6[0][f6 > 4].max(), lw=0.8)
for F, lab, c in [(7.31, "ABAB light (model, n=3.2)", "tab:green"),
                  (25.78, "ABAB heavy (model)", "tab:red"),
                  (33.1, "F_L (ABCA singleton)", "k")]:
    ax[2].axvline(F, ls=":", color=c, label=lab)
ax[2].set(xlim=(0, 45), ylim=(0, 1.5), xlabel="F (T)", ylabel="FFT (norm above 4 T)",
          title="1/B FFT, B >= 1 T")
ax[2].legend(fontsize=7)
fig.tight_layout()
print(f"T_sample {np.nanmin(r6.col('T_sample')):.3f}-{np.nanmax(r6.col('T_sample')):.3f} K; "
      f"leak max |I_tg| {np.max(np.abs(r6.col('k_2400_tg_curr')))*1e12:.0f} pA, "
      f"|I_bg| {np.max(np.abs(r6.col('k_2400_bg_curr')))*1e12:.0f} pA; "
      f"R range {R6.min():.0f}..{R6.max():.0f} Ohm at 50 uV FS ~ 5 kOhm")
