# cnp-t-ladder: runs 8-18, one per T point; peak R per D window; Arrhenius on the high-T branch
import scipy.constants as cst
D_LAB = {0.40: -0.11, 0.00: 0.0, -0.45: +0.10, -0.80: +0.19, -1.15: +0.28}
data = {}
for rid in range(8, 19):
    g = run(rid)
    if g.recipe != "cnp-t-ladder":
        continue
    mc = g.meta["measurement_config"]
    vb = g.col("k_2400_bg_volt"); I = g.col("sr0_X") / mc["sr0_gain"]
    R = np.abs(g.col("sr1_X") / I); Tm = np.median(g.col("T_sample"))
    for v in np.unique(np.round(vb, 3)):
        m = np.isclose(np.round(vb, 3), v)
        data.setdefault(float(v), []).append((Tm, float(np.max(R[m]))))
fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
print("Arrhenius (T >= 8 K), gap = 2 x slope:")
for v in sorted(data, reverse=True):
    arr = np.array(sorted(data[v])); lab = D_LAB.get(round(v, 2), v)
    ax[0].semilogy(arr[:, 0], arr[:, 1], "o-", label=f"D−D0={lab:+.2f}")
    ax[1].semilogy(1 / arr[:, 0], arr[:, 1], "o-", label=f"D−D0={lab:+.2f}")
    hi = arr[arr[:, 0] >= 8]
    p = np.polyfit(1 / hi[:, 0], np.log(hi[:, 1]), 1)
    print(f"  D−D0={lab:+.2f}: R(1.2K)={arr[0,1]:.0f} Ω, R(50K)={arr[-1,1]:.0f} Ω, Δ = {2*p[0]*cst.k/cst.e*1e3:.1f} meV")
ax[0].set_xlabel("T (K)"); ax[0].set_ylabel("R_CNP (Ω)"); ax[0].legend(fontsize=8); ax[0].set_title("runs 8–18: R_CNP(T) at five D")
ax[1].set_xlabel("1/T (1/K)"); ax[1].set_title("Arrhenius"); ax[1].legend(fontsize=8)
