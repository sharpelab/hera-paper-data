"""Spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset via sdh_onset, tones via sdh_fft, vs F_L and the model templates."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

for rid, n_cm2, tag in [(6, +3.2e12, "electron"), (7, -1.2e12, "hole")]:
    run = open_run(f"{BASE}/{rid}")
    B = run.col("magnet_field")
    X = run.col("sr1_X")  # sr1, unity gain
    Ib = run.meta["measurement_config"]["I_bias"] if "I_bias" in str(run.meta.get("measurement_config", {})) else 10e-9
    R = X / 10e-9  # sr1 gain 1, I_bias 10 nA
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = luttinger_frequency(abs(n_cm2) * 1e4)  # n in m^-2
    print(f"\n===== run {rid} ({tag}, n={n_cm2:+.1e} cm^-2)  F_L = {FL:.1f} T =====")
    print(f"B range {B.min():.2f}..{B.max():.2f} T, {len(B)} pts, R range {R.min():.1f}..{R.max():.1f} Ohm")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    fig, axes = plt.subplots(2, 1, figsize=(11, 7))
    axes[0].plot(B, R, lw=0.6)
    axes[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw ({tag})")
    if onset:
        for co in [onset, onset * 1.2, onset * 1.5]:
            if co < B.max() * 0.8:
                f, s = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=5)
                axes[1].plot(f, s[0] / s[0].max(), lw=0.8, label=f"cutoff {co:.2f} T")
        axes[1].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f} T")
        axes[1].axvline(0.72 * FL, color="r", ls=":", label="0.72 F_L")
        axes[1].axvline(0.28 * FL, color="b", ls=":", label="0.28 F_L")
        axes[1].set(xlim=(0, 1.6 * FL), xlabel="F (T)", ylabel="norm FFT", title="1/B FFT")
        axes[1].legend(fontsize=7)
        # peak list at the mid cutoff
        f, s = sdh_fft(R[:, None], B, b_range=(onset * 1.2, B.max()), bg_degree=5)
        sp = s[0]
        pk = [i for i in range(2, len(f) - 2) if sp[i] == max(sp[max(0,i-3):i+4]) and sp[i] > 0.05 * sp.max() and f[i] > 1]
        print("peaks (F [T], rel amp):", [(round(float(f[i]), 2), round(float(sp[i] / sp.max()), 3)) for i in pk])
    fig.tight_layout()
    fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png", dpi=110)
    plt.close(fig)
print("\nsaved spot_run6.png / spot_run7.png")
