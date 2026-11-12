"""Run 5 FFT over the usable high-B window, with stability sweep."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft

run = open_run("data/5")
B = run.col("magnet_field")
I = 20e-9
R = {ch: run.col_at(run.col_indices(f"{ch}_X")[-1]) / I for ch in ("sr1", "sr2")}
F_L = 62.0

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    for (blo, deg) in ((3.0, 5), (3.5, 4), (4.0, 3), (4.5, 3)):
        try:
            fr, mag = sdh_fft(R[ch], B, b_range=(blo, 8.0), bg_degree=deg)
            ax.plot(fr, mag / mag.max(), lw=0.8, label=f"[{blo},8] deg{deg}")
            if ch == "sr1":
                pk, _ = find_peaks(mag, height=mag.max() * 0.1, distance=4)
                print(f"sr1 [{blo},8] deg{deg}: peaks", [f"{fr[p]:.1f}({mag[p]/mag.max():.2f})" for p in pk])
        except Exception as e:
            print(ch, blo, deg, "->", e)
    ax.axvline(F_L, color="k", ls="--", lw=0.8, label="F_L=62 T")
    ax.axvline(F_L/2, color="gray", ls=":", lw=0.8)
    ax.set_xlim(0, 160); ax.set_xlabel("F (T)"); ax.set_title(ch); ax.legend(fontsize=7)
fig.suptitle("run 5 hole n=-6e12 D=0 - SdH FFT stability sweep")
fig.tight_layout(); fig.savefig("hera_scratch/sdh5_fft2.png", dpi=110)
print("saved")
