# === Run 7 — sdh-spot-check, hole side: n = -1.2e12 cm^-2, D = 0, B 10 -> 0.3 T ===
from hera.analysis import sdh_onset, SdhOnsetError

r7 = run(7)
_o = np.argsort(r7.col("magnet_field"))
B7 = r7.col("magnet_field")[_o]
I7 = (r7.col("sr0_X") / r7.metadata["measurement_config"]["sr0_gain"])[_o]
R7 = r7.col("sr1_X")[_o] / I7

fig, ax = plt.subplots(1, 3, figsize=(15, 3.6))
ax[0].plot(B7, R7, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title="run 7 raw: n=-1.2e12, D=0 (20 mT grid)")

m7 = B7 >= 1.0
dR7 = R7[m7] - np.polyval(np.polyfit(B7[m7], R7[m7], 5), B7[m7])
ax[1].plot(B7[m7], dR7, lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="bg-subtracted (deg-5 in B, B >= 1 T)")

on7 = sdh_onset(R7, B7, r_full_scale=50e-6 / np.median(np.abs(I7)))
print(on7.summary())

f7, s7 = sdh_fft(R7[m7][:, None], B7[m7], bg_degree=5, log=False)
ax[2].plot(f7, s7[0] / s7[0][f7 > 3].max(), lw=0.8)
for F, lab, c in [(5.86, "ABAB pair (model, n=-1.2)", "tab:green"),
                  (6.54, None, "tab:green"),
                  (12.41, "F_L (ABCA singleton / breakdown sum)", "k")]:
    ax[2].axvline(F, ls=":", color=c, label=lab)
ax[2].set(xlim=(0, 30), ylim=(0, 1.5), xlabel="F (T)", ylabel="FFT (norm above 3 T)",
          title="1/B FFT, B >= 1 T")
ax[2].legend(fontsize=7)
fig.tight_layout()
print(f"T_sample {np.nanmin(r7.col('T_sample')):.3f}-{np.nanmax(r7.col('T_sample')):.3f} K; "
      f"leak max |I_tg| {np.max(np.abs(r7.col('k_2400_tg_curr')))*1e12:.0f} pA, "
      f"|I_bg| {np.max(np.abs(r7.col('k_2400_bg_curr')))*1e12:.0f} pA; "
      f"R range {R7.min():.0f}..{R7.max():.0f} Ohm at 50 uV FS ~ 5 kOhm")
