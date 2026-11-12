"""sdh-spot-check read on run 7 (hole, n = -1.2e12, D = 0, B 10->0.3 T ride-down, 20 mT):
raw Rxx(B), onset track, FFT vs F_L = 12.4 T."""
from hera.analysis import sdh_onset, SdhOnsetError

rid, n_spot = 7, -1.2e12
r7 = open_run(Path(file_path) / str(rid))
print(summarize_run(r7))
B7 = r7.col("magnet_field")
I7 = r7.col("sr0_X") / (-1e6)
R7 = np.abs(r7.col("sr1_X") / I7)
o7 = np.argsort(B7); B7, R7, I7 = B7[o7], R7[o7], I7[o7]
FL7 = luttinger_frequency(abs(n_spot) * 1e4)
print(f"I_meas ~ {np.median(np.abs(I7))*1e9:.2f} nA; R(B<0.5 T) = {np.median(R7[B7 < 0.5]):.0f} Ohm, "
      f"R_max = {R7.max():.0f} Ohm; F_L = {FL7:.1f} T")

fig, ax = plt.subplots(3, 1, figsize=(10, 10))
ax[0].plot(B7, R7, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw: Rxx(B) at n = -1.2e12, D = 0")

on7 = sdh_onset(R7, B7, r_full_scale=50e-6 / np.median(np.abs(I7)))
print(on7.summary())

m = B7 >= 0.71  # measured onset
dR7 = R7[m] - np.polyval(np.polyfit(B7[m], R7[m], 5), B7[m])
ax[1].plot(B7[m], dR7, lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="MR background removed (deg 5 in B), onset-10 T")

freqs7, spec7 = sdh_fft(R7[m][:, None], B7[m], b_range=(0.71, 10.0), nfft=4096)
ax[2].plot(freqs7, spec7[0], lw=0.8)
ax[2].axvline(FL7, color="r", ls="--", lw=1, label=f"F_L = {FL7:.1f} T")
ax[2].set(xlim=(0, 30), xlabel="F (T)", ylabel="|FFT|", title="FFT in 1/B, window 0.71-10 T")
ax[2].legend(fontsize=8)
fig.tight_layout()
