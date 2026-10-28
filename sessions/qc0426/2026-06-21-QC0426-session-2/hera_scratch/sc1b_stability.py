import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft
import scipy.constants as cst

r = open_run("data/3")
B = r.col("magnet_field"); i = r.col("sr0_X") / (-1e6)
R1 = r.col("sr1_X") / i
o = np.argsort(B); B, R1 = B[o], R1[o]
n = 3.5e16; F_L = cst.h/(4*cst.e)*n
print(f"F_L={F_L:.1f} T")

# Count oscillations by eye: bg-sub at high B, plot dRxx vs 1/B
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
for cutoff, c in [(2.0, "C0"), (3.0, "C1"), (4.0, "C2")]:
    m = B >= cutoff
    coef = np.polyfit(B[m], R1[m], 4); dR = R1[m] - np.polyval(coef, B[m])
    ax[0].plot(1/B[m], dR, ".-", ms=4, lw=0.9, color=c, label=f"cut {cutoff}T (deg4)")
ax[0].set_xlabel("1/B [1/T]"); ax[0].set_ylabel("dRxx [ohm]")
ax[0].set_title("sr1 bg-sub vs 1/B (count periods)"); ax[0].legend(); ax[0].grid(alpha=0.3)

# Stability: vary cutoff x bg_degree, report peak in F>2T (skip bg-residual band)
print("\ncutoff bg_deg | peak_F(>2T)  (looking for a stable tone)")
for cutoff in (1.5, 2.0, 3.0, 4.0):
    row = []
    for deg in (3, 5, 7):
        f, mag = sdh_fft(R1[:, None], B, b_range=(cutoff, B.max()), bg_degree=deg)
        mag = np.asarray(mag).squeeze()
        sel = f > 2.0
        pk = f[sel][np.argmax(mag[sel])]
        row.append(pk)
    print(f"  {cutoff:4.1f}   {str((3,5,7)):10s} | " + "  ".join(f"{p:5.1f}T" for p in row))

# FFT overlay, full and zoomed, cut 3T deg 4/5/7
for deg, c in [(3, "C0"), (5, "C1"), (7, "C2")]:
    f, mag = sdh_fft(R1[:, None], B, b_range=(3.0, B.max()), bg_degree=deg)
    mag = np.asarray(mag).squeeze()
    ax[1].plot(f, mag/mag[f > 2].max(), color=c, lw=1.1, label=f"deg{deg}")
ax[1].axvline(F_L, ls="--", c="k", label=f"F_L={F_L:.0f}T")
ax[1].set_xlabel("F [T]"); ax[1].set_ylabel("norm FFT (>2T)"); ax[1].set_xlim(0, 45)
ax[1].set_title("sr1 FFT cut 3T, bg-deg stability"); ax[1].legend()
fig.tight_layout(); fig.savefig("hera_scratch/sc1b_stability.png", dpi=110)
print("saved hera_scratch/sc1b_stability.png")
