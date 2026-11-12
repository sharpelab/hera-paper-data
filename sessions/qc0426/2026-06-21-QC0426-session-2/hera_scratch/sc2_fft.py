import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft
import scipy.constants as cst

r = open_run("data/4")
B = r.col("magnet_field"); i = r.col("sr0_X") / (-1e6)
R1 = r.col("sr1_X") / i; R2 = r.col("sr2_X") / i
o = np.argsort(B); B, R1, R2 = B[o], R1[o], R2[o]
F_L = cst.h / (4 * cst.e) * 3.5e16
print(f"F_L={F_L:.1f} T")

fig, ax = plt.subplots(2, 2, figsize=(14, 9))
ax[0,0].plot(B, R1, ".-", ms=3, lw=0.7, label="sr1 T3-T4")
ax[0,0].plot(B, R2, ".-", ms=3, lw=0.7, label="sr2 B4-B5")
ax[0,0].set_xlabel("B [T]"); ax[0,0].set_ylabel("Rxx [ohm]"); ax[0,0].legend()
ax[0,0].set_title("Run 4 raw Rxx(B) ELECTRON n=+3.5e12 D=0 (clean)")

# bg-sub vs 1/B (count periods)
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    m = B >= 1.5
    coef = np.polyfit(B[m], R[m], 4); dR = R[m] - np.polyval(coef, B[m])
    ax[0,1].plot(1/B[m], dR, ".-", ms=3, lw=0.8, color=c, label=ch)
ax[0,1].set_xlabel("1/B [1/T]"); ax[0,1].set_ylabel("dRxx [ohm]"); ax[0,1].legend()
ax[0,1].set_title("bg-sub vs 1/B (B>1.5T) — clean periodic?"); ax[0,1].grid(alpha=0.3)

# FFT both channels, several cutoffs (sr1)
for cut, c in [(1.5, "C0"), (2.0, "C1"), (3.0, "C2")]:
    f, mag = sdh_fft(R1[:, None], B, b_range=(cut, B.max()), bg_degree=5)
    mag = np.asarray(mag).squeeze(); ax[1,0].plot(f, mag/mag[f>2].max(), lw=1, label=f"sr1 cut {cut}T")
ax[1,0].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[1,0].set_xlabel("F [T]"); ax[1,0].set_ylabel("norm FFT"); ax[1,0].set_xlim(0, 60)
ax[1,0].legend(fontsize=8); ax[1,0].set_title("sr1 FFT vs cutoff (stable peak?)")

# sr1 vs sr2 at cut 2T, search secondary peaks
from scipy.signal import find_peaks
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    f, mag = sdh_fft(R[:, None], B, b_range=(2.0, B.max()), bg_degree=5)
    mag = np.asarray(mag).squeeze(); magn = mag/mag[f>2].max()
    ax[1,1].plot(f, magn, color=c, lw=1.2, label=ch)
    pk, props = find_peaks(magn[(f>3)], height=0.15)
    fpk = f[(f>3)][pk]; hpk = props["peak_heights"]
    print(f"{ch}: peaks(>3T, h>0.15): " + ", ".join(f"{ff:.1f}T(h{hh:.2f})" for ff,hh in zip(fpk,hpk)))
    dom = fpk[np.argmax(hpk)] if len(fpk) else np.nan
    print(f"   dominant {dom:.1f}T  F_L/dom={F_L/dom:.2f}  (1=single pocket@F_L=ABC; <1 w/ partner=ABA)")
ax[1,1].axvline(F_L, ls="--", c="k", lw=1.2, label=f"F_L={F_L:.0f}T")
ax[1,1].set_xlabel("F [T]"); ax[1,1].set_ylabel("norm FFT"); ax[1,1].set_xlim(0, 60)
ax[1,1].legend(fontsize=8); ax[1,1].set_title("FFT sr1 vs sr2 (cut 2T) + peak search")
fig.tight_layout(); fig.savefig("hera_scratch/sc2_fft.png", dpi=110)
print("saved hera_scratch/sc2_fft.png")
