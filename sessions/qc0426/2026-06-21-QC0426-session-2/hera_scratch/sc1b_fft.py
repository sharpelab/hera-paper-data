import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft
import scipy.constants as cst

r = open_run("data/3")
B = r.col("magnet_field"); i = r.col("sr0_X") / (-1e6)
R1 = r.col("sr1_X") / i; R2 = r.col("sr2_X") / i
order = np.argsort(B); B, R1, R2 = B[order], R1[order], R2[order]
n = 3.5e16; F_L = cst.h / (4 * cst.e) * n
print(f"F_L={F_L:.1f} T ; B {B.min():.2f}-{B.max():.2f} T ; {len(B)} pts")

fig, ax = plt.subplots(2, 2, figsize=(14, 9))
# (0,0) raw Rxx(B)
ax[0,0].plot(B, R1, ".-", ms=3, lw=0.7, label="sr1 T3-T4")
ax[0,0].plot(B, R2, ".-", ms=3, lw=0.7, label="sr2 B4-B5")
ax[0,0].set_xlabel("B [T]"); ax[0,0].set_ylabel("Rxx [ohm]"); ax[0,0].legend()
ax[0,0].set_title("Run 3 raw Rxx(B) HOLE n=-3.5e12 (clean sens)")

# (0,1) bg-subtracted vs 1/B (poly deg-5 in B), cutoff 1.5T
cutoff = 1.5
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    m = B >= cutoff
    coef = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(coef, B[m])
    ax[0,1].plot(1/B[m], dR, ".-", ms=3, lw=0.7, color=c, label=ch)
ax[0,1].set_xlabel("1/B [1/T]"); ax[0,1].set_ylabel("dRxx [ohm]")
ax[0,1].legend(); ax[0,1].set_title(f"bg-subtracted (B>={cutoff}T) vs 1/B")

# (1,0) FFT at several cutoffs (sr1)
for cut, c in [(1.0, "C0"), (1.5, "C1"), (2.5, "C2"), (3.5, "C3")]:
    f, mag = sdh_fft(R1[:,None], B, b_range=(cut, B.max()), bg_degree=5)
    mag=np.asarray(mag).squeeze(); ax[1,0].plot(f, mag, color=c, lw=1, label=f"sr1 cut {cut}T")
ax[1,0].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[1,0].set_xlabel("F [T]"); ax[1,0].set_ylabel("FFT mag"); ax[1,0].set_xlim(0, 1.3*F_L)
ax[1,0].legend(fontsize=8); ax[1,0].set_title("sr1 FFT vs cutoff (stability)")

# (1,1) FFT sr1 vs sr2 at cutoff 1.5
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    f, mag = sdh_fft(R[:,None], B, b_range=(1.5, B.max()), bg_degree=5)
    mag=np.asarray(mag).squeeze(); ax[1,1].plot(f, mag, color=c, lw=1.2, label=ch)
    pk = f[1:][np.argmax(mag[1:])]
    print(f"{ch}: dominant FFT peak at F={pk:.1f} T  (F_L={F_L:.1f}); F_L/peak={F_L/pk:.2f}")
ax[1,1].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[1,1].set_xlabel("F [T]"); ax[1,1].set_ylabel("FFT mag"); ax[1,1].set_xlim(0, 1.3*F_L)
ax[1,1].legend(fontsize=8); ax[1,1].set_title("FFT sr1 vs sr2 (cut 1.5T)")
fig.tight_layout(); fig.savefig("hera_scratch/sc1b_fft.png", dpi=110)
print("saved hera_scratch/sc1b_fft.png")
