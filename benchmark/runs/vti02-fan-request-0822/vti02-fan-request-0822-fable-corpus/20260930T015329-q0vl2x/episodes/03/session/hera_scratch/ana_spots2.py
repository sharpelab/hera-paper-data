"""Runs 6 & 7 — ana-grade figure: raw R(B), then windowed FFT with tone marks."""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS = 1.0 / 100e6

cases = {
    6: dict(n=+3.2e16, label="run 6 — electron n=+3.2e12", brange=(1.0, 10.0), model_pair=(7.31, 25.78)),
    7: dict(n=-1.2e16, label="run 7 — hole n=-1.2e12", brange=(0.72, 10.0), model_pair=(1.15, 11.25)),
}
fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for i, (rid, c) in enumerate(cases.items()):
    r = open_run(f"{BASE}/{rid}")
    B, R = r.col("magnet_field"), r.col("sr1_X") / I_BIAS
    o = np.argsort(B)
    B, R = B[o], R[o]
    FL = float(luttinger_frequency(c["n"]))
    ax = axs[0, i]
    ax.plot(B, R, lw=0.6, color="k")
    ax.set(xlabel="B (T)", ylabel=r"Rxx ($\Omega$)", title=c["label"])
    freqs, spec = sdh_fft(R[:, None], B, b_range=c["brange"], log=False)
    s = spec[0] / spec[0][freqs > 2].max()
    ax2 = axs[1, i]
    ax2.plot(freqs, s, lw=0.9, color="k")
    ax2.axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    for f, name, col in ((c["model_pair"][0], "model light", "tab:blue"), (c["model_pair"][1], "model heavy", "tab:green")):
        ax2.axvline(f, color=col, ls=":", lw=1, label=name)
    ax2.set(xlabel="F (T)", xlim=(0, 1.4 * FL), ylim=(0, 1.1), ylabel="FFT mag (norm)",
            title=f"FFT, B in {c['brange']} T")
    ax2.legend(fontsize=8)
    from scipy.signal import find_peaks
    pk, _ = find_peaks(s, height=0.08, distance=4)
    print(c["label"], "peaks (F>1.5 T):")
    for p in pk:
        if freqs[p] > 1.5:
            print(f"  F = {freqs[p]:6.2f} T ({freqs[p]/FL:.3f} F_L) amp {s[p]:.2f}")
fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_ana.png", dpi=120)
print("saved spots_ana.png")
