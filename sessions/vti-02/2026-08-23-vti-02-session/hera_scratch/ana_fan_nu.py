"""Extract Rxx minima from the fan and fit nu lines: n_true = scale * n_geo; minima at n_true = nu e B / h."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import argrelmin
from hera.analysis import open_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

rid = int(sys.argv[1])
r = open_run(f"data/{rid}")
mc = r.meta["measurement_config"]
vt = r.col("k_2400_tg_volt"); vb = r.col("k_2400_bg_volt"); B = r.col("magnet_field")
I = r.col("sr0_X") / mc["sr0_gain"]; R = np.abs(r.col("sr1_X") / I)
nfast = len(r.meta["fast_setpoints"][0]); nrows = len(R) // nfast
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
n_geo, _ = calc_nD(vt, vb, c_tg, c_bg)
Rg = R[:nrows*nfast].reshape(nrows, nfast); Bg = B[:nrows*nfast].reshape(nrows, nfast); ng = n_geo[:nrows*nfast].reshape(nrows, nfast)
# smooth each row lightly, find local minima with prominence in log space
pts = []
for i in range(nrows):
    lr = np.log10(np.maximum(Rg[i], 1e-1))
    ls = np.convolve(lr, np.ones(3)/3, mode="same")
    idx = argrelmin(ls, order=3)[0]
    for j in idx:
        lo = max(0, j-6); hi = min(nfast, j+7)
        prom = max(ls[lo:hi]) - ls[j]
        if prom > 0.25 and 3 < j < nfast-4 and abs(ng[i, j]) > 0.12:
            pts.append((Bg[i, j], ng[i, j], prom))
pts = np.array(pts)
print(f"{len(pts)} minima candidates")
# for each candidate: nu_geo = n_geo/(eB/h); the true filling nu = scale*nu_geo should cluster at multiples of 2/4
nu_geo = pts[:, 1] * 1e16 / (cst.e * pts[:, 0] / cst.h)
best = None
for scale in np.arange(0.7, 1.45, 0.005):
    nu = nu_geo * scale
    err = np.mean(np.minimum(np.abs(nu - np.round(nu/4)*4), 1.0)**2)
    if best is None or err < best[1]:
        best = (scale, err)
scale = best[0]
print(f"best n-scale (minima at multiples of 4): {scale:.3f}  (rms {best[1]**0.5:.2f})")
nu = nu_geo * scale
for target in [-12, -8, -4, 4, 8, 12, 16, 20]:
    sel = np.abs(nu - target) < 1.2
    if sel.sum():
        print(f"nu={target:+3d}: {sel.sum():3d} pts, B {pts[sel,0].min():.1f}-{pts[sel,0].max():.1f} T, residual {np.mean(nu[sel]-target):+.2f}")
fig, ax = plt.subplots(figsize=(9, 7))
pm = ax.pcolormesh(ng*scale, Bg, np.log10(Rg), shading="nearest", cmap="magma")
fig.colorbar(pm, ax=ax, label="log10 |Rxx|")
ax.plot(pts[:, 1]*scale, pts[:, 0], "c.", ms=3)
for t in [-12, -8, -4, 4, 8, 12, 16, 20]:
    bb = np.linspace(0.5, Bg.max(), 40)
    ax.plot(t*cst.e*bb/cst.h*1e-16, bb, "w--", lw=0.4)
    ax.text(t*cst.e*Bg.max()/cst.h*1e-16, Bg.max()*0.98, str(t), color="w", fontsize=7, ha="center")
ax.set_xlim((ng*scale).min(), (ng*scale).max()); ax.set_xlabel(f"n = {scale:.2f} x n_geo (1e12 cm^-2)"); ax.set_ylabel("B (T)")
ax.set_title(f"run {rid}: minima + nu fit")
fig.tight_layout(); fig.savefig(f"hera_scratch/run{rid}_nu.png", dpi=110); print("saved")
