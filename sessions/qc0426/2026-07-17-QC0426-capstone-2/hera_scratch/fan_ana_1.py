# Run 7 — Landau fan, hole side D=0 (landau-fan-vti). Raw first: grids + map.
from hera.analysis import fan_grids, resistance_grids

fan7 = fan_grids("data/7")
rg7 = resistance_grids(fan7)
B7 = fan7.slow
ns7 = np.linspace(-0.5, -3.5, 101)      # design n vector (e12 cm^-2)
FLnom7 = luttinger_frequency(np.abs(ns7) * 1e16)
print(f"fan: {rg7.R['sr2'].shape} (B rows x n cols), B {B7[0]:.2f}-{B7[-1]:.2f} T, "
      f"interrupted={fan7.metadata.get('interrupted')}")
Tcol = fan7.grid("T_sample")
print(f"T during fan: {np.nanmin(Tcol):.3f}-{np.nanmax(Tcol):.3f} K")

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    R = rg7.R[ch]
    pm = ax.pcolormesh(np.abs(ns7), B7, np.log10(np.clip(R, 10, None)),
                       shading="auto", cmap="viridis")
    plt.colorbar(pm, ax=ax, label="log10 R (Ω)")
    ax.set_xlabel("|n| (10¹² cm⁻²)")
    ax.set_title(ch)
axes[0].set_ylabel("B (T)")
fig.suptitle("run 7 raw: Rxx(n, B), hole side D=0, 0.77–8 T × 101 n-cols")
fig.tight_layout()
plt.show()
# clip bookkeeping (soft-clip corner, flagged live): columns exceeding 95% ceiling
for ch, ceil in (("sr1", 23.75e3), ("sr2", 9.5e3)):
    cl = rg7.R[ch].max(axis=0) > ceil
    print(f"{ch}: {cl.sum()} clipped cols (|n| <= {np.abs(ns7)[cl].max() if cl.any() else 0:.2f}) — excluded from FFT claims")
