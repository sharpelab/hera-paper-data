"""Is there oscillation POWER below 1 T in run 6?

The sub-1 T leg (50 mT) aliases the 7.3 T comb in *frequency*, but aliasing
preserves *power*. So: detrend in sliding B windows and compare the residual
RMS to the point-to-point noise floor. A grid-independent onset statement.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

r = open_run("data/6"); mc = r.meta["measurement_config"]
B = r.col("magnet_field"); I = r.col("sr0_X") / mc["sr0_gain"]; R = r.col("sr1_X") / I
o = np.argsort(B); B, R = B[o], R[o]

# noise floor: 2nd difference of the dense 10 mT leg at high B, where the
# oscillation is slow in B -> 2nd diff is dominated by white noise.
hi = B > 8.0
nz = np.std(np.diff(R[hi], 2)) / np.sqrt(6)
print(f"white-noise sigma (from 2nd diff, B>8 T): {nz:.3f} Ohm   (R ~ {np.median(R[hi]):.0f} Ohm)")

print(f"\n{'B window':>14} {'npts':>5} {'dB':>7} {'resid RMS':>10} {'/sigma':>8}  verdict")
for lo, hi_ in ((0.15, 0.30), (0.30, 0.50), (0.50, 0.75), (0.75, 1.00),
                (1.00, 1.30), (1.30, 1.70), (1.70, 2.20)):
    m = (B >= lo) & (B < hi_)
    if m.sum() < 6:
        print(f"{lo:6.2f}-{hi_:5.2f} {m.sum():5d}   too few points")
        continue
    bb, rr = B[m], R[m]
    p = np.polyfit(bb, rr, min(3, m.sum() - 2))
    res = rr - np.polyval(p, bb)
    rms = np.std(res)
    print(f"{lo:6.2f}-{hi_:5.2f} {m.sum():5d} {np.median(np.diff(bb))*1e3:6.0f}mT "
          f"{rms:10.3f} {rms/nz:8.1f}  {'OSCILLATING' if rms/nz > 4 else 'noise-floor'}")

fig, ax = plt.subplots(2, 1, figsize=(11, 7))
m = B <= 2.2
ax[0].plot(B[m], R[m], ".-", ms=3, lw=0.7)
ax[0].axvline(1.0, color="r", ls="--", label="grid change 50 -> 10 mT")
ax[0].set_xlabel("B [T]"); ax[0].set_ylabel(r"$R_{xx}$ [$\Omega$]")
ax[0].set_title("run 6 raw, low field (n = +3.2e12, D = 0)"); ax[0].legend(fontsize=8)
mm = (B >= 0.15) & (B <= 2.2)
bb, rr = B[mm], R[mm]
res = rr - np.polyval(np.polyfit(bb, rr, 7), bb)
ax[1].plot(bb, res, ".-", ms=3, lw=0.7)
ax[1].axhline(0, color="k", lw=0.5)
ax[1].fill_between([0.15, 2.2], -3 * nz, 3 * nz, color="grey", alpha=0.3, label=r"$\pm3\sigma$ noise")
ax[1].axvline(1.0, color="r", ls="--")
ax[1].set_xlabel("B [T]"); ax[1].set_ylabel(r"$\Delta R_{xx}$ [$\Omega$]"); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig("hera_scratch/onset_lowB.png", dpi=110)
print("\nwrote hera_scratch/onset_lowB.png")
