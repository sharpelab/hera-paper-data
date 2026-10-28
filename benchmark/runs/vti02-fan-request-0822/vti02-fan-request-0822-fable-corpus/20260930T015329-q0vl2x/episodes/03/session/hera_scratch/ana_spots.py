"""Runs 6 & 7 — SdH spot checks (electron n=+3.2e12, hole n=-1.2e12), D=0.
Raw traces, per-tone onsets, FFT tone content vs F_L. Scratch pass."""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS = 1.0 / 100e6  # 1 V drive / 100 MOhm
R_FS = 50e-6 / I_BIAS  # 50 uV sensitivity -> 5 kOhm full scale

runs = {
    6: dict(n=+3.2e12 * 1e4, label="electron n=+3.2e12"),  # SI m^-2
    7: dict(n=-1.2e12 * 1e4, label="hole n=-1.2e12"),
}

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for i, (rid, info) in enumerate(runs.items()):
    r = open_run(f"{BASE}/{rid}")
    print(f"===== run {rid} — {info['label']} =====")
    print(summarize_run(r))
    B = r.col("magnet_field")
    R = r.col("sr1_X") / 1.0 / I_BIAS  # gain 1
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = float(luttinger_frequency(info["n"]))
    print(f"F_L = {FL:.1f} T; B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; R range {R.min():.1f}..{R.max():.1f} Ohm; FS {R_FS:.0f} Ohm")

    ax = axs[0, i]
    ax.plot(B, R, lw=0.6)
    ax.set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid}: {info['label']} raw")

    try:
        o = sdh_onset(R, B, r_full_scale=R_FS)
        print(o)
        print(f"onset_b = {o.onset_b:.3f} T")
        for t in o.tones:
            print("  tone:", t)
        blo = o.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        blo = 1.5

    freqs, spec = sdh_fft(R[:, None], B, b_range=(max(blo, 0.5), B.max()), log=False)
    s = spec[0]
    ax2 = axs[1, i]
    ax2.plot(freqs, s / s.max(), lw=0.8)
    ax2.axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f} T")
    ax2.axvline(0.72 * FL, color="g", ls=":", label="0.72 F_L")
    ax2.axvline(0.28 * FL, color="g", ls=":", label="0.28 F_L")
    ax2.set(xlabel="F (T)", xlim=(0, 1.6 * FL), ylabel="FFT mag (norm)", title=f"run {rid} FFT, B>{max(blo,0.5):.2f} T")
    ax2.legend(fontsize=8)
    # peak list
    from scipy.signal import find_peaks

    pk, props = find_peaks(s, height=0.05 * s.max(), distance=3)
    for p in pk:
        print(f"  FFT peak: F = {freqs[p]:6.2f} T  ({freqs[p]/FL:.3f} F_L)  amp {s[p]/s.max():.2f}")

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_raw_fft.png", dpi=120)
print("saved spots_raw_fft.png")
