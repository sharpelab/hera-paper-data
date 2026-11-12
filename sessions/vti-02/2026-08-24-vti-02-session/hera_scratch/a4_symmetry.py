"""Robust R_CNP(D) and the inversion-symmetry test.

Improvements over a4's first pass:
  * parabolic sub-step interpolation of the CNP peak position/height
  * the CNP-line fit uses only rows where the ridge is UNAMBIGUOUS (high |D|,
    tall narrow peak), then extrapolates into the low-|D| region
  * propagates the fitted-slope uncertainty into the location of D = 0
  * explicit +D vs -D comparison at matched |D|
  * flags rows where the neutrality region is double-peaked
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration

here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / "3")
fan = fan_grids(r)
rg = resistance_grids(fan)
Vtg = fan.grid("k_2400_tg_volt")
Vbg = fan.slow
Rxx = np.abs(rg.R["sr1"])
nrows, nfast = Rxx.shape
dvtg = Vtg[0, 1] - Vtg[0, 0]

# ---- per-row peak: parabolic interpolation on the 3 points around argmax ----
kpk = np.argmax(Rxx, axis=1)
Vpk = np.empty(nrows)
Rpk = np.empty(nrows)
for i, k in enumerate(kpk):
    if 0 < k < nfast - 1:
        y0, y1, y2 = Rxx[i, k - 1], Rxx[i, k], Rxx[i, k + 1]
        den = (y0 - 2 * y1 + y2)
        d = 0.5 * (y0 - y2) / den if den != 0 else 0.0
        d = np.clip(d, -1, 1)
        Vpk[i] = Vtg[i, k] + d * dvtg
        Rpk[i] = y1 - 0.25 * (y0 - y2) * d
    else:
        Vpk[i], Rpk[i] = Vtg[i, k], Rxx[i, k]
edge = (kpk <= 1) | (kpk >= nfast - 2)

# ---- double-peak flag: a second local max within 80% of the main one --------
def n_strong_peaks(row, frac=0.80):
    m = row.max()
    pk = [j for j in range(1, nfast - 1)
          if row[j] > row[j - 1] and row[j] >= row[j + 1] and row[j] > frac * m]
    return len(pk)

npk = np.array([n_strong_peaks(Rxx[i]) for i in range(nrows)])

# ---- CNP-line fit on the UNAMBIGUOUS rows only ------------------------------
contrast = Rpk / np.median(Rxx, axis=1)
good = (~edge) & (npk == 1) & (contrast > 1.6)
print(f"rows total {nrows} | interior {(~edge).sum()} | single-peaked {(npk == 1).sum()} | "
      f"used for the line fit {good.sum()}")
print(f"rows flagged DOUBLE-peaked: {list(np.round(Vbg[npk > 1], 3))}")

A, cov = np.polyfit(Vbg[good], Vpk[good], 1, cov=True)
slope, icept = A
sl_err = np.sqrt(cov[0, 0])
ratio = -1.0 / slope                                   # c_tg / c_bg
ratio_err = abs(sl_err / slope ** 2) * ratio ** 0 / abs(slope) * 0 + abs(sl_err) / slope ** 2
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
print(f"\nCNP line (strong rows): V_tg = {slope:+.5f}(+/-{sl_err:.5f})*V_bg {icept:+.5f}")
print(f"  measured c_tg/c_bg = {ratio:.4f} +/- {ratio_err:.4f}   "
      f"(geometry prior {cal_g.c_tg / cal_g.c_bg:.4f})")

cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / ratio)
D = cal_s.displacement_field(Vpk, Vbg) * 1e-9
use = ~edge
o = np.argsort(D[use])
Dv, Rv, npv = D[use][o], Rpk[use][o], npk[use][o]

# where is D = 0 on the CNP line, and how uncertain is it?
Vtg_D0 = icept / (1.0 - slope * ratio) if abs(1.0 - slope * ratio) > 1e-9 else np.nan
# sensitivity of D_min location to the fitted ratio: recompute D with ratio +/- err
for rr, tag in ((ratio - ratio_err, "-1sig"), (ratio + ratio_err, "+1sig")):
    c2 = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / rr)
    D2 = c2.displacement_field(Vpk, Vbg) * 1e-9
    print(f"  D of the R_CNP argmin with ratio {tag}: {D2[use][np.argmin(Rpk[use])]:+.4f} V/nm")

kmin = int(np.argmin(Rv))
sel = np.abs(Dv - Dv[kmin]) < 0.10
q = np.polyfit(Dv[sel], np.log10(Rv[sel]), 2)
D_min = -q[1] / (2 * q[0])
print(f"\nR_CNP min: argmin at D = {Dv[kmin]:+.4f} V/nm (R = {Rv[kmin]:.0f} ohm); "
      f"parabola on log10 R over {sel.sum()} pts -> D_min = {D_min:+.4f} V/nm")
print(f"R_CNP range {Rv.min():.0f} .. {Rv.max():.0f} ohm  ({Rv.max()/Rv.min():.1f}x)")
print(f"D covered: {Dv.min():+.4f} .. {Dv.max():+.4f} V/nm "
      f"(-D lever arm is {abs(Dv.min())/Dv.max():.2f} of +D)")

# ---- +D vs -D at matched |D| about the fitted minimum -----------------------
print(f"\nsymmetry about D_min = {D_min:+.4f} V/nm:")
dd = Dv - D_min
neg = dd < 0
print(f"  {'|dD|':>7}  {'R(-D)':>8}  {'R(+D)':>8}   ratio")
for target in (0.02, 0.04, 0.06, 0.08):
    if (-dd[neg]).max() < target:
        continue
    rn = np.interp(target, -dd[neg][::-1], Rv[neg][::-1])
    rp = np.interp(target, dd[~neg], Rv[~neg])
    print(f"  {target:7.3f}  {rn:8.0f}  {rp:8.0f}   {rp/rn:5.2f}")
print(f"  (per-point noise ~3 %; anything within ~1.1 is consistent with symmetric)")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(Dv, Rv, "o-", ms=5, lw=1.2, color="C0")
m2 = npv > 1
ax[0].plot(Dv[m2], Rv[m2], "s", ms=9, mfc="none", mec="r", label="double-peaked row")
ax[0].axvline(0, ls="--", c="k", lw=1.0, label="D = 0")
ax[0].axvline(D_min, ls=":", c="r", lw=1.2, label=f"R_CNP min {D_min:+.3f} V/nm")
ax[0].set_yscale("log"); ax[0].set_xlabel("D/eps0 (V/nm)"); ax[0].set_ylabel("R_CNP (ohm)")
ax[0].set_title("R at neutrality vs D  (run 3, B=0, T=1.17 K)")
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3, which="both")

ax[1].plot(np.abs(dd[neg]), Rv[neg], "o-", ms=5, label="D < D_min")
ax[1].plot(dd[~neg], Rv[~neg], "s-", ms=5, label="D > D_min")
ax[1].set_yscale("log"); ax[1].set_xlim(0, 0.10)
ax[1].set_xlabel("|D - D_min|  (V/nm)"); ax[1].set_ylabel("R_CNP (ohm)")
ax[1].set_title("folded about the minimum — inversion-symmetry test")
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, which="both")
fig.tight_layout()
out = here / "hera_scratch" / "a4_symmetry.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
np.savez(here / "hera_scratch" / "a4_symmetry.npz", D=Dv, R=Rv, npk=npv,
         ratio=ratio, ratio_err=ratio_err, D_min=D_min, slope=slope, icept=icept)
