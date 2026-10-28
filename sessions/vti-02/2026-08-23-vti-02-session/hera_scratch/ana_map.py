"""Scratch analysis of a gate map run: re-form via fan_grids/resistance_grids, plot R(Vtg,Vbg), find ridge.
usage: menv python hera_scratch/ana_map.py <run_id>
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, fan_grids, resistance_grids
from sharpelab_nb.gates import stack_capacitance, calc_nD

rid = int(sys.argv[1])
r = open_run(f"data/{rid}")
print(summarize_run(r))
fan = fan_grids(r)
rg = resistance_grids(fan)
R = np.abs(rg.R["sr1"]); I = rg.current
vb = fan.slow; vt = fan.grid("k_2400_tg_volt")[0]
print(f"grid {fan.nrows} x {fan.nfast}; R {R.min():.0f}-{R.max():.0f} Ohm; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
itg = fan.grid("k_2400_tg_curr"); ibg = fan.grid("k_2400_bg_curr")
print(f"I_tg {itg.min()*1e12:.0f}..{itg.max()*1e12:.0f} pA (med {np.median(itg)*1e12:.0f}); I_bg {ibg.min()*1e12:.0f}..{ibg.max()*1e12:.0f} pA (med {np.median(ibg)*1e12:.0f})")
# ridge: argmax of R along the fast axis per row
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
print("row  V_bg   V_tg(max)  R_max   n_geo  D_geo")
ridge = []
for i in range(fan.nrows):
    j = int(np.argmax(R[i])); n, D = calc_nD(vt[j], vb[i], c_tg, c_bg)
    ridge.append((vb[i], vt[j], R[i, j]))
    print(f"{i:3d} {vb[i]:+.2f}  {vt[j]:+.3f}   {R[i,j]:6.0f}  {n:+.2f}  {D:+.3f}")
ridge = np.array(ridge)
# linear fit of the ridge where the max is interior
m = (ridge[:, 1] > vt.min() + 0.02) & (ridge[:, 1] < vt.max() - 0.02)
if m.sum() >= 3:
    p = np.polyfit(ridge[m, 0], ridge[m, 1], 1)
    print(f"ridge fit V_tg = {p[0]:+.3f} * V_bg + {p[1]:+.3f}  -> c_bg/c_tg = {-p[0]:.3f} (geometry 0.864); V_tg0 at V_bg=0: {p[1]:+.3f}")
fig, ax = plt.subplots(1, 3, figsize=(16, 5))
pm = ax[0].pcolormesh(vt, vb, R, shading="nearest", cmap="viridis"); fig.colorbar(pm, ax=ax[0], label="|Rxx| (Ohm)")
ax[0].plot(ridge[m, 1], ridge[m, 0], "r.", ms=3)
ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)"); ax[0].set_title(f"run {rid} |Rxx|")
pm = ax[1].pcolormesh(vt, vb, np.log10(R), shading="nearest", cmap="magma"); fig.colorbar(pm, ax=ax[1], label="log10 R")
ax[1].set_xlabel("V_tg (V)"); ax[1].set_title("log10 |Rxx|")
for i in range(0, fan.nrows, max(1, fan.nrows // 8)):
    ax[2].plot(vt, R[i], lw=0.8, label=f"V_bg={vb[i]:+.1f}")
ax[2].set_xlabel("V_tg (V)"); ax[2].set_ylabel("|Rxx| (Ohm)"); ax[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"hera_scratch/run{rid}_map.png", dpi=100)
print("saved", f"hera_scratch/run{rid}_map.png")
