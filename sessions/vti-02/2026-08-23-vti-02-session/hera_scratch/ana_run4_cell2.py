from sharpelab_nb.gates import stack_capacitance, calc_nD
mc = g.meta["measurement_config"]
vb = g.col("k_2400_bg_volt"); vt = g.col("k_2400_tg_volt")
I = g.col("sr0_X") / mc["sr0_gain"]; R = np.abs(g.col("sr1_X") / I)
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
rows = np.unique(vb); tab = []
for v in rows:
    m = np.isclose(vb, v); x, y = vt[m], R[m]; j = np.argmax(y)
    half = (y[j] + y.min()) / 2; above = x[y >= half]
    tab.append((v, x[j], y[j], (above.max() - above.min()) * 1e3, j in (0, len(x) - 1)))
tab = np.array(tab, dtype=float); ok = tab[:, 4] == 0
_, D = calc_nD(tab[:, 1], tab[:, 0], c_tg, c_bg)
hole = ok & (tab[:, 0] <= -0.2); p = np.polyfit(tab[hole, 0], tab[hole, 1], 1)
i0 = np.argmin(np.where(ok, tab[:, 2], np.inf)); D0 = D[i0]
print(f"CNP line (hole-side rows): V_tg = {p[1]:+.3f} {p[0]:+.3f}*V_bg -> c_bg/c_tg = {-p[0]:.3f}")
print(f"R_CNP minimum {tab[i0,2]:.0f} Ω at (V_tg, V_bg) = ({tab[i0,1]:+.3f}, {tab[i0,0]:+.2f}), D_geo = {D0:+.3f} V/nm  -> D_offset")
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
ax[0].semilogy(D[ok] - D0, tab[ok, 2], "o-", label="R_peak (interior)"); ax[0].semilogy(D[~ok] - D0, tab[~ok, 2], "s", mfc="none", label="edge-clipped")
ax[0].set_xlabel("D − D0 (V/nm, geometry scale)"); ax[0].set_ylabel("R_CNP (Ω)"); ax[0].legend(); ax[0].set_title("run 4 — R_CNP(D), B=0, 1.18 K")
ax[1].plot(D[ok] - D0, tab[ok, 3], "o-"); ax[1].set_xlabel("D − D0 (V/nm)"); ax[1].set_ylabel("FWHM in V_tg (mV)"); ax[1].set_title("CNP peak width")
# ±D comparison on the common range
Dp = D[ok] - D0; Rp = tab[ok, 2]; pos = Dp > 0.02; neg = Dp < -0.02
dd = np.linspace(0.03, min(Dp.max(), -Dp.min()), 12)
_op = np.argsort(Dp[pos]); _on = np.argsort(-Dp[neg])
Rpos = np.interp(dd, Dp[pos][_op], Rp[pos][_op]); Rneg = np.interp(dd, (-Dp[neg])[_on], Rp[neg][_on])
ax[2].plot(dd, Rneg / Rpos, "o-"); ax[2].axhline(1, color="k", lw=0.5); ax[2].set_xlabel("|D − D0| (V/nm)"); ax[2].set_ylabel("R(−D) / R(+D)"); ax[2].set_title("D-symmetry")
for d_, rr in zip(dd, Rneg / Rpos):
    print(f"|D-D0| = {d_:.3f}: R(-D)/R(+D) = {rr:.2f}")
print("R_CNP at D-D0 = +0.10, +0.20, +0.30:", [f"{np.interp(x, Dp[pos][_op], Rp[pos][_op]):.0f} Ω" for x in (0.10, 0.20, 0.30)])
