"""Landau-fan read: absolute lever arm + CNP location from LL minima.

Physics used, and nothing else: at field B, Landau levels hold n = nu*eB/h
carriers, so minima in Rxx sit at densities spaced by e*B/h per filling factor.
With n = c_tg*(V_tg - V_CNP)/e at fixed V_bg, a minimum lies at

    V_tg = V_CNP + nu * alpha * B,      alpha = e^2 / (h * c_tg)   [V / (T * nu)]

so the fan is a set of straight rays through (V_CNP, B=0). Fitting alpha gives
c_tg ABSOLUTELY (degeneracy only -- no band model, no assumed capacitance), and
V_CNP is where the rays converge. Two doping domains would give TWO convergence
points.
"""
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from hera.analysis import fan_grids, resistance_grids, summarize_run, open_run

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RID = int(sys.argv[1]) if len(sys.argv) > 1 else 5
B_MIN_FIT = 1.0          # rows below this have no developed LL structure

r = open_run(f"{BASE}/{RID}")
print(summarize_run(r))
fg = fan_grids(r)
def g(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); tg = g("k_2400_tg_volt")[0]; B = g("magnet_field")[:, 0]
Vx = np.abs(g("sr1_X"))
SENS = 5e-4
print(f"{fg.nrows} rows, B = {B.min():.2f}..{B.max():.2f} T; fast {len(tg)} pts "
      f"{tg[0]:+.3f}..{tg[-1]:+.3f} V")

# ---------- per-row minima ----------
def minima(row, prom_frac=0.06, edge=3):
    """Minima of log R (log so deep minima on a huge dynamic range register)."""
    y = gaussian_filter1d(np.log10(np.maximum(row, 1e-2)), 1.5)
    idx, pr = find_peaks(-y, prominence=prom_frac * np.ptp(y))
    out = []
    for i, p in zip(idx, pr["prominences"]):
        if not (edge <= i < len(y) - edge):
            continue
        y0, y1, y2 = y[i - 1], y[i], y[i + 1]
        d = y0 - 2 * y1 + y2
        sh = 0.5 * (y0 - y2) / d if d else 0.0
        out.append((tg[i] + sh * (tg[1] - tg[0]), row[i], p))
    return out


rows_min = {}
print("\nper-row Rxx minima (electron flank; V_tg, R):")
for k in range(fg.nrows):
    clipped = (Vx[k] > 0.9 * SENS).sum()
    m = minima(R[k])
    rows_min[k] = m
    tags = " ".join(f"{v:+.3f}({rr:.0f})" for v, rr, _ in m)
    print(f"  B={B[k]:.2f} T  clip {clipped:3d}/{len(tg)}  {tags}")

# ---------- fan fit ----------
# Collect minima from rows with developed LL structure, on the electron flank
# (V_tg above the clipped region) so one ray family is fitted at a time.
pts = []
for k in range(fg.nrows):
    if B[k] < B_MIN_FIT:
        continue
    clip_idx = np.where(Vx[k] > 0.9 * SENS)[0]
    v_hi = tg[clip_idx.max()] if len(clip_idx) else 0.0
    for v, rr, p in rows_min[k]:
        if v > v_hi + 0.05:
            pts.append((B[k], v))
pts = np.array(pts)
print(f"\n{len(pts)} electron-flank minima from rows with B >= {B_MIN_FIT} T")

if len(pts) < 6:
    print("too few minima to fit a fan yet")
    raise SystemExit

# 2-parameter search: V_CNP and alpha such that (V - V_CNP)/(alpha*B) is integer.
def score(vcnp, alpha):
    nu = (pts[:, 1] - vcnp) / (alpha * pts[:, 0])
    return np.mean((nu - np.round(nu)) ** 2), nu


best = None
for vcnp in np.linspace(-0.35, 0.35, 281):
    for alpha in np.linspace(0.004, 0.120, 1161):
        s, nu = score(vcnp, alpha)
        if np.abs(np.round(nu)).max() > 60 or np.abs(np.round(nu)).min() < 1:
            continue
        if best is None or s < best[0]:
            best = (s, vcnp, alpha)
