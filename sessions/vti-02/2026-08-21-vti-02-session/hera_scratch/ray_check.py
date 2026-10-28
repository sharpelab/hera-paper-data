"""QH-ray lever-arm check on the fan (cnp-and-dline-calibration step 5): Landau-level minima in R(n, B) lie on
n = nu * e B / h. Track minima per B row in the design-frame n, fit each ray's slope dn/dB, and read the scale
factor s = n_actual/n_design from the requirement that slopes quantize as nu * (e/h) with integer nu.
Usage: menv python hera_scratch/ray_check.py <run_id>
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelmin
from hera.analysis import open_run, fan_grids, resistance_grids

DATA = Path(__file__).resolve().parents[1] / "data"
rid = int(sys.argv[1])
C_TG, C_BG, N_OFF = 2.7961e-3, 2.0330e-3, -0.069
e, h = 1.602176634e-19, 6.62607015e-34
r = open_run(DATA / str(rid)); f = fan_grids(r); rg = resistance_grids(f)
B = f.slow; R = rg.R["sr1"]; Vtg = f.grid("k_2400_tg_volt")[0]; Vbg = f.grid("k_2400_bg_volt")[0]
n_d = (C_TG * Vtg + C_BG * Vbg) / e * 1e-16 + N_OFF        # design frame (1e12 cm^-2)
eB_h = e / h * 1e-4 * 1e-12                                  # (e/h) in 1e12 cm^-2 per T
print(f"e/h = {eB_h:.4f} e12 cm^-2 per T; run {rid}: {f.nrows} rows, B {B.min():.2f}..{B.max():.2f}")

# collect minima (n_d, B) per row on a lightly smoothed R
pts = []
for i in range(f.nrows):
    Rs = gaussian_filter1d(R[i], 1.0)
    for j in argrelmin(Rs, order=2)[0]:
        if 1 <= j <= f.nfast - 2:
            pts.append((n_d[j], B[i], Rs[j]))
pts = np.array(pts)
print(f"{len(pts)} minima collected")

# for each candidate nu, the ray n_d = nu * eB_h * B / s passes through the origin (n_d = 0 at B = 0, since n_offset
# is already applied). Scan s in [0.7, 1.3]: score = number of minima within |n_d - nu*eB_h*B/s| < tol for integer nu.
best = None
for s in np.linspace(0.7, 1.3, 601):
    nu = pts[:, 0] * s / (eB_h * pts[:, 1])
    resid = np.abs(nu - np.round(nu))
    score = np.sum(resid < 0.15) - 0.5 * np.sum(resid > 0.35)
    if best is None or score > best[1]:
        best = (s, score, nu)
s_best, score, nu_best = best
print(f"best scale s = {s_best:.3f} (score {score:.0f}/{len(pts)}); nu of the minima near integers at that scale:")
nu_int = np.round(nu_best); ok = np.abs(nu_best - nu_int) < 0.15
for v in sorted(set(nu_int[ok].astype(int))):
    sel = ok & (nu_int == v)
    print(f"  nu = {v:2d}: {sel.sum():2d} minima, B {pts[sel,1].min():.2f}..{pts[sel,1].max():.2f} T, mean nu {nu_best[sel].mean():.2f}")
# scale profile
ss = np.linspace(0.7, 1.3, 601)
prof = [np.sum(np.abs((pts[:,0]*s/(eB_h*pts[:,1])) - np.round(pts[:,0]*s/(eB_h*pts[:,1]))) < 0.15) for s in ss]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].pcolormesh(n_d * s_best, B, R, shading="nearest", cmap="RdBu_r", vmin=np.nanpercentile(R, 2), vmax=np.nanpercentile(R, 98))
ax[0].plot(pts[ok, 0] * s_best, pts[ok, 1], "k.", ms=3)
for v in sorted(set(nu_int[ok].astype(int))):
    bb = np.linspace(B.min(), B.max(), 10); ax[0].plot(v * eB_h * bb, bb, "g-", lw=0.6)
ax[0].set_xlim((n_d * s_best).min(), (n_d * s_best).max()); ax[0].set_xlabel(f"n [1e12] (scale {s_best:.3f})"); ax[0].set_ylabel("B [T]"); ax[0].set_title("minima + integer-nu rays")
ax[1].plot(ss, prof); ax[1].axvline(s_best, color="r"); ax[1].set_xlabel("scale s"); ax[1].set_ylabel("# minima on integer rays"); ax[1].set_title("lever-arm scan")
plt.tight_layout(); out = Path(__file__).resolve().parent / f"rays_{rid}.png"; plt.savefig(out, dpi=90); print("saved", out)
