"""sdh-spot-check run 6 (electron, n = +3.2e12, D = 0, B 0 -> 10 T): raw trace, onset, 1/B FFT vs model."""
from hera.analysis import sdh_onset, SdhOnsetError

rid, n12 = 6, +3.2                       # run id, density in 1e12 cm^-2 (run-5 cal)
r = run(rid)
o = np.argsort(r.col("magnet_field"))
B, R = r.col("magnet_field")[o], (r.col("sr1_X") / 1 / 10e-9)[o]   # sr1 gain 1, I_bias 10 nA
FL = luttinger_frequency(abs(n12) * 1e16)                          # g = 4, n in m^-2
MODEL = {"ABAB light": 7.31, "ABAB heavy": 25.78, "ABCA": 33.08}   # fs_count_b0 F [T] at +3.2e12

on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
print(on.summary())

fig, ax = plt.subplots(2, 1, figsize=(11, 7))
ax[0].plot(B, R, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel="Rxx (Ω)", title=f"run {rid} raw — electron spot, n = {n12:+.1f}e12, D = 0")
# FFT stability set: cutoff above the (censored) onset edge, bg poly deg 5 in B
for co in (0.36, 0.5, 1.0):
    f, s = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=5)
    ax[1].plot(f, s[0] / s[0].max(), lw=0.8, label=f"cutoff {co:.2f} T")
ax[1].axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T")
for lbl, Fm in MODEL.items():
    ax[1].axvline(Fm, color={"ABAB light": "b", "ABAB heavy": "r", "ABCA": "g"}[lbl], ls=":", label=f"{lbl} {Fm} T")
ax[1].set(xlim=(0, 1.5 * FL), xlabel="F (T)", ylabel="norm FFT", title="per-cutoff 1/B FFT vs model")
ax[1].legend(fontsize=7)
fig.tight_layout()

f, s = sdh_fft(R[:, None], B, b_range=(0.5, B.max()), bg_degree=5)
sp = s[0]
pk = [i for i in range(2, len(f) - 2) if sp[i] == sp[max(0, i - 3):i + 4].max() and sp[i] > 0.05 * sp.max() and f[i] > 1]
print("peaks at cutoff 0.5 T (F [T], rel amp):",
      [(round(float(f[i]), 2), round(float(sp[i] / sp.max()), 3)) for i in pk])
print(f"F_L = {FL:.1f} T; sum candidates: 7.1+29.5 = {7.1+29.5:.1f} (1.11 F_L), 7.1+25.8(model heavy) = {7.1+25.8:.1f} (0.99 F_L)")
