"""sdh-spot-check read on run 6 (electron, n = +3.2e12, D = 0, B 0->10 T uniform-B):
raw Rxx(B), background-subtracted dRxx, sdh_onset tone track, FFT in 1/B vs F_L."""
from hera.analysis import sdh_onset, SdhOnsetError

rid, n_spot = 6, +3.2e12  # cm^-2
r6 = open_run(Path(file_path) / str(rid))
print(summarize_run(r6))
B6 = r6.col("magnet_field")
I6 = r6.col("sr0_X") / (-1e6)                 # measured drain current, A
R6 = np.abs(r6.col("sr1_X") / I6)             # sr1 gain 1 (device card)
o6 = np.argsort(B6); B6, R6, I6 = B6[o6], R6[o6], I6[o6]
FL6 = luttinger_frequency(abs(n_spot) * 1e4)  # cm^-2 -> m^-2
print(f"I_meas ~ {np.median(np.abs(I6))*1e9:.2f} nA; R(B<0.2 T) = {np.median(R6[B6 < 0.2]):.0f} Ohm, "
      f"R_max = {R6.max():.0f} Ohm ({R6.max()/(50e-6/np.median(np.abs(I6))):.0%} of the 50 uV FS); F_L = {FL6:.1f} T")

# raw FIRST
fig, ax = plt.subplots(3, 1, figsize=(10, 10))
ax[0].plot(B6, R6, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw: Rxx(B) at n = +3.2e12, D = 0 (sr1/sr0, gain-divided)")

# onset / tone track (r_full_scale flags soft clipping)
on6 = sdh_onset(R6, B6, r_full_scale=50e-6 / np.median(np.abs(I6)))
print(on6.summary())

# background-subtracted (deg-5 in B, B >= 1 T where the grid is 10 mT)
m = B6 >= 1.0
dR6 = R6[m] - np.polyval(np.polyfit(B6[m], R6[m], 5), B6[m])
ax[1].plot(B6[m], dR6, lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="MR background removed (deg 5 in B), 1-10 T")

# FFT in 1/B on the 10 mT record (cutoff at 1 T: the 50 mT sub-1 T grid under-samples a 7 T tone)
freqs6, spec6 = sdh_fft(R6[m][:, None], B6[m], b_range=(1.0, 10.0), nfft=4096)
ax[2].plot(freqs6, spec6[0], lw=0.8)
for f, c, lbl in ((FL6, "r", f"F_L = {FL6:.1f} T"), (25.78, "g", "ABAB heavy 25.8 T [model]"),
                  (7.31, "g", "ABAB light 7.3 T [model]")):
    ax[2].axvline(f, color=c, ls="--", lw=1, label=lbl)
ax[2].set(xlim=(0, 55), xlabel="F (T)", ylabel="|FFT| (dB-ish)", title="FFT in 1/B, window 1-10 T")
ax[2].legend(fontsize=8)
fig.tight_layout()
