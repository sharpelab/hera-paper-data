"""Runs 6 & 7 — sdh-spot-check read: onset + tone set vs F_L and the model."""
from hera.analysis import sdh_onset, SdhOnsetError

SENS, GAIN_CUR = 50e-6, -1e6

# Model predictions at the two spots (hera/models/tetralayer_fs_count/fs_count_b0.py,
# abab_fs/abca_fs/abab_mstar/abca_mstar at the run-5-calibrated densities):
MODEL = {
    6: dict(n=+3.2e12, abab=(7.31, 25.78), abab_m=(0.027, 0.061), abca=33.08, abca_m=0.074),
    7: dict(n=-1.2e12, abab=(5.86, 6.54), abab_m=(0.032, 0.074), abca=12.41, abca_m=1.122),
}

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
onsets = {}
for col, rid in enumerate((6, 7)):
    r, mdl = run(rid), MODEL[rid]
    B = r.col("magnet_field")
    I = r.col("sr0_X") / GAIN_CUR
    R = r.col("sr1_X") / I
    idx = np.argsort(B)
    B, R = B[idx], R[idx]
    FL = luttinger_frequency(mdl["n"] * 1e4)

    ax = axes[0, col]                                   # raw first
    ax.plot(B, R, lw=0.5)
    ax.set(title=f"run {rid}: n={mdl['n']/1e12:+.1f}e12, D=0 — raw Rxx(B)",
           xlabel="B (T)", ylabel="Rxx (Ω)")

    on = sdh_onset(R, B, r_full_scale=SENS / np.median(np.abs(I)))
    print(f"=== run {rid} (n = {mdl['n']/1e12:+.1f}e12, F_L = {FL:.1f} T) ===")
    print(on.summary())
    onsets[rid] = on

    bmask = B >= 0.3
    p = np.polyfit(B[bmask], R[bmask], 5)
    ax = axes[1, col]
    ax.plot(B[bmask], R[bmask] - np.polyval(p, B[bmask]), lw=0.5)
    ax.axvline(on.onset_b, color="r", ls="--", label=f"onset {on.onset_b:.2f} T")
    ax.legend()
    ax.set(title=f"run {rid}: ΔRxx (deg-5 bg in B)", xlabel="B (T)", ylabel="ΔRxx (Ω)")

    ax = axes[2, col]
    for cut, style in [(max(on.onset_b, 0.5), "-"), (1.6, "--")]:
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5)
        ax.plot(freqs, spec[0] / spec[0].max(), style, lw=1, label=f"cutoff {cut:.2f} T")
    ax.axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    for f, c, lab in [(mdl["abab"][0], "tab:green", "ABAB light"),
                      (mdl["abab"][1], "tab:orange", "ABAB heavy"),
                      (mdl["abca"], "tab:red", "ABCA")]:
        ax.axvline(f, color=c, ls=":", alpha=0.8, label=f"{lab} {f:.1f} T")
    ax.set(xlim=(0, 1.4 * FL), title=f"run {rid}: FFT in 1/B (norm.)", xlabel="F (T)")
    ax.legend(fontsize=7)

fig.tight_layout()
plt.show()
