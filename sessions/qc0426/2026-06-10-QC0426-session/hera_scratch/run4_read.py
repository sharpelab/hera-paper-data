"""Run 4 (densified 8->6 T segment) — render + integer-ray counting.

Works on partial data. Per-row minima at native resolution; ray counting
between strong gaps -> absolute nu; sequence symmetry test.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

eps0, e = 8.8541878128e-12, 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
NFAST = 201

m = json.load(open(r"data/4/metadata.json"))
f = r"data/4/data.tsv.gz" if os.path.exists(r"data/4/data.tsv.gz") else r"data/4/data.tsv"
arr = np.loadtxt(f)
cols = m["columns"]
nrows = arr.shape[0] // NFAST
arr = arr[: nrows * NFAST]
g = lambda nm: arr[:, cols.index(nm)].reshape(nrows, NFAST)
B = g("mag")[:, 0]
n12 = 2 * c_tg * g("DC_bias")[0] / e * 1e-16
I = g("sr0_X") / (-1e6)
print(f"complete rows: {nrows}, B {B.max():.2f} -> {B.min():.2f} T")

R1 = np.abs(g("sr1_X") / I)
R2 = np.abs(g("sr2_X") / I)
Rxy = g("sr3_X") / I

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, R, name in [(axes[0], R1, "sr1 (09-01)"), (axes[1], R2, "sr2 (12-20)")]:
    pc = ax.pcolormesh(n12, B, R, norm=LogNorm(vmin=max(np.nanpercentile(R, 3), 10),
                       vmax=np.nanpercentile(R, 99.5)), cmap="inferno", shading="nearest")
    fig.colorbar(pc, ax=ax, label="|R| (Ohm)")
    ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
    ax.set_title(name)
axes[0].set_ylabel("B (T)")
fig.suptitle(f"Run 4 — densified D=0 segment, rows to B={B.min():.2f} T")
fig.tight_layout()
fig.savefig(r"hera_scratch/run4_map.png", dpi=130)
print("saved hera_scratch/run4_map.png")

# per-row minima at native resolution
print("\nper-row minima (sr1), apparent nu = 41.356*n/B:")
for k in range(nrows):
    logR = np.log10(np.maximum(uniform_filter1d(R1[k], 3), 1e-2))
    pk, pr = find_peaks(-logR, prominence=0.04)
    nus = n12[pk] * 41.356 / B[k]
    msk = n12[pk] > 0.15
    with np.printoptions(precision=2, suppress=True):
        print(f"  B={B[k]:4.2f}: nu_app = {np.sort(nus[msk])}")

# stacked traces for the top rows
fig2, ax2 = plt.subplots(figsize=(10, 6))
for k in range(min(nrows, 9)):
    ax2.semilogy(n12, R1[k] * 10 ** (0.25 * k), lw=0.8,
                 label=f"B={B[k]:.2f} T (x10^{0.25*k:.1f})")
ax2.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
ax2.set_ylabel("|R_sr1| (Ohm), offset")
ax2.legend(fontsize=7, ncol=2)
ax2.set_title("Run 4 — stacked rows, sr1")
fig2.tight_layout()
fig2.savefig(r"hera_scratch/run4_stack.png", dpi=130)
print("saved hera_scratch/run4_stack.png")
