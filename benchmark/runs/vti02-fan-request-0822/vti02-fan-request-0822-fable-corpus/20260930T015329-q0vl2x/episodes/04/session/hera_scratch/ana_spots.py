"""SdH spot checks, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).

Read: onset + tone set vs F_L per side; decides the fan's side, B_lo,
Delta(1/B), and sensitivity (investigation Step 3 -> Step 4 handoff).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

SR1_GAIN = 1.0
BIAS_R = 100e6
SENS = 50e-6            # V, both runs
runs = {
    6: dict(label="electron n=+3.2e12", F_L=33.1, n=3.2e12),
    7: dict(label="hole n=-1.2e12", F_L=12.4, n=1.2e12),
}

fig, axes = plt.subplots(2, 3, figsize=(15, 7))
for row, (rid, info) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    # I_bias from drive: sr1 is bias channel; amplitude in metadata config?
    amp = None
    for k, v in r.meta.get("instruments", {}).get("sr1", {}).items():
        if "amplitude" in k:
            amp = v
    if amp is None:
        amp = 1.0  # fall back; report
    I = amp / BIAS_R
    R = (r.col("sr1_X") / SR1_GAIN) / I
    fs = SENS / I
    order = np.argsort(B)
    B, R = B[order], R[order]
    print(f"=== run {rid} — {info['label']}; I_bias {I*1e9:.2f} nA, FS {fs:.0f} Ohm")
    print(f"R(Bmin)={R[0]:.1f} Ohm, R(Bmax)={R[-1]:.1f} Ohm, max {R.max():.1f}")
    try:
        on = sdh_onset(R, B, r_full_scale=fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.5)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {info['label']}")

    # background-subtracted trace
    msk = B > 0.5
    p = np.polyfit(B[msk], R[msk], 5)
    dR = R[msk] - np.polyval(p, B[msk])
    ax = axes[row, 1]
    ax.plot(B[msk], dR, lw=0.5)
    if onset:
        ax.axvline(onset, color="r", ls="--", label=f"onset {onset:.2f} T")
        ax.legend()
    ax.set_xlabel("B (T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title("bg-subtracted (deg-5)")

    # FFT above onset (and a stability variant)
    ax = axes[row, 2]
    if onset:
        for cut, deg, style in [(onset, 5, "-"), (onset * 1.3, 5, "--"), (onset, 7, ":")]:
            f, s = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=deg, log=False)
            ax.plot(f, s[0] / s[0].max(), style, lw=1,
                    label=f"cut {cut:.2f} deg {deg}")
        ax.axvline(info["F_L"], color="k", ls="-", alpha=0.4, label=f"F_L {info['F_L']} T")
        ax.set_xlim(0, info["F_L"] * 1.6)
        ax.legend(fontsize=7)
    ax.set_xlabel("F (T)"); ax.set_ylabel("norm. amp")
    ax.set_title("1/B FFT")

fig.tight_layout()
fig.savefig("hera_scratch/spots_67.png", dpi=110)
print("saved hera_scratch/spots_67.png")
