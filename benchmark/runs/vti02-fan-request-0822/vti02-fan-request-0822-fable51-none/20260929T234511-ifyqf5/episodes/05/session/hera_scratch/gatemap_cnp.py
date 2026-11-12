"""Gatemap read (run 5): re-form R(Vtg, Vbg) from TSV, extract CNP ridge(s) per row, fit slope/intercept,
compare to the geometry prior. Works on a partial run (fan_grids keeps complete rows)."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from hera.analysis import fan_grids, resistance_grids
from sharpelab_nb.gates import stack_capacitance, calc_nD

rid = int(sys.argv[1]) if len(sys.argv) > 1 else 5
g = fan_grids(f"data/{rid}")
rg = resistance_grids(g)
R = np.abs(rg.R["sr1"])          # (nrows, nfast)
Vbg = g.slow                     # per row
Vtg = np.asarray(g.meta["fast_setpoints"][0] if isinstance(g.meta["fast_setpoints"][0], list) else g.meta["fast_setpoints"])
print(f"run {rid}: {g.nrows} complete rows x {g.nfast} fast; R {R.min():.0f}-{R.max():.0f} Ohm; Vbg {Vbg[0]:+.2f}..{Vbg[-1]:+.2f}")

c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3)])
print(f"geometry prior: c_bg/c_tg = {c_bg/c_tg:.3f} -> CNP slope dVtg/dVbg = {-c_bg/c_tg:.3f}")

# per-row peaks along Vtg (smoothed), up to two, excluding edge-clipped maxima
ridges = {"A": [], "B": []}
rows_used = []
for i in range(g.nrows):
    r = gaussian_filter1d(R[i], 1.0)
    pk, props = find_peaks(r, prominence=0.08 * r.max())
    pk = [p for p in pk if 1 < p < g.nfast - 2]
    if not pk:
        continue
    pk = sorted(pk, key=lambda p: -r[p])[:2]
    pk = sorted(pk)                  # lower Vtg first
    rows_used.append(i)
    for name, p in zip(("A", "B"), pk):
        ridges[name].append((Vbg[i], Vtg[p], r[p]))

fits = {}
for name, pts in ridges.items():
    if len(pts) < 4:
        print(f"ridge {name}: {len(pts)} rows — too few"); continue
    pts = np.array(pts)
    x, y = pts[:, 0], pts[:, 1]
    keep = np.ones(len(x), bool)
    for _ in range(3):
        cf = np.polyfit(x[keep], y[keep], 1)
        res = y - np.polyval(cf, x)
        sig = max(np.std(res[keep]), 0.01)
        keep = np.abs(res) < 2.5 * sig
    cf = np.polyfit(x[keep], y[keep], 1)
    res = (y - np.polyval(cf, x))[keep]
    fits[name] = cf
    n0, D0 = calc_nD(cf[1], 0.0, c_tg, c_bg)
    print(f"ridge {name}: {keep.sum()}/{len(x)} rows, Vtg = {cf[0]:+.3f}*Vbg {cf[1]:+.3f} V, rms resid {np.std(res)*1e3:.1f} mV, "
          f"Vbg range {x[keep].min():+.2f}..{x[keep].max():+.2f}; c_bg/c_tg = {-cf[0]:.3f}; n_offset(prior scale) = {-n0:+.3f}e12; "
          f"peak R {pts[:,2].min():.0f}-{pts[:,2].max():.0f} Ohm")

fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
m = ax[0].pcolormesh(Vtg, Vbg, R, shading="nearest", cmap="viridis", vmin=0, vmax=np.percentile(R, 99))
fig.colorbar(m, ax=ax[0], label="|Rxx| B_1-B_2 (Ohm)")
ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)"); ax[0].set_title(f"run {rid} gatemap, B = 0, T = 1.17 K")
for name, pts in ridges.items():
    if pts:
        pts = np.array(pts); ax[0].plot(pts[:, 1], pts[:, 0], "w.", ms=3)
    if name in fits:
        xx = np.array([Vbg.min(), Vbg.max()]); ax[0].plot(np.polyval(fits[name], xx), xx, "r--" if name == "A" else "m--", lw=1, label=f"ridge {name}: slope {fits[name][0]:+.2f}")
# D = 0 line from prior: c_tg Vtg = c_bg Vbg
xx = np.array([Vbg.min(), Vbg.max()]); ax[0].plot(c_bg / c_tg * xx, xx, "c:", lw=1, label="D = 0 (prior)")
ax[0].set_xlim(Vtg.min(), Vtg.max()); ax[0].set_ylim(Vbg.min(), Vbg.max()); ax[0].legend(fontsize=8, loc="upper right")
# log view
m2 = ax[1].pcolormesh(Vtg, Vbg, np.log10(R), shading="nearest", cmap="magma")
fig.colorbar(m2, ax=ax[1], label="log10 |Rxx|")
ax[1].set_xlabel("V_tg (V)"); ax[1].set_ylabel("V_bg (V)"); ax[1].set_title("log10 R")
fig.tight_layout(); fig.savefig(f"hera_scratch/gatemap_run{rid}.png", dpi=110)
print(f"saved hera_scratch/gatemap_run{rid}.png")
