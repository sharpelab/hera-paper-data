"""Absolute density calibration + Landau-level degeneracy from run 4's fan minima.

The logic, stated carefully because the two unknowns are entangled:

  Rxx minima sit at integer filling nu_true = n_true*h/(e*B). Each fan line is
  n_true = (nu*e/h)*B, i.e. a straight line through the origin in (B, n).

  My n axis is n_assumed = alpha * n_true, where alpha is the error in the ABSOLUTE
  gate capacitance (the geometry prior). Fitting the fan lines on the assumed axis
  gives nu_assumed = alpha * nu_true.

  RATIOS of nu between fan lines are alpha-independent. So: fit the lines, take the
  ratios, identify the integer sequence, and alpha falls out. That pins both the
  degeneracy (the stacking discriminator) and the absolute density scale.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration

here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / "4")
fan = fan_grids(r)
rg = resistance_grids(fan)
Rxx = np.abs(rg.R["sr1"])
nB, nfast = Rxx.shape
_b = [i for i, c in enumerate(fan.cols) if c == "magnet_field"][-1]
B = fan.data[:, _b].reshape(nB, nfast).mean(axis=1)
Vtg = fan.grid("k_2400_tg_volt")[0]
RATIO = 1.2737
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / RATIO)
n_ass = cal_s.density(Vtg, RATIO * Vtg)                       # m^-2, assumed scale

# mask clipped points
_s = [i for i, c in enumerate(fan.cols) if c == "sr1_X"][0]
Vxx = fan.data[:, _s].reshape(nB, nfast)
Rxx = np.where(np.abs(Vxx) > 0.95e-3, np.nan, Rxx)

# ---- find Rxx minima per field row, on each carrier side --------------------
pts = []   # (B, n_assumed, side)
for i in range(nB):
    if B[i] < 1.5:            # below this the levels are not resolved
        continue
    row = Rxx[i]
    for side, sel in (("e", n_ass > 0.15e16), ("h", n_ass < -0.15e16)):
        idx = np.where(sel & np.isfinite(row))[0]
        if len(idx) < 5:
            continue
        sub = row[idx]
        for k in range(1, len(sub) - 1):
            if sub[k] < sub[k - 1] and sub[k] <= sub[k + 1] and sub[k] < 0.6 * np.nanmedian(sub):
                pts.append((B[i], n_ass[idx[k]], side))
pts = np.array([(a, b, 0 if c == "e" else 1) for a, b, c in pts])
print(f"detected {len(pts)} Rxx minima over B >= 1.5 T "
      f"({int((pts[:,2]==0).sum())} electron, {int((pts[:,2]==1).sum())} hole)")

# ---- nu on the ASSUMED scale for every minimum ------------------------------
nu_ass = pts[:, 1] * cst.h / (cst.e * pts[:, 0])
print(f"nu_assumed range: {nu_ass.min():+.1f} .. {nu_ass.max():+.1f}")

# ---- what common spacing best explains the observed nu_assumed set? ---------
# For a true sequence nu_true = m*g (m integer, g the degeneracy step), the observed
# values are nu_assumed = alpha*g*m -> all should be near-integer multiples of a single
# step s = alpha*g. Scan s and score how close the values sit to multiples of s.
cand = np.linspace(1.0, 12.0, 2201)
score = []
for s in cand:
    frac = np.abs(np.round(nu_ass / s) - nu_ass / s)
    ok = np.abs(nu_ass) > 0.7 * s          # ignore anything below the first gap
    score.append(np.mean(frac[ok]) if ok.sum() > 5 else 1.0)
score = np.array(score)
best = cand[int(np.argmin(score))]
print(f"\nbest-fit spacing on the assumed scale: s = alpha*g = {best:.3f} "
      f"(mean |frac| = {score.min():.3f})")
for g in (2, 4, 6, 8, 12, 16):
    print(f"    if the true degeneracy step g = {g:2d}  ->  alpha = {best/g:.3f}  "
          f"->  c_tg_true = {cal_g.c_tg/(best/g)*1e3:.3f} mF/m^2 "
          f"(prior {cal_g.c_tg*1e3:.3f}), n scale x{1/(best/g):.3f}")

# ---- fit individual fan lines: group minima by nu_assumed/best --------------
mult = np.round(nu_ass / best).astype(int)
print(f"\nfan lines found (grouped by multiple of s):")
print(f"  {'m':>4} {'npts':>5} {'nu_assumed(fit)':>16} {'ratio to |m|=1':>15}")
slopes = {}
for m in sorted(set(mult)):
    if m == 0:
        continue
    sel = mult == m
    if sel.sum() < 3:
        continue
    # fit n_assumed = slope * B through the origin
    sl = np.sum(pts[sel, 0] * pts[sel, 1]) / np.sum(pts[sel, 0] ** 2)
    nu_fit = sl * cst.h / cst.e
    slopes[m] = nu_fit
    print(f"  {m:>4} {int(sel.sum()):>5} {nu_fit:>16.3f} {nu_fit/best:>15.3f}")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
ax[0].plot(cand, score, lw=1.2)
ax[0].axvline(best, ls="--", c="r", label=f"best s = {best:.2f}")
ax[0].set_xlabel("trial spacing s = alpha*g  (nu on the assumed scale)")
ax[0].set_ylabel("mean |fractional part|"); ax[0].legend(fontsize=8)
ax[0].set_title("which spacing explains the minima?")

ax[1].scatter(pts[:, 0], pts[:, 1] * 1e-16, c=mult, cmap="tab20", s=18)
bb = np.linspace(1.4, B.max(), 20)
for m, nu_fit in slopes.items():
    ax[1].plot(bb, nu_fit * cst.e * bb / cst.h * 1e-16, "k-", lw=0.6, alpha=0.5)
ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("n_assumed (1e12 cm^-2)")
ax[1].set_title("Rxx minima and fitted fan lines")

ax[2].hist(nu_ass[np.abs(nu_ass) > 0.7 * best], bins=60)
for k in range(-12, 13):
    if k:
        ax[2].axvline(k * best, ls=":", c="r", lw=0.7)
ax[2].set_xlabel("nu on the assumed scale"); ax[2].set_ylabel("count")
ax[2].set_title(f"minima cluster at multiples of {best:.2f}")
fig.tight_layout()
out = here / "hera_scratch" / "a6_llcal.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
