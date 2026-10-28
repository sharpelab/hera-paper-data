"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Onset via hera.analysis.sdh_onset, tones via sdh_fft; against F_L and the model table.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS_R = 100e6  # bias resistor
SENS = 50e-6

runs = {6: dict(n=3.2, FL=33.1, label="electron n=+3.2e12"),
        7: dict(n=-1.2, FL=12.4, label="hole n=-1.2e12")}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for i, (rid, info) in enumerate(runs.items()):
    r = open_run(f"{BASE}/{rid}")
    B = r.col("magnet_field")
    sr1x = r.col("sr1_X")
    sr0x = r.col("sr0_X")
    # measured drain current from sr0 (gain -1e6 V/A)
    g0 = r.metadata["measurement_config"]["sr0_gain"]
    I = sr0x / g0
    R = sr1x / I  # sr1 gain 1
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]
    # drive amplitude for full-scale estimate
    ib_nom = np.median(np.abs(I))
    r_fs = SENS / ib_nom
    print(f"\n=== run {rid} ({info['label']}) ===")
    print(f"pts {len(B)}, B {B.min():.3f}..{B.max():.3f} T, interrupted={r.interrupted}")
    print(f"I_drain median {ib_nom*1e9:.3f} nA, R(Bmin) {R[0]:.1f} Ohm, R range {R.min():.1f}..{R.max():.1f}; r_full_scale ~ {r_fs:.0f} Ohm")
    Tcol = r.col("T_sample")
    print(f"T_sample {np.nanmin(Tcol):.3f}-{np.nanmax(Tcol):.3f} K; leak max |I_tg| {np.max(np.abs(r.col('k_2400_tg_curr')))*1e12:.0f} pA, |I_bg| {np.max(np.abs(r.col('k_2400_bg_curr')))*1e12:.0f} pA")

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        onset = None

    axes[i, 0].plot(B, R, lw=0.6)
    axes[i, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw {info['label']}")
    # bg-subtracted view
    m = B > 1.0
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    axes[i, 1].plot(B[m], dR, lw=0.6)
    if onset:
        axes[i, 1].axvline(onset, color="r", ls="--", label=f"onset {onset:.2f} T")
        axes[i, 1].legend()
    axes[i, 1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="bg-subtracted (deg5, B>1)")
    # FFT above onset (and a stability alt)
    for cut, style in [(onset or 1.5, "-"), ((onset or 1.5) * 1.3, "--")]:
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
            axes[i, 2].plot(f, spec[0] / spec[0].max(), style, lw=0.8, label=f"cut {cut:.2f} T")
        except Exception as e:
            print(f"fft cut {cut:.2f}: {e}")
    axes[i, 2].axvline(info["FL"], color="k", ls=":", label=f"F_L {info['FL']} T")
    axes[i, 2].set(xlim=(0, 60), xlabel="F (T)", ylabel="FFT (norm)", title="1/B FFT")
    axes[i, 2].legend(fontsize=7)

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_fft.png", dpi=110)
print("\nsaved spot_fft.png")
