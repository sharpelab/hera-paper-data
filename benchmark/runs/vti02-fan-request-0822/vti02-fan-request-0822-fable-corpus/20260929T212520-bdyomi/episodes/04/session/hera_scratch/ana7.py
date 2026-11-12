"""sdh-spot-check run 7 (hole, n = -1.2e12, D = 0, B 10 -> 0.3 T ride-down): raw trace, onset, 1/B FFT."""
from hera.analysis import sdh_onset, SdhOnsetError

rid, n12 = 7, -1.2
r = run(rid)
o = np.argsort(r.col("magnet_field"))
B, R = r.col("magnet_field")[o], (r.col("sr1_X") / 1 / 10e-9)[o]
FL = luttinger_frequency(abs(n12) * 1e16)
MODEL = {"ABAB pair": (5.3, 7.1), "ABCA (LK-dead at T_e~8K)": (12.4,)}   # fs_count_b0 F [T] at -1.2e12

on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
print(on.summary())

fig, ax = plt.subplots(2, 1, figsize=(11, 7))
ax[0].plot(B, R, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ω)", title=f"run {rid} raw — hole spot, n = {n12:+.1f}e12, D = 0")
for co in (0.71, 0.86, 1.07):
    f, s = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=5)
    ax[1].plot(f, s[0] / s[0].max(), lw=0.8, label=f"cutoff {co:.2f} T")
ax[1].axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T")
for Fm in MODEL["ABAB pair"]:
    ax[1].axvline(Fm, color="b", ls=":", label=f"ABAB {Fm} T")
ax[1].set(xlim=(0, 2.0 * FL), xlabel="F (T)", ylabel="norm FFT", title="per-cutoff 1/B FFT vs model")
ax[1].legend(fontsize=7)
fig.tight_layout()
print(f"F_L = {FL:.1f} T; near-CNP exception regime — tones close/balanced, record beat-like; no partition read")
