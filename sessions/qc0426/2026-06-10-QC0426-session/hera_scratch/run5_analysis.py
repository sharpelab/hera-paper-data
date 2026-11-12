"""Run 5 — overnight fine-B D=0 fan (6->0 T, 121 x 271). Main analysis.

Outputs:
  run5_map.png      log|R| maps (sr1, sr2) + model chain loci overlay
  run5_bgdiv.png    background-divided sr1 with model overlay
  run5_fixed_n.png  Rxx(B) waterfall at fixed n in 0.7-1.4 (series test)
  stdout            nu=6 edge track, chain-locus residual stats
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import median_filter, uniform_filter1d

sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\aba_trilayer")
from ll_spectrum import SWMcC
from crossing_model import ml_trajectories

eps0, e = 8.8541878128e-12, 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
NF = 271

m = json.load(open(r"data/5/metadata.json"))
arr = np.loadtxt(r"data/5/data.tsv.gz")
cols = m["columns"]
nr = arr.shape[0] // NF
arr = arr[: nr * NF]
g = lambda nm: arr[:, cols.index(nm)].reshape(nr, NF)
B = g("mag")[:, 0]
n12 = 2 * c_tg * g("DC_bias")[0] / e * 1e-16
I = g("sr0_X") / (-1e6)
R1 = np.abs(g("sr1_X") / I)
R2 = np.abs(g("sr2_X") / I)
print(f"rows {nr}, B {B.max():.2f} -> {B.min():.2f}, n {n12.min():.2f} .. {n12.max():.2f}")

# model chains
p = SWMcC()
Bg = np.linspace(0.3, 6.0, 80)
tr = ml_trajectories(p, Bg, nmax=200)

# ---- map ----
fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
for ax, R, name in [(axes[0], R1, "sr1 (09-01)"), (axes[1], R2, "sr2 (12-20)")]:
    pc = ax.pcolormesh(n12, B, R, norm=LogNorm(vmin=40, vmax=np.nanpercentile(R, 99.5)),
                       cmap="inferno", shading="nearest")
    fig.colorbar(pc, ax=ax, label="|R| (Ohm)")
    for NM, v in sorted(tr.items()):
        nv, Bv = np.asarray(v)
        msk = (nv >= -0.4) & (nv <= 8) & (Bv <= 6.1)
        if msk.sum() > 1:
            ax.plot(nv[msk], Bv[msk], "c--", lw=0.8, alpha=0.8)
    ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
    ax.set_title(name)
axes[0].set_ylabel("B (T)")
fig.suptitle("Run 5 — D=0 fine-B fan (0.05 T rows), cyan: model N_M chains (no rescale)")
fig.tight_layout()
fig.savefig(r"hera_scratch/run5_map.png", dpi=130)

# ---- background-divided ----
bg = median_filter(R1, size=(1, 31), mode="nearest")
ratio = np.log10(R1 / np.maximum(bg, 1e-3))
fig2, ax2 = plt.subplots(figsize=(11, 6))
pc = ax2.pcolormesh(n12, B, ratio, cmap="RdBu_r", vmin=-0.25, vmax=0.25, shading="nearest")
fig2.colorbar(pc, ax=ax2, label="log10(R/smooth)")
for NM, v in sorted(tr.items()):
    nv, Bv = np.asarray(v)
    msk = (nv >= -0.4) & (nv <= 8) & (Bv <= 6.1)
    if msk.sum() > 1:
        ax2.plot(nv[msk], Bv[msk], "k--", lw=0.8, alpha=0.7)
ax2.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
ax2.set_ylabel("B (T)")
ax2.set_title("Run 5 sr1 — background-divided, black: model chains")
fig2.tight_layout()
fig2.savefig(r"hera_scratch/run5_bgdiv.png", dpi=130)

# ---- fixed-n series test (fine B is the new capability) ----
fig3, ax3 = plt.subplots(figsize=(9, 6))
for k, ncen in enumerate(np.arange(0.7, 1.45, 0.1)):
    j = np.argmin(np.abs(n12 - ncen))
    col = R1[:, j]
    sm = uniform_filter1d(col, 15)
    ax3.plot(B, col / np.maximum(sm, 1e-3) + 0.25 * k, lw=0.8,
             label=f"n={n12[j]:.2f}")
ax3.set_xlabel("B (T)")
ax3.set_ylabel("R/smooth (offset)")
ax3.legend(fontsize=7)
ax3.set_title("Run 5 — fixed-n detrended Rxx(B), series test band")
fig3.tight_layout()
fig3.savefig(r"hera_scratch/run5_fixed_n.png", dpi=130)
print("saved run5_map.png, run5_bgdiv.png, run5_fixed_n.png")

# ---- nu=6 edge track: per row, n position of max |d log R/dn| on the
# falling edge beyond the CNP peak ----
print("\nnu-edge track (sr1): n* = steepest descent of log R for n in (0.3, 2.5)")
sel = (n12 > 0.3) & (n12 < 2.5)
ns = n12[sel]
for k in range(0, nr, 10):
    dlog = np.gradient(np.log10(np.maximum(uniform_filter1d(R1[k][sel], 5), 1)), ns)
    j = np.argmin(dlog)
    nu_edge = ns[j] * 41.356 / B[k] if B[k] > 0.2 else np.nan
    print(f"  B={B[k]:4.2f}: n*={ns[j]:5.2f}  nu*={nu_edge:6.2f}")
