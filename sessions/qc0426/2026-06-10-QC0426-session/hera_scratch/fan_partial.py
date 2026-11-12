"""Partial-fan re-form + ABA model overlay for run 3 (D=0 electron-side fan).

Re-run any time; uses however many complete B-rows have landed.
Renders per-channel log-|Rxx|(n, B) with predicted N_M chain loci overlaid.
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\aba_trilayer")
from ll_spectrum import SWMcC
from crossing_model import ml_trajectories

eps0 = 8.8541878128e-12
e = 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9

NFAST = 121

m = json.load(open(r"data/3/metadata.json"))
arr = np.loadtxt(r"data/3/data.tsv")
cols = m["columns"]
c = {name: arr[:, i] for i, name in enumerate(cols)}

nrows = arr.shape[0] // NFAST
arr = arr[: nrows * NFAST]
print(f"complete B-rows: {nrows}")

def grid(name):
    return arr[:, cols.index(name)].reshape(nrows, NFAST)

B = grid("mag")[:, 0]
vtg = grid("DC_bias")[0]
n12 = 2 * c_tg * vtg / e * 1e-16          # 1e12 cm^-2 along D=0 line
I = grid("sr0_X") / (-1e6)
print(f"B rows: {B.min():.2f} -> {B.max():.2f} T")

# model chains
p = SWMcC()
Bg = np.linspace(max(0.25, B.min() + 0.01), max(B.max(), 0.5), 60)
tr = ml_trajectories(p, Bg, nmax=130)

fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
for ax, (name, key) in zip(axes, [("sr1 (09-01)", "sr1_X"),
                                  ("sr2 (12-20)", "sr2_X"),
                                  ("sr3 Rxy (09-12)", "sr3_X")]):
    R = np.abs(grid(key) / I)
    vmin = max(np.nanpercentile(R, 5), 1)
    pc = ax.pcolormesh(n12, B, R, norm=LogNorm(vmin=vmin,
                       vmax=np.nanpercentile(R, 99.5)), cmap="inferno",
                       shading="nearest")
    fig.colorbar(pc, ax=ax, label="|R| (Ohm)")
    for NM, v in sorted(tr.items()):
        nv, Bv = np.asarray(v)
        msk = (nv >= n12.min()) & (nv <= n12.max()) & (Bv <= B.max() + 0.3)
        if msk.sum() > 1:
            ax.plot(nv[msk], Bv[msk], "c--", lw=1)
            ax.annotate(f"$N_M$={NM}", (nv[msk][-1], min(Bv[msk][-1], B.max())),
                        color="c", fontsize=7)
    ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
    ax.set_title(name)
axes[0].set_ylabel("B (T)")
fig.suptitle(f"Run 3 partial fan — D=0, rows to {B.max():.2f} T — cyan: model N_M chains (no rescale)")
fig.tight_layout()
fig.savefig(r"hera_scratch/fan_partial.png", dpi=130)
print("saved hera_scratch/fan_partial.png")

# quick onset metric: per-row std of log|R| (sr1) at n>0.3
Rxx = np.abs(grid("sr1_X") / I)
sel = n12 > 0.3
for k in range(nrows):
    row = Rxx[k][sel]
    print(f"B={B[k]:4.2f} T  sr1 med {np.median(row):8.1f} Ohm   "
          f"osc amp (p90/p10) {np.percentile(row,90)/np.percentile(row,10):6.2f}")

# --- background-divided render (sr1, sr2): R / smooth(R along n) per row ---
from scipy.ndimage import median_filter
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, (name, key) in zip(axes2, [("sr1 (09-01)", "sr1_X"), ("sr2 (12-20)", "sr2_X")]):
    R = np.abs(grid(key) / I)
    bg = median_filter(R, size=(1, 25), mode="nearest")
    ratio = R / np.maximum(bg, 1e-3)
    pc = ax.pcolormesh(n12, B, np.log10(ratio), cmap="RdBu_r", vmin=-0.3, vmax=0.3,
                       shading="nearest")
    fig2.colorbar(pc, ax=ax, label="log10(R / smooth bg)")
    for NM, v in sorted(tr.items()):
        nv, Bv = np.asarray(v)
        msk = (nv >= n12.min()) & (nv <= n12.max()) & (Bv <= B.max() + 0.3)
        if msk.sum() > 1:
            ax.plot(nv[msk], Bv[msk], "k--", lw=0.8, alpha=0.6)
    ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
    ax.set_title(name)
axes2[0].set_ylabel("B (T)")
fig2.suptitle(f"Run 3 — background-divided, rows to {B.max():.2f} T (black: model chains)")
fig2.tight_layout()
fig2.savefig(r"hera_scratch/fan_partial_bgdiv.png", dpi=130)
print("saved hera_scratch/fan_partial_bgdiv.png")
