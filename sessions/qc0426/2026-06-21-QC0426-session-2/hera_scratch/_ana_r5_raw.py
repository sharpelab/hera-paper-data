# Run 5 raw — re-form the fan Rxx(n, B), sr1
g5 = run(5); print(summarize_run(g5))
fan5 = fan_grids(g5); ci5 = {c: i for i, c in enumerate(fan5.cols)}
G5 = fan5.data.reshape(fan5.nrows, fan5.nfast, len(fan5.cols))
Bax5 = G5[:, 0, ci5["magnet_field"]]
rg5 = resistance_grids(fan5); R1f = rg5.R["sr1"]; R2f = rg5.R["sr2"]
n_col = np.linspace(0.5e16, 3.5e16, 40)
oB = np.argsort(Bax5); Bs5 = Bax5[oB]
plt.figure(figsize=(7.5, 5))
plt.pcolormesh(n_col / 1e16, Bs5, np.log10(np.abs(R1f[oB, :]) + 1), shading="nearest", cmap="magma")
plt.colorbar(label="log10(|Rxx|+1)  sr1")
plt.xlabel("n [10^12 cm^-2]"); plt.ylabel("B [T]")
plt.title("Run 5 fan: log|Rxx|(n,B) sr1 (low-n/high-B corner = QH, clipped)")
plt.show()
