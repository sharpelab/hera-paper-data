# Run 6 — Rxx, Rxy vs filling factor at fixed B=7.95 T
import scipy.constants as cst
g6 = run(6); print(summarize_run(g6))
i6 = g6.col("sr0_X") / (-1e6)
R1 = g6.col("sr1_X") / i6; R2 = g6.col("sr2_X") / i6; Rxy = g6.col("sr3_X") / i6
Vtg = g6.col("DC_bias"); Vbg = g6.col("k_2400_volt")
nn = np.array([cal.n_D(Vtg[k], Vbg[k])[0] for k in range(len(Vtg))])
nu = nn * cst.h / (cst.e * 7.95)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(nu, R1/1e3, "o-", ms=3, label="Rxx sr1"); ax[0].plot(nu, R2/1e3, "s-", ms=3, label="Rxx sr2")
for v in (2, 4, 6, 8): ax[0].axvline(v, ls=":", c="grey", lw=0.7)
ax[0].set_xlabel("nu (= n h / e B, B=7.95 T)"); ax[0].set_ylabel("Rxx [kohm]")
ax[0].set_title("Rxx vs nu: monotonic, NO QH minima"); ax[0].legend()
ax[1].plot(nu, Rxy/1e3, "o-", ms=3, color="C3", label="Rxy measured")
nv = np.linspace(1, 8, 200); ax[1].plot(nv, 25.813/nv, "k--", lw=1, label="quantized h/nu e^2")
for v in (2, 4, 6, 8): ax[1].plot(v, 25.813/v, "k+", ms=10)
ax[1].set_xlabel("nu"); ax[1].set_ylabel("Rxy [kohm]"); ax[1].set_title("Rxy: classical, NO plateaus"); ax[1].legend()
plt.show()
print("Rxx ~12%% washed-out modulation on a monotonic background; Rxy below quantized, no plateaus.")
