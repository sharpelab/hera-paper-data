"""Figure 3 R(T,n) map from run 4. Uses RECORDED T per heater step (not setpoint).
Builds the pcolormesh, extracts Tc(n) by 50%-normal threshold, dome T-extent."""
import sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, GateCalibration

rid = sys.argv[1] if len(sys.argv) > 1 else "4"
g = open_run(f"data/{rid}")
print(summarize_run(g)); print("interrupted:", g.interrupted)

N_OFF = -0.362e11*1e4
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=N_OFF)
vtg = g.col_at(g.col_indices("k_tg_volt")[0]); vbg = g.col_at(g.col_indices("k_bg_volt")[0])
n11 = cal.n_D(vtg, vbg)[0]/1e4/1e11
hv = g.col_at(g.col_indices("heater_volt")[0])
T = g.col("T")*1e3                                     # mK, recorded
R = (g.col_at(g.col_indices("sr830_3_X")[0])/100)/1e-9 # 4T Rxx

# verify
itg = np.abs(g.col("k_tg_curr")).max(); ibg = np.abs(g.col("k_bg_curr")).max()
print(f"leak max |I_tg|={itg:.2e} |I_bg|={ibg:.2e} A; NaNs(R)={np.isnan(R).sum()}")
print(f"B held: {g.col_at(g.col_indices('magnet_field')[0]).mean()*1e3:.4f} mT")
print(f"T recorded span: {T.min():.1f} -> {T.max():.1f} mK")

# group by heater step (slow axis) -> rows
hvu = np.unique(hv)
hvu = hvu[np.argsort(-hvu)]                            # descending (480->34)
n_grid = np.sort(np.unique(np.round(n11, 3)))         # fast axis (ascending -7..-4)
# nearest n bin
def nidx(x): return np.argmin(np.abs(n_grid - x))
Z = np.full((len(hvu), len(n_grid)), np.nan)
Trow = np.full(len(hvu), np.nan); Tdrift = np.full(len(hvu), np.nan)
for i, h in enumerate(hvu):
    m = hv == h
    Trow[i] = np.nanmean(T[m]); Tdrift[i] = np.nanmax(T[m]) - np.nanmin(T[m])
    for x, r in zip(n11[m], R[m]):
        Z[i, nidx(x)] = r
print(f"per-row T-drift: median {np.nanmedian(Tdrift):.1f} mK, max {np.nanmax(Tdrift):.1f} mK")
print(f"T monotonic (rows): {bool(np.all(np.diff(Trow) < 1.0))}  (Trow {Trow[0]:.0f}->{Trow[-1]:.0f} mK)")

# Tc(n): per n-column, T where R crosses 50% of its normal value (R at highest T)
Tc = np.full(len(n_grid), np.nan)
for j in range(len(n_grid)):
    col = Z[:, j]                                       # R vs row (T descending)
    good = np.isfinite(col)
    if good.sum() < 10: continue
    Rn = np.nanmedian(col[Trow > 420])                 # normal-state R (top of ladder)
    if not np.isfinite(Rn) or Rn < 5: continue          # only where there's a real normal state
    half = 0.5*Rn
    # walk from cold (low T) up: first crossing above half
    order = np.argsort(Trow)                            # ascending T
    tt, rr = Trow[order], col[order]
    for k in range(1, len(rr)):
        if np.isfinite(rr[k-1]) and np.isfinite(rr[k]) and rr[k-1] < half <= rr[k]:
            f = (half-rr[k-1])/(rr[k]-rr[k-1]); Tc[j] = tt[k-1]+f*(tt[k]-tt[k-1]); break
jopt = nidx(-5.0)
print(f"\nTc at optimum n=-5.0: {Tc[jopt]:.0f} mK (50%-normal)")
print(f"Tc range over dome: {np.nanmin(Tc):.0f} - {np.nanmax(Tc):.0f} mK")

# render
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
def edges(c):
    c = np.asarray(c, float); e = np.empty(len(c)+1)
    e[1:-1] = 0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
oi = np.argsort(Trow); Te = edges(Trow[oi]); Ne = edges(n_grid)
pc = ax[0].pcolormesh(Ne, Te, Z[oi], cmap="inferno", vmin=0, vmax=55, shading="flat")
plt.colorbar(pc, ax=ax[0], label=r"$R_{xx}$ ($\Omega$)")
ax[0].plot(n_grid, Tc, "c.-", ms=3, lw=1, label="Tc (50%-normal)")
ax[0].axvline(-5.0, color="w", ls="--", lw=0.8)
ax[0].set_xlabel(r"$n$ ($10^{11}$ cm$^{-2}$)"); ax[0].set_ylabel("T (mK)")
ax[0].set_title(f"Fig 3 — R(T,n) at D=-0.64, B_eff0 (run {rid})"); ax[0].legend(fontsize=8)
# R(T) at the optimum column
ax[1].plot(Trow, Z[:, jopt], "o-", ms=3)
ax[1].axhline(0, color="k", lw=0.5); ax[1].axvline(Tc[jopt], color="r", ls="--", lw=1, label=f"Tc={Tc[jopt]:.0f} mK")
ax[1].set_xlabel("T (mK)"); ax[1].set_ylabel(r"$R_{xx}$ ($\Omega$)"); ax[1].set_title("R(T) at optimum n=-5.0"); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig("hera_scratch/tdep_map.png", dpi=140)
print("saved hera_scratch/tdep_map.png")
