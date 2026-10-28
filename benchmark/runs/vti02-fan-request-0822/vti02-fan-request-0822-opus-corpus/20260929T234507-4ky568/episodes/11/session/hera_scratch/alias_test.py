"""Grid-choice test for the fan: re-sample run 6 (n=+3.2e12) onto candidate uniform-1/B fan
grids and compare per-grid FFTs against the dense record, over several analysis windows.
Question: does Delta(1/B) = 1/(3 F_L) fold the measured 60/90 T harmonic content back into the
0-35 T claim band, while 1/(4 F_L) does not?"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft

here = Path(__file__).resolve().parent
r = open_run(here.parent / "data" / "6")
B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
o = np.argsort(B); B, R = B[o], R[o]
FL = 33.1
B_LO_ACQ = 0.65

GRIDS = [("dense", None), ("3/period (0.01007)", 1 / (3 * FL)), ("4/period (0.00755)", 1 / (4 * FL))]
WINDOWS = [(0.65, 4.0), (1.2, 7.5), (2.0, 10.0)]

def grid_pick(dinv, b_lo, b_hi):
    if dinv is None:
        m = (B >= b_lo) & (B <= b_hi); return B[m], R[m]
    inv = np.arange(1 / 10.0, 1 / B_LO_ACQ + 1e-12, dinv)     # acquisition grid, full span
    Bt = 1 / inv[::-1]
    idx = np.unique(np.abs(B[:, None] - Bt[None, :]).argmin(axis=0))
    Bg, Rg = B[idx], R[idx]
    m = (Bg >= b_lo) & (Bg <= b_hi)
    return Bg[m], Rg[m]

fig, axes = plt.subplots(len(WINDOWS), 1, figsize=(11, 10), sharex=True)
for ax, (lo, hi) in zip(axes, WINDOWS):
    print(f"=== analysis window B {lo}-{hi} T   (dF = {1/(1/lo - 1/hi):.2f} T)")
    for lab, dinv in GRIDS:
        Bg, Rg = grid_pick(dinv, lo, hi)
        if len(Bg) < 25:
            print(f"  {lab}: only {len(Bg)} pts — skip"); continue
        f, spec = sdh_fft(Rg[:, None], Bg, b_range=(lo, hi), bg_degree=5, nfft=4096, log=False)
        s = spec[0] / spec[0].max()
        pk = np.where((s[1:-1] > s[:-2]) & (s[1:-1] > s[2:]) & (s[1:-1] > 0.10))[0] + 1
        print(f"  {lab:20s} N={len(Bg):4d}  peaks<45T:",
              [(round(f[i], 1), round(s[i], 2)) for i in pk if f[i] < 45])
        ax.plot(f, s, lw=1.0, label=f"{lab} (N={len(Bg)})")
    ax.axvline(FL, color="r", ls="--", lw=1)
    ax.set_xlim(0, 60); ax.set_ylabel("|FFT| norm"); ax.legend(fontsize=7)
    ax.set_title(f"window B {lo}-{hi} T", fontsize=9)
axes[-1].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig(here / "fan_grid_alias.png", dpi=110)
print("saved", here / "fan_grid_alias.png")
