# Figure 1 (run 3) — raw: wide SC dome Rxx(n,D) at B_eff0, pcolormesh
g = run(3)
print(summarize_run(g))
vtg = g.col_at(g.col_indices("k_tg_volt")[0]); vbg = g.col_at(g.col_indices("k_bg_volt")[0])
n11 = cal.n_D(vtg, vbg)[0] / 1e4 / 1e11
D_Vnm = cal.n_D(vtg, vbg)[1] / 1e9
R = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100) / 1e-9   # 4T Rxx (30-31)

# reconstruct regular grid (flattened boustrophedon, variable-len sanitized rows)
DN, DD = 0.03, 0.0025
ng = np.sort(np.round(np.arange(-1.0, -7.0001, -DN), 5))
Dg = np.sort(np.round(np.arange(-0.40, -0.69001, -DD), 5))
ni = np.round((n11 - ng[0]) / DN).astype(int); di = np.round((D_Vnm - Dg[0]) / DD).astype(int)
Z = np.full((len(Dg), len(ng)), np.nan)
ok = (ni >= 0) & (ni < len(ng)) & (di >= 0) & (di < len(Dg)); Z[di[ok], ni[ok]] = R[ok]

def _edges(c):
    c = np.asarray(c, float); e = np.empty(len(c)+1)
    e[1:-1] = 0.5*(c[:-1]+c[1:]); e[0] = c[0]-0.5*(c[1]-c[0]); e[-1] = c[-1]+0.5*(c[-1]-c[-2]); return e
Xe, Ye = _edges(ng), _edges(Dg)

fig, ax = plt.subplots(figsize=(8.5, 6))
pc = ax.pcolormesh(Xe, Ye, Z, cmap="viridis", vmin=0, vmax=50, shading="flat")
cb = plt.colorbar(pc, ax=ax, extend="max"); cb.set_label(r"$R_{xx}$ 4T (30-31) ($\Omega$)  [rails >1 k$\Omega$ near CNP]")
Xc, Yc = np.meshgrid(ng, Dg)
cs = ax.contour(Xc, Yc, np.ma.masked_invalid(Z), levels=[2, 5], colors=["white", "cyan"], linewidths=1.1)
ax.clabel(cs, fmt="%g Ω", fontsize=8)
ax.plot(-5.0, -0.64, "r*", ms=15, label="selected optimum n=-5.0, D=-0.64")
ax.axhline(-0.64, color="orange", ls="--", lw=1, label="widest-D line (Figs 3/4/5)")
ax.set_xlabel(r"$n$ ($10^{11}$ cm$^{-2}$)"); ax.set_ylabel(r"$D$ (V/nm)")
ax.set_title("Fig 1 — SC dome R$_{xx}$(n,D) at B$_{eff0}$=-0.366 mT (run 3)")
ax.legend(loc="upper left", fontsize=8); plt.tight_layout(); plt.show()
