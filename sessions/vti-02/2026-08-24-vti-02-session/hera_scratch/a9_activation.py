"""Activation gap Delta(D) from the temperature ladder (runs 6..12).

Each run is a 245-point co-swept multisweep: 5 perpendicular V_bg offsets x 49 points
along the measured CNP line. R_CNP at each point along the line is the MAXIMUM over the
5 offsets — that is what makes the measurement robust to the fitted line drifting by a
few mV, or to the CNP itself moving as the sample warms.

Then, at each D, fit  ln R_CNP = ln R0 + Delta/(2 k_B T)  over the temperatures where the
sample is thermally activated. Delta is in meV and is INDEPENDENT of the unknown Hall-bar
geometry factor, because it comes from a ratio.

  ABCA (inversion symmetric): Delta grows with |D| and extrapolates to ~0 at D = 0.
  ABCB (no inversion)       : Delta stays FINITE at D = 0.
  ABAB                      : no activated gap at all.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import open_run, GateCalibration

here = Path(__file__).resolve().parent.parent
RIDS = [int(x) for x in sys.argv[1:]] or list(range(6, 13))
RATIO = 1.2737
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / RATIO)
NOFF = 5

curves = []       # (T, D_array, Rcnp_array)
for rid in RIDS:
    p = here / "data" / str(rid)
    if not (p / "data.tsv.gz").exists() and not (p / "data.tsv").exists():
        print(f"run {rid}: not on disk yet, skipping")
        continue
    r = open_run(p)
    # COMPLETENESS GUARD: the path is offset0's 49 pts, then offset1's 49, ... A partial
    # run reshaped to (5, npts) silently interleaves different offsets and yields garbage
    # (caught doing exactly that on a still-writing run 6). Only whole runs are used.
    _sp = r.meta.get("setpoints")
    _exp = len(_sp[0]) if isinstance(_sp, list) and _sp and isinstance(_sp[0], list) else None
    if _exp is not None and r.rows != _exp:
        print(f"run {rid}: INCOMPLETE ({r.rows} of {_exp} pts) — skipping, "
              f"a partial reshape would scramble the offsets")
        continue
    if r.interrupted:
        print(f"run {rid}: marked interrupted — skipping")
        continue
    vtg = r.col("k_2400_tg_volt")
    vbg = r.col("k_2400_bg_volt")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    Vxx = r.col("sr1_X")
    T = r.col("T_sample")
    npts = len(vtg) // NOFF
    assert npts * NOFF == len(vtg), f"run {rid}: {len(vtg)} not divisible by {NOFF} offsets"
    R = (Vxx / I)[: npts * NOFF].reshape(NOFF, npts)
    vtg_g = vtg[: npts * NOFF].reshape(NOFF, npts)
    vbg_g = vbg[: npts * NOFF].reshape(NOFF, npts)
    k = np.nanargmax(np.abs(R), axis=0)                 # best offset per along-line point
    Rc = np.abs(R)[k, np.arange(npts)]
    D = cal_s.displacement_field(vtg_g[0], vbg_g[k, np.arange(npts)]) * 1e-9
    Tm = float(np.nanmean(T))
    curves.append((Tm, D, Rc, rid))
    print(f"run {rid}: T = {Tm:6.3f} K   R_CNP {Rc.min():7.1f} .. {Rc.max():8.1f} ohm   "
          f"D {D.min():+.3f}..{D.max():+.3f} V/nm")

if len(curves) < 3:
    print("\nneed at least 3 temperatures for an Arrhenius fit — stopping")
    raise SystemExit

curves.sort(key=lambda c: c[0])
Ts = np.array([c[0] for c in curves])
Dgrid = curves[0][1]
Rmat = np.vstack([np.interp(Dgrid, c[1], c[2]) for c in curves])   # (nT, nD)
print(f"\ntemperatures: {np.round(Ts, 2)} K")

# ---- Arrhenius fit per D ----------------------------------------------------
# Use only T where the sample is genuinely activated. The rig's ELECTRON temperature is
# ~8 K, so points below that carry no independent information and are excluded.
fitm = Ts >= 7.0
print(f"fitting over T = {np.round(Ts[fitm],2)} K "
      f"(below ~8 K the electron temperature floors out, so those points are excluded)")
inv2kT = 1.0 / (2 * cst.k * Ts[fitm]) * cst.e * 1e-3      # per meV
gaps, gerr = [], []
for j in range(len(Dgrid)):
    y = np.log(np.maximum(Rmat[fitm, j], 1e-3))
    A = np.vstack([inv2kT, np.ones_like(inv2kT)]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    dof = max(len(y) - 2, 1)
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(A.T @ A)
    gaps.append(coef[0]); gerr.append(np.sqrt(cov[0, 0]))
gaps, gerr = np.array(gaps), np.array(gerr)

print(f"\n{'D/eps0':>8} {'Delta(meV)':>11} {'+/-':>7}   R(base)  R(hottest)")
for j in range(0, len(Dgrid), max(1, len(Dgrid) // 16)):
    print(f"{Dgrid[j]:+8.3f} {gaps[j]:11.3f} {gerr[j]:7.3f}   {Rmat[0,j]:8.1f} {Rmat[-1,j]:9.1f}")

k0 = int(np.argmin(np.abs(Dgrid)))
print(f"\nDelta at D = 0 ({Dgrid[k0]:+.3f} V/nm): {gaps[k0]:.3f} +/- {gerr[k0]:.3f} meV")
for dt in (0.10, 0.20, 0.28):
    j = int(np.argmin(np.abs(Dgrid - dt)))
    print(f"Delta at D = {Dgrid[j]:+.3f} V/nm: {gaps[j]:.3f} +/- {gerr[j]:.3f} meV")
pos = Dgrid > 0.05
if pos.sum() > 3:
    sl, ic = np.polyfit(Dgrid[pos], gaps[pos], 1)
    print(f"\nlinear fit of Delta vs D over D > 0.05: slope {sl:.1f} meV per V/nm, "
          f"intercept {ic:+.3f} meV")
    print(f"  ABCA requires the intercept ~0 (gapless at D=0); ABCB requires it clearly > 0")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
for (Tm, D, Rc, rid) in curves:
    ax[0].plot(D, Rc, lw=1.1, label=f"{Tm:.1f} K")
ax[0].set_yscale("log"); ax[0].set_xlabel("D/eps0 (V/nm)"); ax[0].set_ylabel("R_CNP (ohm)")
ax[0].set_title("R at neutrality vs D, per temperature"); ax[0].legend(fontsize=7)

for dt in (0.0, 0.10, 0.20, 0.28):
    j = int(np.argmin(np.abs(Dgrid - dt)))
    ax[1].plot(1 / Ts, Rmat[:, j], "o-", ms=5, label=f"D={Dgrid[j]:+.2f}")
ax[1].set_yscale("log"); ax[1].set_xlabel("1/T (1/K)"); ax[1].set_ylabel("R_CNP (ohm)")
ax[1].set_title("Arrhenius"); ax[1].legend(fontsize=7); ax[1].grid(alpha=0.3)

ax[2].errorbar(Dgrid, gaps, yerr=gerr, fmt="o-", ms=4, lw=1.0, capsize=2)
ax[2].axhline(0, ls="--", c="k", lw=0.9); ax[2].axvline(0, ls="--", c="k", lw=0.9)
ax[2].set_xlabel("D/eps0 (V/nm)"); ax[2].set_ylabel("activation gap Delta (meV)")
ax[2].set_title("Delta(D) — ABCA: ~0 at D=0, growing with |D|")
ax[2].grid(alpha=0.3)
fig.tight_layout()
out = here / "hera_scratch" / "a9_activation.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
np.savez(here / "hera_scratch" / "a9_activation.npz",
         D=Dgrid, gap=gaps, gerr=gerr, T=Ts, R=Rmat)
