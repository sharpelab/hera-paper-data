"""Where does the Landau sequence START? The decisive stacking test.

Spacing alone is 4 for every candidate. What separates them is the FIRST gap:
  ABCA tetralayer : zero-energy LL is 4 orbital x 4 spin/valley = 16 states,
                    spanning nu = -8..+8  ->  first gaps at |nu| = 8, then 12, 16...
                    NO gap at |nu| = 4.
  ABAB tetralayer : two bilayer-like sets, each an 8-fold zero LL at a DIFFERENT
                    energy  ->  a gap opens at |nu| = 4 when the first set fills,
                    then 8, 12, ...
  (bilayer would be 4, 8, 12...; ABC trilayer 6, 10, 14...)

So: is there a real Rxx minimum at |nu| = 4, and how does it compare with |nu| = 8?
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
_s = [i for i, c in enumerate(fan.cols) if c == "sr1_X"][0]
Vxx = fan.data[:, _s].reshape(nB, nfast)
Rxx = np.where(np.abs(Vxx) > 0.95e-3, np.nan, Rxx)

Vtg = fan.grid("k_2400_tg_volt")[0]
RATIO = 1.2737
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / RATIO)
n_ass = cal_s.density(Vtg, RATIO * Vtg)

ALPHA = 1.166                      # from a6: assumed/true, for degeneracy step g = 4
n_true = n_ass / ALPHA
print(f"absolute calibration: n_true = n_assumed / {ALPHA:.3f}; "
      f"c_tg_true = {cal_g.c_tg/ALPHA*1e3:.3f} mF/m^2 (prior {cal_g.c_tg*1e3:.3f})")
print(f"n_true range {n_true.min()*1e-16:+.3f} .. {n_true.max()*1e-16:+.3f} e12 cm^-2\n")

# ---- Rxx vs nu at the highest fields, both carrier signs --------------------
print("Rxx (ohm) at integer filling factors, averaged over the top field rows:")
hi = B >= 3.0
print(f"  using {hi.sum()} rows with B >= 3.0 T ({B[hi].min():.2f}-{B[hi].max():.2f} T)")
targets = [2, 4, 6, 8, 10, 12, 16, 20]
print(f"  {'|nu|':>5} {'R(electron)':>13} {'R(hole)':>12}   note")
prof = {}
for nu0 in targets:
    vals = {"e": [], "h": []}
    for i in np.where(hi)[0]:
        nu_row = n_true * cst.h / (cst.e * B[i])
        for side, sgn in (("e", +1), ("h", -1)):
            m = np.abs(nu_row - sgn * nu0) < 1.0
            if m.sum() and np.isfinite(Rxx[i][m]).any():
                vals[side].append(np.nanmin(Rxx[i][m]))
    re_ = np.median(vals["e"]) if vals["e"] else np.nan
    rh_ = np.median(vals["h"]) if vals["h"] else np.nan
    prof[nu0] = (re_, rh_)
    note = ""
    if nu0 == 4:
        note = "<- ABAB predicts a gap here; ABCA predicts NONE"
    if nu0 == 8:
        note = "<- ABCA's FIRST gap"
    print(f"  {nu0:>5} {re_:>13.1f} {rh_:>12.1f}   {note}")

# contrast: a real gap should sit well below its neighbours
print("\ncontrast of each candidate gap vs the mean of its neighbours (lower = deeper gap):")
for nu0 in (4, 8, 12, 16):
    for si, side in ((0, "electron"), (1, "hole")):
        nb = [prof[k][si] for k in (nu0 - 2, nu0 + 2) if k in prof and np.isfinite(prof[k][si])]
        if nb and np.isfinite(prof[nu0][si]):
            print(f"  nu={nu0:>2} {side:>8}: R={prof[nu0][si]:8.1f}  "
                  f"neighbours={np.mean(nb):8.1f}  ratio={prof[nu0][si]/np.mean(nb):.3f}")

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
for i in np.where(B >= 2.5)[0][::3]:
    nu_row = n_true * cst.h / (cst.e * B[i])
    ax[0].plot(nu_row, Rxx[i], lw=1.0, alpha=0.85, label=f"{B[i]:.1f} T")
ax[0].set_yscale("log"); ax[0].set_xlim(-20, 30)
for k in (-16, -12, -8, -4, 4, 8, 12, 16, 20):
    ax[0].axvline(k, ls=":", c="0.6", lw=0.8)
for k in (-8, 8):
    ax[0].axvline(k, ls="--", c="b", lw=1.1)
for k in (-4, 4):
    ax[0].axvline(k, ls="--", c="r", lw=1.1)
ax[0].set_xlabel("filling factor nu (calibrated)"); ax[0].set_ylabel("Rxx (ohm)")
ax[0].set_title("Rxx vs nu — red = |nu|=4 (ABAB), blue = |nu|=8 (ABCA first gap)")
ax[0].legend(fontsize=7, ncol=2)

ks = sorted(prof)
ax[1].plot(ks, [prof[k][0] for k in ks], "o-", label="electron")
ax[1].plot(ks, [prof[k][1] for k in ks], "s-", label="hole")
ax[1].set_yscale("log"); ax[1].set_xlabel("|nu|"); ax[1].set_ylabel("median Rxx minimum (ohm)")
ax[1].axvline(4, ls="--", c="r"); ax[1].axvline(8, ls="--", c="b")
ax[1].set_title("depth of each candidate gap"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
fig.tight_layout()
out = here / "hera_scratch" / "a7_nu.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
