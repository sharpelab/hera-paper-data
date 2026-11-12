# Run 7 raw maps — all four channels, linear scale, native grid
r7b = run(7)
fg7b = fan_grids(r7b)
rg7b = resistance_grids(fg7b)
B7b = np.asarray(fg7b.slow)
ns_d = np.linspace(2.0, 6.3, 51)   # design density axis (1e12 cm^-2)

fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True, sharey=True)
panels = [
    (axes[0, 0], np.asarray(rg7b.R["sr1"]),      "sr1 Rxx (T3-T4) [Ohm]",   "viridis"),
    (axes[0, 1], np.asarray(rg7b.R["sr2"]),      "sr2 Rxx (B4-B5) [Ohm]",   "viridis"),
    (axes[1, 0], np.asarray(rg7b.R["sr3"]),      "sr3 Rxy (T5-B6) [Ohm]",   "RdBu_r"),
    (axes[1, 1], np.asarray(rg7b.current) * 1e9, "sr0 drain current [nA]",  "cividis"),
]
for ax, Z, title, cmap in panels:
    pm = ax.pcolormesh(ns_d, B7b, Z, cmap=cmap, shading="auto")
    plt.colorbar(pm, ax=ax, label=title.split("[")[-1].rstrip("]"))
    ax.set_title(title)
for ax in axes[1]: ax.set_xlabel("n design (1e12 cm^-2)  [x1.07 = Hall-true]")
for ax in axes[:, 0]: ax.set_ylabel("B (T)")
fig.suptitle("run 7 - RAW Landau fan, all channels (linear, native 126x51 grid)")
fig.tight_layout()
