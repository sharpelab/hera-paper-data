"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Onset via hera.analysis.sdh_onset, FFT via sdh_fft, tones vs F_L.
"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

RUNS = {
    6: dict(n=+3.2e12, label="electron n=+3.2e12"),
    7: dict(n=-1.2e12, label="hole n=-1.2e12"),
}

fig, axes = plt.subplots(3, 2, figsize=(13, 11))

for col, (rid, info) in enumerate(RUNS.items()):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field")
    # sr1 = Rxx (unity gain); I = measured drain current sr0_X / sr0_gain
    I = run.col("sr0_X") / (-1e6)
    R = run.col("sr1_X") / I
    sens = 50e-6  # sr1 sensitivity, from run comment
    i_bias = float(np.median(np.abs(I)))
    print(f"\n=== run {rid} ({info['label']}) ===")
    print(f"npts {len(B)}, B {B.min():.3f}..{B.max():.3f} T, sens {sens}, I_med {i_bias:.3e} A")
    print(f"R(B~0): {np.median(R[np.abs(B) < 0.4]):.1f} Ω; R range {R.min():.1f}..{R.max():.1f} Ω")
    FL = luttinger_frequency(info["n"] * 1e4)  # cm^-2 -> m^-2
    print(f"F_L = {FL:.2f} T")

    # sort ascending in B (run 7 was descending)
    idx = np.argsort(B)
    B, R = B[idx], R[idx]

    ax = axes[0, col]
    ax.plot(B, R, lw=0.5)
    ax.set_title(f"run {rid}: {info['label']} — raw R(B)")
    ax.set_xlabel("B (T)")
    ax.set_ylabel("Rxx (Ω)")

    try:
        on = sdh_onset(R, B, r_full_scale=sens / i_bias)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    if onset is not None:
        # background-subtracted trace
        bmask = B >= max(0.3, 0.8 * onset)
        p = np.polyfit(B[bmask], R[bmask], 5)
        dR = R[bmask] - np.polyval(p, B[bmask])
        ax = axes[1, col]
        ax.plot(B[bmask], dR, lw=0.5)
        ax.axvline(onset, color="r", ls="--", label=f"onset {onset:.2f} T")
        ax.legend()
        ax.set_title(f"run {rid}: ΔRxx (deg-5 bg removed)")
        ax.set_xlabel("B (T)")
        ax.set_ylabel("ΔRxx (Ω)")

        # FFT above onset (and a bit above, per recipe)
        for cut, style in [(onset, "-"), (1.25 * onset, "--")]:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5)
            axes[2, col].plot(freqs, spec[0] / spec[0].max(), style, lw=1,
                              label=f"cutoff {cut:.2f} T")
        axes[2, col].axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
        for frac, c in [(0.72, "tab:orange"), (0.28, "tab:green")]:
            axes[2, col].axvline(frac * FL, color=c, ls=":", alpha=0.7,
                                 label=f"{frac:.2f}·F_L")
        axes[2, col].set_xlim(0, 1.6 * FL)
        axes[2, col].legend(fontsize=7)
        axes[2, col].set_title(f"run {rid}: FFT in 1/B (normalized)")
        axes[2, col].set_xlabel("F (T)")

fig.tight_layout()
fig.savefig("hera_scratch/spot_fft.png", dpi=110)
print("\nsaved hera_scratch/spot_fft.png")
