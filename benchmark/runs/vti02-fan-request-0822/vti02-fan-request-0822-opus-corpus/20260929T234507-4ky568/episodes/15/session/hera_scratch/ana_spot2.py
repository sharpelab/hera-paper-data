"""Run 6 (electron, n=+3.2e12) — high-resolution 1/B FFT: is there a real heavy tone near 26 T
between the 3rd (22) and 4th (29) harmonics of the 7.3 T fundamental?  Also the B-window split."""
import numpy as np, matplotlib, warnings
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency
warnings.simplefilter("ignore")

r = open_run("data/6")
B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / (-1e6))
o = np.argsort(B); B, R = B[o], R[o]
F_L = luttinger_frequency(3.2e12 * 1e4)
print(f"F_L = {F_L:.2f} T; model ABAB @ n=+3.2e12 ~ (7.2, 25.9) T; ABCA = {F_L:.1f} T")

windows = [(1.0, 10.0), (1.2, 7.5), (1.2, 10.0), (1.5, 10.0), (2.0, 10.0), (1.0, 5.0), (3.0, 10.0)]
fig, axes = plt.subplots(2, 2, figsize=(13, 8))

ax = axes[0, 0]
for (lo, hi) in windows[:5]:
    for deg in (5,):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=deg, log=False, nfft=8192)
        s = sp[0]; m = (f > 2) & (f < 60)
        ax.plot(f[m], s[m] / s[m].max(), lw=1.0, label=f"{lo}-{hi} T (dF {1/(1/lo-1/hi):.2f})")
ax.axvline(F_L, color="r", ls="--", lw=1); ax.axvline(25.9, color="b", ls="--", lw=1)
ax.axvline(7.2, color="g", ls="--", lw=1)
for k in (2, 3, 4):
    ax.axvline(k * 7.3, color="k", ls=":", lw=0.7)
ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| norm"); ax.legend(fontsize=6)
ax.set_title("run 6 — window dependence (g: ABAB light 7.2, b: ABAB heavy 25.9, r: F_L=ABCA 33.1; dotted k x 7.3)")

# bg_degree stability
ax = axes[0, 1]
for deg in (3, 5, 7, 9):
    f, sp = sdh_fft(R[:, None], B, b_range=(1.2, 10.0), bg_degree=deg, log=False, nfft=8192)
    s = sp[0]; m = (f > 2) & (f < 60)
    ax.plot(f[m], s[m] / s[m].max(), lw=1.0, label=f"bg_degree {deg}")
ax.axvline(F_L, color="r", ls="--"); ax.axvline(25.9, color="b", ls="--"); ax.axvline(7.2, color="g", ls="--")
for k in (2, 3, 4): ax.axvline(k * 7.3, color="k", ls=":", lw=0.7)
ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.set_title("bg_degree stability, 1.2-10 T")

# B-window split: low half vs high half in 1/B
ax = axes[1, 0]
for (lo, hi, lab) in [(1.2, 2.2, "low-B 1.2-2.2"), (2.2, 10.0, "high-B 2.2-10")]:
    f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=8192)
    s = sp[0]; m = (f > 2) & (f < 60)
    ax.plot(f[m], s[m] / s[m].max(), lw=1.0, label=f"{lab} (dF {1/(1/lo-1/hi):.2f})")
ax.axvline(F_L, color="r", ls="--"); ax.axvline(25.9, color="b", ls="--"); ax.axvline(7.2, color="g", ls="--")
for k in (2, 3, 4): ax.axvline(k * 7.3, color="k", ls=":", lw=0.7)
ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.set_title("B-window split (F_L-tone origin probe)")

# peak table at the best window
print("\npeak tables:")
for (lo, hi) in windows:
    f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=8192)
    s = sp[0]
    m = (f > 2.5) & (f < 60)
    ff, ss = f[m], s[m]
    idx = [i for i in range(1, len(ss) - 1) if ss[i] > ss[i - 1] and ss[i] >= ss[i + 1]]
    idx.sort(key=lambda i: -ss[i])
    top = [(ff[i], ss[i] / ss[idx[0]]) for i in idx[:8]]
    print(f"  [{lo:4.1f}-{hi:4.1f}] dF={1/(1/lo-1/hi):5.2f}: " +
          ", ".join(f"{a:.1f}T({b:.2f})" for a, b in top))

# raw + bg
ax = axes[1, 1]
m = (B >= 1.0) & (B <= 10.0)
cf = np.polyfit(B[m], R[m], 5)
ax.plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.8)
ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("run 6 bg-subtracted, 1-10 T")
fig.tight_layout(); fig.savefig("hera_scratch/spot_run6_hires.png", dpi=110)
print("saved hera_scratch/spot_run6_hires.png")
