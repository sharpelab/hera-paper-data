"""Gate map read: re-form the fan, extract R_CNP(D) along the CNP line, measure the
CNP-line slope (session gate calibration), and test where the R_CNP minimum sits.

R_CNP(D) is the primary ABAB / ABCA / ABCB discriminator:
  ABAB  - band-overlapped semimetal, stays conducting, weak D dependence
  ABCA  - inversion symmetric, gap opens with |D| -> R_CNP MINIMUM exactly at D = 0
  ABCB  - no inversion symmetry, built-in gap -> R_CNP minimum DISPLACED from D = 0
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration

rid = int(sys.argv[1]) if len(sys.argv) > 1 else 3
here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / str(rid))
print(f"run {rid}: {r.meta['type']}  {r.recipe}  rows={r.rows}  interrupted={r.interrupted}")

fan = fan_grids(r)
rg = resistance_grids(fan)
Vtg = fan.grid("k_2400_tg_volt")          # (nrows, nfast)
Vbg = fan.slow                            # (nrows,)
Rxx = np.abs(rg.R["sr1"])                 # (nrows, nfast), signed -> magnitude
Ig = rg.current
print(f"grid: {fan.nrows} rows x {fan.nfast} fast   Rxx {Rxx.min():.1f} .. {Rxx.max():.1f} ohm")
print(f"current: {Ig.min()*1e9:.3f} .. {Ig.max()*1e9:.3f} nA")

cal = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)

# --- per-row CNP: the Rxx maximum along the fast (V_tg) axis -----------------
kpk = np.argmax(Rxx, axis=1)
Rpk = Rxx[np.arange(fan.nrows), kpk]
Vtg_pk = Vtg[np.arange(fan.nrows), kpk]
# rows whose peak sits on a boundary never actually crossed the CNP
edge = (kpk <= 1) | (kpk >= fan.nfast - 2)
print(f"\nrows with an interior CNP peak: {(~edge).sum()} of {fan.nrows} "
      f"(boundary rows excluded: {edge.sum()})")

# --- measured CNP-line slope = the session gate calibration ------------------
A = np.polyfit(Vbg[~edge], Vtg_pk[~edge], 1)
slope_meas = A[0]                       # dV_tg/dV_bg along the CNP line
ratio_meas = -1.0 / slope_meas          # = c_tg / c_bg
ratio_geom = cal.c_tg / cal.c_bg
print(f"CNP line fit : V_tg = {A[0]:+.4f}*V_bg {A[1]:+.4f}")
print(f"  measured c_tg/c_bg = {ratio_meas:.4f}   geometry prior = {ratio_geom:.4f}   "
      f"({100*(ratio_meas/ratio_geom-1):+.1f} %)")

# absolute scale still from geometry; only the RATIO is measured here
c_bg_cal = cal.c_tg / ratio_meas
cal_s = GateCalibration(c_tg=cal.c_tg, c_bg=c_bg_cal)
D_pk = cal_s.displacement_field(Vtg_pk, Vbg) * 1e-9        # V/nm
n_pk = cal_s.density(Vtg_pk, Vbg) * 1e-16                  # 1e12 cm^-2 (should be ~const)
print(f"  n along the fitted CNP line: {n_pk.mean():+.4f} +/- {n_pk.std():.4f} e12 cm^-2 "
      f"(this is n_offset)")

ok = ~edge
order = np.argsort(D_pk[ok])
Dv, Rv = D_pk[ok][order], Rpk[ok][order]
print(f"\nD range covered along the CNP line: {Dv.min():+.4f} .. {Dv.max():+.4f} V/nm")
print(f"R_CNP range                       : {Rv.min():.0f} .. {Rv.max():.0f} ohm "
      f"(ratio {Rv.max()/Rv.min():.1f}x)")

kmin = int(np.argmin(Rv))
print(f"\nR_CNP MINIMUM at D/eps0 = {Dv[kmin]:+.4f} V/nm  (R = {Rv[kmin]:.0f} ohm)")
print("   ABCA (inversion symmetric) requires the minimum at D = 0;")
print("   ABCB (no inversion) puts it at D != 0;")
print("   ABAB would show little D dependence at all.")

# quadratic fit near the minimum -> sub-step estimate of D_min
sel = np.abs(Dv - Dv[kmin]) < 0.12
if sel.sum() >= 4:
    q = np.polyfit(Dv[sel], np.log10(Rv[sel]), 2)
    D_min_fit = -q[1] / (2 * q[0])
    print(f"   quadratic fit on log10(R) near the minimum: D_min = {D_min_fit:+.4f} V/nm "
          f"({sel.sum()} pts)")

for tag, lo, hi in (("+D", 0.0, 1.0), ("-D", -1.0, 0.0)):
    m = (Dv >= lo) & (Dv < hi) if tag == "+D" else (Dv > lo) & (Dv <= hi)
    if m.sum():
        print(f"   {tag}: {m.sum()} pts, |D| up to {np.abs(Dv[m]).max():.3f} V/nm, "
              f"R_CNP up to {Rv[m].max():.0f} ohm")

# --- figures ----------------------------------------------------------------
fig = plt.figure(figsize=(12, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])

ax = fig.add_subplot(gs[0, 0])
pc = ax.pcolormesh(Vtg, np.tile(Vbg[:, None], (1, fan.nfast)), np.log10(Rxx),
                   shading="nearest", cmap="magma")
ax.plot(Vtg_pk[~edge], Vbg[~edge], "c.-", ms=4, lw=0.8, label="CNP (Rxx max)")
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)")
ax.set_title(f"run {rid} — log10 Rxx (ohm),  B = 0, T = base")
fig.colorbar(pc, ax=ax, label="log10 Rxx"); ax.legend(fontsize=7)

ax = fig.add_subplot(gs[0, 1])
nn = cal_s.density(Vtg, np.tile(Vbg[:, None], (1, fan.nfast))) * 1e-16
DD = cal_s.displacement_field(Vtg, np.tile(Vbg[:, None], (1, fan.nfast))) * 1e-9
pc = ax.pcolormesh(nn, DD, np.log10(Rxx), shading="nearest", cmap="magma")
ax.plot(n_pk[~edge], D_pk[~edge], "c.-", ms=4, lw=0.8)
ax.set_xlabel("n  (1e12 cm^-2)"); ax.set_ylabel("D/eps0  (V/nm)")
ax.set_title("same map in (n, D)")
fig.colorbar(pc, ax=ax, label="log10 Rxx")

ax = fig.add_subplot(gs[1, :])
ax.plot(Dv, Rv, "o-", ms=5, lw=1.2)
ax.axvline(0.0, ls="--", c="k", lw=1.0, label="D = 0")
ax.axvline(Dv[kmin], ls=":", c="r", lw=1.2, label=f"R_CNP min at {Dv[kmin]:+.3f} V/nm")
ax.set_yscale("log")
ax.set_xlabel("D/eps0  (V/nm)  along the CNP line")
ax.set_ylabel("R_CNP  (ohm)")
ax.set_title("R at charge neutrality vs displacement field — the stacking discriminator")
ax.legend(fontsize=8); ax.grid(alpha=0.3, which="both")

fig.tight_layout()
out = here / "hera_scratch" / f"a3_gatemap_run{rid}.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")

np.savez(here / "hera_scratch" / f"a3_gatemap_run{rid}.npz",
         D=Dv, R=Rv, Vtg_pk=Vtg_pk, Vbg=Vbg, edge=edge,
         ratio_meas=ratio_meas, n_offset=n_pk.mean())
