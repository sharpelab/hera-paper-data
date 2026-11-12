# Run 0 — raw: re-entry baseline, constant-D n-cut at D=-0.64
g = run(0)
print(summarize_run(g))
vtg = g.col_at(g.col_indices('k_tg_volt')[0]); vbg = g.col_at(g.col_indices('k_bg_volt')[0])
n11 = cal.n_D(vtg, vbg)[0] / 1e4 / 1e11
D_Vnm = cal.n_D(vtg, vbg)[1] / 1e9
I_bias = 1e-9
R3 = (g.col_at(g.col_indices('sr830_3_X')[0]) / 100) / I_bias   # 4T Rxx (30-31)
R2 = (g.col_at(g.col_indices('sr830_2_X')[0]) / 100) / I_bias   # 2T (5-4)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(n11, R3, '-o', ms=3)
ax[0].set_xlabel('n  (1e11 cm$^{-2}$)'); ax[0].set_ylabel('R$_{xx}$ 4T (30-31)  ($\\Omega$)')
ax[0].set_title(f'Run 0 raw — D={D_Vnm.mean():.3f} V/nm'); ax[0].axhline(0, color='k', lw=0.5)
ax[1].plot(n11, R3, '-o', ms=3); ax[1].set_ylim(-1, 5); ax[1].axhline(0, color='k', lw=0.5)
ax[1].axhline(2, color='r', ls=':', lw=0.8, label='2 $\\Omega$')
ax[1].set_xlabel('n  (1e11 cm$^{-2}$)'); ax[1].set_ylabel('R$_{xx}$  ($\\Omega$)')
ax[1].set_title('zoom: SC core'); ax[1].legend()
plt.tight_layout(); plt.show()
