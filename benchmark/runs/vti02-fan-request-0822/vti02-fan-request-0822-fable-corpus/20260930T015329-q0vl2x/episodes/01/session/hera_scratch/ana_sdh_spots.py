# SdH spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0
# Onset via hera.analysis.sdh_onset, FFT via hera.analysis.sdh_fft, tones vs F_L.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

DIR = "/home/hera/measurements/zack/20260822-vti-02"
I_BIAS = 10e-9
SENS = 50e-6
RFS = SENS / I_BIAS  # 5 kOhm full scale

H_OVER_4E = 6.62607015e-34 / (4 * 1.602176634e-19)  # T m^2

runs = {
    6: dict(n=3.2e16, label="electron n=+3.2e12"),
    7: dict(n=-1.2e16, label="hole n=-1.2e12"),
}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for i, (fid, info) in enumerate(runs.items()):
    r = open_run(f"{DIR}/data/{fid}")
    B = r.col("magnet_field")
    R = r.col("sr1_X") / I_BIAS  # gain 1
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = H_OVER_4E * abs(info["n"])
    print(f"\n===== run {fid}: {info['label']}, F_L = {FL:.1f} T =====")
    print(f"B {B.min():.2f}..{B.max():.2f} T, {len(B)} pts; R range {R.min():.1f}..{R.max():.1f} Ohm (FS {RFS:.0f})")

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=RFS)
        print(on.summary())
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        on, onset_b = None, None

    # raw
    ax = axes[i, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {fid} raw — {info['label']}")
    if onset_b:
        ax.axvline(onset_b, color="r", ls="--", lw=0.8)

    # background-subtracted (poly in B over the FFT window)
    if onset_b:
        for cut, c in [(onset_b, "C0"), (max(onset_b * 1.3, onset_b + 0.5), "C1")]:
            m = (B >= cut)
            if m.sum() < 20:
                continue
            freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(cut, B.max()), bg_degree=5)
            sp = spec[0]
            ax2 = axes[i, 2]
            ax2.plot(freqs, sp / sp.max(), c, lw=0.9, label=f"cut {cut:.2f} T")
        ax2.axvline(FL, color="k", ls=":", lw=1, label=f"F_L {FL:.1f} T")
        ax2.set_xlim(0, 1.6 * FL)
        ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT (norm)")
        ax2.set_title(f"run {fid} FFT in 1/B")
        ax2.legend(fontsize=7)

        # delta-R view
        m = B >= onset_b
        p = np.polyfit(B[m], R[m], 5)
        dR = R[m] - np.polyval(p, B[m])
        axm = axes[i, 1]
        axm.plot(B[m], dR, lw=0.6)
        axm.set_xlabel("B (T)"); axm.set_ylabel("dRxx (Ohm)")
        axm.set_title(f"run {fid} bg-subtracted (deg5, cut {onset_b:.2f})")

        # peak table on the wider-window FFT
        freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(onset_b, B.max()), bg_degree=5)
        sp = spec[0]
        # simple local maxima above 10% of max, F > 1 T
        pk = [j for j in range(2, len(sp) - 2)
              if sp[j] == max(sp[j-2:j+3]) and sp[j] > 0.08 * sp.max() and freqs[j] > 1.0]
        print("FFT peaks (cut = onset):")
        for j in pk:
            print(f"  F = {freqs[j]:6.2f} T  amp {sp[j]/sp.max():.2f}  F/F_L = {freqs[j]/FL:.3f}")
        dF = 1.0 / (1.0 / onset_b - 1.0 / B.max())
        print(f"record resolution dF = {dF:.2f} T (onset {onset_b:.2f} -> {B.max():.1f} T)")

plt.tight_layout()
plt.savefig(f"{DIR}/hera_scratch/sdh_spots_67.png", dpi=110)
print("\nsaved hera_scratch/sdh_spots_67.png")
