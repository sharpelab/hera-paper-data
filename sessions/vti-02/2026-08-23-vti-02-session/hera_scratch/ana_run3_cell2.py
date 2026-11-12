from sharpelab_nb.gates import stack_capacitance, calc_nD
fan = fan_grids(g); rg = resistance_grids(fan)
R = np.abs(rg.R["sr1"]); vb = fan.slow; vt = fan.grid("k_2400_tg_volt")[0]
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
# ridge (argmax per row) where the CNP line is interior to the box: rows V_bg <= -0.2
ridge = np.array([(vb[i], vt[np.argmax(R[i])], R[i].max()) for i in range(fan.nrows)])
m = (ridge[:, 0] <= -0.2)
p = np.polyfit(ridge[m, 0], ridge[m, 1], 1)
print(f"CNP line (rows V_bg <= -0.2): V_tg = {p[1]:+.3f} {p[0]:+.3f}*V_bg  ->  c_bg/c_tg = {-p[0]:.3f} (geometry prior 0.864)")
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
pm = ax[0].pcolormesh(vt, vb, np.log10(R), shading="nearest", cmap="magma"); fig.colorbar(pm, ax=ax[0], label="log10 |Rxx| (Ω)")
ax[0].plot(ridge[m, 1], ridge[m, 0], "c.", ms=4, label="ridge (argmax)")
ax[0].plot(p[1] + p[0] * vb, vb, "w--", lw=0.8, label="fit"); ax[0].set_xlim(vt.min(), vt.max()); ax[0].set_ylim(vb.min(), vb.max())
ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)"); ax[0].legend(fontsize=8); ax[0].set_title("run 3 — coarse gate map, B=0, 1.18 K")
n_r, D_r = calc_nD(ridge[:, 1], ridge[:, 0], c_tg, c_bg)
ax[1].semilogy(D_r[m], ridge[m, 2], "o-", label="ridge rows V_bg ≤ −0.2 (interior)")
ax[1].semilogy(D_r[~m], ridge[~m, 2], "s", mfc="none", label="rows V_bg > −0.2 (edge-pinned / 2nd line)")
ax[1].set_xlabel("D (V/nm, geometry prior)"); ax[1].set_ylabel("R_max per row (Ω)"); ax[1].legend(fontsize=8); ax[1].set_title("R_CNP vs D (coarse)")
for i in [21, 23, 25, 27, 29, 31, 33]:
    ax[2].plot(vt, R[i], lw=0.8, label=f"V_bg={vb[i]:+.1f}")
ax[2].set_xlabel("V_tg (V)"); ax[2].set_ylabel("|Rxx| (Ω)"); ax[2].legend(fontsize=7); ax[2].set_title("TG cuts")
for i in range(fan.nrows):
    if i % 3 == 0 or ridge[i, 2] > 500:
        print(f"V_bg={vb[i]:+.2f}  V_tg*={ridge[i,1]:+.2f}  R_max={ridge[i,2]:6.0f} Ω  D_geo={D_r[i]:+.3f} V/nm")
