"""Is the ~6.9 T tone density-independent? Overlay run 6 vs run 7 in 1/B; locate extrema; LL index fits."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, luttinger_frequency

def load(rid):
    run = open_run(f"data/{rid}")
    I = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"] / \
        run.meta["measurement_config"]["bias_resistor"]
    B = run.col("magnet_field"); R = run.col("sr1_X") / I
    o = np.argsort(B); return B[o], R[o]

def detrend(B, R, lo, hi, deg=5):
    m = (B >= lo) & (B <= hi)
    return B[m], R[m] - np.polyval(np.polyfit(B[m], R[m], deg), B[m])

fig, ax = plt.subplots(3, 1, figsize=(13, 11))
info = {}
for rid, n12, col, (lo, hi) in [(6, +3.2, "C0", (1.0, 7.6)), (7, -1.2, "C1", (1.0, 8.5))]:
    B, R = load(rid)
    Bd, dR = detrend(B, R, lo, hi)
    info[rid] = (Bd, dR, n12)
    ax[0].plot(1/Bd, dR/np.abs(dR).max(), col, lw=1.0, label=f"run {rid}  n_nom={n12:+.1f}e12  F_L={luttinger_frequency(abs(n12)*1e16):.1f} T")
    # minima of Rxx = LL centers of gaps
    mins, _ = find_peaks(-dR, prominence=0.15*np.ptp(dR))
    Bmin = Bd[mins]
    print(f"--- run {rid} (n_nom {n12:+.2f}e12): Rxx minima at B =", np.round(Bmin, 3))
    inv = 1/Bmin
    if len(inv) >= 3:
        idx = np.arange(len(inv))
        # fit 1/B_min = (1/F)*index + c  -> F from slope
        p = np.polyfit(idx, np.sort(inv), 1)
        print(f"    uniform-in-1/B spacing fit: d(1/B) = {p[0]:.5f} /T  -> F = {1/p[0]:.2f} T")
        print(f"    residuals: {np.round(np.sort(inv) - np.polyval(p, idx), 5)}")
    for b in Bmin:
        ax[0].axvline(1/b, color=col, ls=":", alpha=0.4)
ax[0].legend(); ax[0].set_xlabel("1/B (1/T)"); ax[0].set_ylabel("dRxx (norm)")
ax[0].set_title("Background-subtracted SdH vs 1/B — are the two densities in phase?")

# raw traces, both
for rid, col in [(6, "C0"), (7, "C1")]:
    B, R = load(rid)
    ax[1].plot(B, R, col, lw=0.8, label=f"run {rid}")
ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("Rxx (Ohm)"); ax[1].legend(); ax[1].set_title("raw Rxx(B)")

# high-field zoom
for rid, col in [(6, "C0"), (7, "C1")]:
    B, R = load(rid); m = B >= 1.0
    ax[2].plot(B[m], R[m], col, lw=0.9, label=f"run {rid}")
ax[2].set_xlim(1, 10); ax[2].set_ylim(-60, 620); ax[2].grid(alpha=0.3, which="both")
ax[2].set_xticks(np.arange(1, 10.5, 0.5)); ax[2].set_xlabel("B (T)"); ax[2].legend()
fig.tight_layout(); fig.savefig("hera_scratch/spot_phase.png", dpi=110)
print("saved hera_scratch/spot_phase.png")

# direct correlation between the two records on the shared 1/B range
B6, d6, _ = info[6]; B7, d7, _ = info[7]
grid = np.linspace(max(1/B6.max(), 1/B7.max()), min(1/B6.min(), 1/B7.min()), 800)
i6 = np.interp(grid, 1/B6[::-1], d6[::-1]); i7 = np.interp(grid, 1/B7[::-1], d7[::-1])
i6 -= i6.mean(); i7 -= i7.mean()
print(f"\nshared 1/B range {grid[0]:.3f}-{grid[-1]:.3f} /T; Pearson r(run6, run7) = {np.corrcoef(i6, i7)[0,1]:+.3f}")