s, vcnp, alpha = best
_, nu = score(vcnp, alpha)
nu_int = np.round(nu).astype(int)
print(f"\nbest fan fit: V_CNP = {vcnp:+.4f} V, alpha = {alpha:.5f} V/(T*nu), "
      f"rms integer residual {np.sqrt(s):.3f}")
print(f"  assigned filling factors: {sorted(set(nu_int.tolist()))}")
gaps = np.diff(sorted(set(nu_int.tolist())))
print(f"  spacing between observed nu: {sorted(set(gaps.tolist()))}")

# refine by least squares at fixed integers
A = np.stack([np.ones(len(pts)), nu_int * pts[:, 0]], axis=1)
coef, *_ = np.linalg.lstsq(A, pts[:, 1], rcond=None)
vcnp_f, alpha_f = coef
resid = pts[:, 1] - A @ coef
print(f"  refined: V_CNP = {vcnp_f:+.4f} V, alpha = {alpha_f:.5f}, "
      f"rms resid {resid.std(ddof=1)*1e3:.2f} mV")

c_tg_meas = cst.e ** 2 / (cst.h * alpha_f)
c_tg_prior = cst.epsilon_0 * 3.0 / 9.5e-9
print(f"\n  c_tg (measured, absolute) = {c_tg_meas:.5e} F/m^2")
print(f"  c_tg (geometry prior)     = {c_tg_prior:.5e} F/m^2   "
      f"ratio meas/prior = {c_tg_meas/c_tg_prior:.3f}")
print(f"  -> dn/dV_tg = {c_tg_meas/cst.e*1e-4*1e-12:.4f} e12 cm^-2 / V "
      f"(prior {c_tg_prior/cst.e*1e-4*1e-12:.4f})")
print(f"  -> implied top-gate hBN thickness = "
      f"{cst.epsilon_0*3.0/c_tg_meas*1e9:.2f} nm (card says 9.50 nm)")
print(f"\n  CNP at V_tg = {vcnp_f:+.4f} V (V_bg = 0)")
print(f"  zero-field ridges were: A {-0.2032:+.4f}, B {+0.1125:+.4f}")

fig, ax = plt.subplots(1, 2, figsize=(14.5, 5.6))
pc = ax[0].pcolormesh(tg, B, np.log10(R), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax[0], label=r"$\log_{10} R_{xx}$")
for nn in sorted(set(nu_int.tolist())):
    ax[0].plot(vcnp_f + nn * alpha_f * B, B, "-", lw=0.7, color="c", alpha=0.7)
ax[0].plot(pts[:, 1], pts[:, 0], "w.", ms=4)
ax[0].axvline(vcnp_f, color="lime", lw=1.0, ls="--")
ax[0].set_xlabel(r"$V_{tg}$ (V)"); ax[0].set_ylabel("B (T)")
ax[0].set_xlim(tg[0], tg[-1]); ax[0].set_ylim(B.min(), B.max())
ax[0].set_title(f"calibration fan, $V_{{bg}}$=0  —  rays at $V_{{CNP}}$={vcnp_f:+.3f} V")

ax[1].plot(nu_int * pts[:, 0], pts[:, 1], "o", ms=5)
xx = np.linspace((nu_int * pts[:, 0]).min(), (nu_int * pts[:, 0]).max(), 10)
ax[1].plot(xx, vcnp_f + alpha_f * xx, "-", lw=1.2)
ax[1].set_xlabel(r"$\nu \cdot B$ (T)"); ax[1].set_ylabel(r"$V_{tg}$ at minimum (V)")
ax[1].set_title(f"fan collapse: slope $\\alpha$={alpha_f:.4f} V/(T·$\\nu$)\n"
                f"$c_{{tg}}$ = {c_tg_meas:.3e} F/m² "
                f"({c_tg_meas/c_tg_prior:.2f}× prior)")
ax[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{SCRATCH}/fan.png", dpi=120)
print(f"\nwrote {SCRATCH}/fan.png")
