# Run 7 — sdh-spot-check, hole side: n = -1.2e12 cm^-2, D = 0, B 10 -> 0.3 T (ride-down).
from hera.analysis import sdh_onset, SdhOnsetError

run7 = run(7)
print(summarize_run(run7))
I_BIAS, SENS7 = 10e-9, 50e-6
B7 = run7.col("magnet_field"); R7 = run7.col("sr1_X") / I_BIAS
i7 = np.argsort(B7); B7, R7 = B7[i7], R7[i7]       # swept downward; sort ascending
FL7 = luttinger_frequency(1.2e16)   # n in m^-2 -> 12.4 T
print(f"complete: {not run7.interrupted}; R(0.3 T) = {R7[0]:.0f}, Rmax = {R7.max():.0f} Ohm; F_L = {FL7:.1f} T")

on7 = sdh_onset(R7, B7, r_full_scale=SENS7 / I_BIAS)
print(on7.summary())

fig, ax = plt.subplots(3, 1, figsize=(9.5, 10))
ax[0].plot(B7, R7, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title="run 7 RAW: Rxx(B), n = -1.2e12, D = 0, T = 1.2 K")
m = B7 >= on7.onset_b * 0.8
p = np.polyfit(B7[m], R7[m], 5)
ax[1].plot(B7[m], R7[m] - np.polyval(p, B7[m]), lw=0.6)
ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title=f"MR background removed (deg-5 in B, B > {on7.onset_b*0.8:.2f} T)")
for cut in (0.71, 1.0, 1.5):
    freqs, spec = sdh_fft(R7[:, None], B7, b_range=(cut, 10.0), bg_degree=5)
    ax[2].plot(freqs, spec[0] / spec[0].max(), lw=0.9, label=f"cutoff {cut:.2f} T")
ax[2].axvline(FL7, color="k", ls="--", lw=1, label=f"F_L = {FL7:.1f} T")
for f, lab in [(1.2, "ABAB light (model)"), (11.3, "ABAB heavy (model, e-side val.)")]:
    ax[2].axvline(f, color="tab:red", ls=":", lw=1)
    ax[2].text(f, 0.98, lab, rotation=90, fontsize=7, va="top", color="tab:red")
ax[2].set(xlabel="F (T)", ylabel="norm. FFT amp", xlim=(0, 30),
          title="1/B FFT: near-CNP hole regime (recipe's stated low-|n| exception — tones close/beat-like)")
ax[2].legend(fontsize=8, loc="upper right")
fig.tight_layout()
dF7 = 1.0 / (1.0 / on7.onset_b - 1.0 / B7.max())
print(f"record resolution dF = {dF7:.2f} T (onset {on7.onset_b:.2f} T -> 10 T)")
