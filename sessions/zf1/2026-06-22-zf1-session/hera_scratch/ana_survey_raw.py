# --- Run 2: Step-1 survey gatemap (full box). RAW first. ---
from matplotlib.colors import LogNorm
f2 = fan_grids(Path(file_path)/"2"); rg2 = resistance_grids(f2)
VT = f2.grid("k_tg_volt"); VB = f2.grid("k_bg_volt")
Rxx = np.abs(rg2.R["sr830_3"])          # 4T longitudinal (30-31)
Icur = rg2.current
print(summarize_run(run(2)))
print(f"current min/med = {Icur.min()*1e9:.3f}/{np.median(Icur)*1e9:.3f} nA  (current-bias holds)")

N = cal.density(VT, VB)/1e15; D = cal.displacement_field(VT, VB)/1e9
fig, ax = plt.subplots(1, 2, figsize=(14,5))
pc=ax[0].pcolormesh(VT, VB, np.clip(Rxx,1,None), norm=LogNorm(1,5e3), shading="nearest", cmap="viridis")
ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)"); ax[0].set_title("Run 2 — 4T Rxx(V_tg,V_bg) [Ω, log] RAW"); fig.colorbar(pc,ax=ax[0])
pc=ax[1].pcolormesh(N, D, np.clip(Rxx,1,None), norm=LogNorm(1,5e3), shading="nearest", cmap="viridis")
ax[1].axhline(-0.5,color="w",ls=":",lw=.7); ax[1].axvline(-5,color="w",ls=":",lw=.7)
ax[1].set_xlabel("n (1e11 cm⁻²)"); ax[1].set_ylabel("D (V/nm)"); ax[1].set_title("Rxx(n,D) [Ω, log] (white = proximity-SC prior)"); fig.colorbar(pc,ax=ax[1])
plt.show()
