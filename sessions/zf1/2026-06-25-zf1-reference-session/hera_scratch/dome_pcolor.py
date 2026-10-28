"""Figure 1 dome map -> pcolormesh in (n,D). Reconstructs the regular grid from
the flattened boustrophedon multisweep (variable-length sanitized rows) by binning
each measured point to its grid cell. Works on partial OR complete runs.
Usage:  menv python hera_scratch/dome_pcolor.py [run_id]   (default 3)"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration

run_id = sys.argv[1] if len(sys.argv) > 1 else "3"
g = open_run(f"data/{run_id}")

# --- calibration: USE EXACTLY (handoff §1) ---
N_OFF = -0.362e11 * 1e4
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=N_OFF)

# --- planned setpoints (first occurrence) -> (n, D) ---
vtg = g.col_at(g.col_indices("k_tg_volt")[0])
vbg = g.col_at(g.col_indices("k_bg_volt")[0])
n_m2, D_Vm = cal.n_D(vtg, vbg)
n11 = n_m2 / 1e4 / 1e11           # 1e11 cm^-2
D = D_Vm / 1e9                    # V/nm

# --- 4T Rxx (30-31): R = (X / gain) / I_bias ---
I_bias = 1e-9
R = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100) / I_bias

# --- regenerate the theoretical grid (must match the measure cell) ---
DN, DD = 0.03, 0.0025
n_grid = np.sort(np.round(np.arange(-1.0, -7.0001, -DN), 5))          # -7..-1 (201)
D_grid = np.sort(np.round(np.arange(-0.40, -0.69001, -DD), 5))        # -0.69..-0.40 (117)

# --- bin each measured point to its (D-row, n-col); clipped cells stay NaN ---
ni = np.round((n11 - n_grid[0]) / DN).astype(int)
di = np.round((D - D_grid[0]) / DD).astype(int)
Z = np.full((len(D_grid), len(n_grid)), np.nan)
ok = (ni >= 0) & (ni < len(n_grid)) & (di >= 0) & (di < len(D_grid))
Z[di[ok], ni[ok]] = R[ok]

# --- cell edges for pcolormesh (centers -> edges) ---
def edges(c):
    c = np.asarray(c, float)
    e = np.empty(len(c) + 1)
    e[1:-1] = 0.5 * (c[:-1] + c[1:])
    e[0] = c[0] - 0.5 * (c[1] - c[0])
    e[-1] = c[-1] + 0.5 * (c[-1] - c[-2])
    return e
Xe, Ye = edges(n_grid), edges(D_grid)

# --- plot ---
fig, ax = plt.subplots(figsize=(8.5, 6))
pc = ax.pcolormesh(Xe, Ye, Z, cmap="viridis", vmin=0, vmax=50, shading="flat")
cb = plt.colorbar(pc, ax=ax, extend="max")
cb.set_label(r"$R_{xx}$ 4T (30-31)  ($\Omega$)   [>1 k$\Omega$ rails @0.1 mV near CNP]")

# 2 / 5 Ohm dome contours on the filled cells
Xc, Yc = np.meshgrid(n_grid, D_grid)
Zm = np.ma.masked_invalid(Z)
if np.isfinite(Z).sum() > 50:
    try:
        cs = ax.contour(Xc, Yc, Zm, levels=[2, 5], colors=["white", "cyan"], linewidths=1.1)
        ax.clabel(cs, fmt="%g Ω", fontsize=8)
    except Exception as e:
        print("contour skipped:", e)

ax.plot(-5.0, -0.64, "r*", ms=15, label="optimum n=-5.0, D=-0.64")
ax.set_xlabel(r"$n$  ($10^{11}$ cm$^{-2}$)")
ax.set_ylabel(r"$D$  (V/nm)")
filled = int(np.isfinite(Z).sum())
ax.set_title(f"Fig 1 — SC dome R$_{{xx}}$(n,D) at B$_{{eff0}}$  (run {run_id}; {filled}/{Z.size} cells)")
ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
out = "hera_scratch/dome_pcolor.png"
plt.savefig(out, dpi=140)
print(f"saved {out}: filled {filled}/{Z.size} cells; "
      f"R range {np.nanmin(Z):.2f}..{np.nanmax(Z):.2f} Ω; "
      f"grid {len(n_grid)} n x {len(D_grid)} D")
