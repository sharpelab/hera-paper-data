"""Scratch analysis of a measure-while-ramping Landau fan (multimegasweep fan_row x gate line, B read per point).
usage: menv python hera_scratch/ana_fan.py <run_id> [Bbin=0.1]
Bins points onto (B, fast-index) -> Rxx image; plots vs 1/B; overlays nu lines using the geometry-prior n scale.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from hera.analysis import open_run, summarize_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

rid = int(sys.argv[1]); Bbin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
r = open_run(f"data/{rid}")
print(summarize_run(r))
mc = r.meta["measurement_config"]
vt = r.col("k_2400_tg_volt"); vb = r.col("k_2400_bg_volt"); B = r.col("magnet_field")
I = r.col("sr0_X") / mc["sr0_gain"]; R = np.abs(r.col("sr1_X") / I)
T = r.col("T_sample")
nfast = len(r.meta["fast_setpoints"][0]); nrows = len(R) // nfast
print(f"{nrows} complete rows x {nfast} pts; B {B.min():.3f}..{B.max():.3f} T; R {R.min():.0f}..{R.max():.0f} Ω; T {T.min():.3f}..{T.max():.3f} K")
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
n_geo, D_geo = calc_nD(vt, vb, c_tg, c_bg)
# row-wise: each row has a mean B; image rows = sweep rows (B increases along the row too, ~0.2 T)
Rg = R[:nrows * nfast].reshape(nrows, nfast); Bg = B[:nrows * nfast].reshape(nrows, nfast)
ng = n_geo[:nrows * nfast].reshape(nrows, nfast)
Brow = Bg.mean(axis=1)
print("row  <B>    B_span   R_min   R_max   R at fast mid")
for i in range(0, nrows, max(1, nrows // 10)):
    print(f"{i:3d} {Brow[i]:6.3f} {Bg[i].max()-Bg[i].min():6.3f} {Rg[i].min():7.0f} {Rg[i].max():7.0f} {Rg[i, nfast//2]:7.0f}")
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
pm = ax[0].pcolormesh(ng, Bg, np.log10(Rg), shading="nearest", cmap="magma")
fig.colorbar(pm, ax=ax[0], label="log10 |Rxx| (Ω)")
ax[0].set_xlabel("n_geo (1e12 cm^-2, geometry prior)"); ax[0].set_ylabel("B (T)"); ax[0].set_title(f"run {rid} fan (measured B per point)")
# nu lines on the geometry n scale for reference (n = nu e B / h)
for nu in [-12, -8, -4, 4, 8, 12, 16]:
    bb = np.linspace(0.5, Bg.max(), 50)
    ax[0].plot(nu * cst.e * bb / cst.h * 1e-16, bb, "c--", lw=0.5)
ax[0].set_xlim(ng.min(), ng.max())
# dR/dn to sharpen minima
dR = np.gradient(np.log10(Rg), axis=1)
pm = ax[1].pcolormesh(ng, Bg, dR, shading="nearest", cmap="RdBu_r", vmin=-np.percentile(np.abs(dR), 98), vmax=np.percentile(np.abs(dR), 98))
fig.colorbar(pm, ax=ax[1], label="d log10 R / d idx")
ax[1].set_xlabel("n_geo (1e12 cm^-2)"); ax[1].set_title("derivative")
fig.tight_layout(); fig.savefig(f"hera_scratch/run{rid}_fan.png", dpi=100); print("saved")
