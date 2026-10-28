# Run 1 — B=0 (n,D) gate map, raw re-form (TG fast x BG slow)
from scipy.ndimage import gaussian_filter1d
g1 = run(1)
print(summarize_run(g1))
fan = fan_grids(g1)
ci = {c: i for i, c in enumerate(fan.cols)}
G = fan.data.reshape(fan.nrows, fan.nfast, len(fan.cols))
VTG = G[:, :, ci["DC_bias"]]
VBG = G[:, 0, ci["k_2400_volt"]]
tg_axis = VTG[0]
rg = resistance_grids(fan)
print("leakage |I_bg|max=%.2f nA |I_si|max=%.2f nA"
      % (np.abs(g1.col("k_2400_curr")).max()*1e9, np.abs(g1.col("k_2410_curr")).max()*1e9))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    im = ax.pcolormesh(tg_axis, VBG, np.log10(np.abs(rg.R[ch]) + 1),
                       shading="nearest", cmap="viridis")
    ax.set_xlabel("V_tg (DC_bias) [V]"); ax.set_ylabel("V_bg [V]")
    ax.set_title(f"{ch}  log10|Rxx|  (run 1, B=0)")
    fig.colorbar(im, ax=ax, label="log10(|R|+1)")
plt.show()
