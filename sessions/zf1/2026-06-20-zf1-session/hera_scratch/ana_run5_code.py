g = run(5); mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
vtg = g.col_at(g.col_indices("k_tg_volt")[-1]); vbg = g.col_at(g.col_indices("k_bg_volt")[-1])
R2 = (g.col("sr830_2_X")/mc["sr2_gain"])/Ib; R3 = (g.col("sr830_3_X")/mc["sr3_gain"])/Ib
n0,_ = cal.n_D(np.array([0.082]), np.array([0.0])); nn, DD = cal.n_D(vtg, vbg); nn = nn - n0[0]
x = nn/1e4/1e12; i3 = np.argmin(R3)
print(f"D={DD.mean()/1e9:.3f} V/nm ; n {x.min():.3f}..{x.max():.3f} e12")
print(f"Rxx2 {R2.min():.0f}..{R2.max():.0f} Ω ; Rxx3 {R3.min():.1f}..{R3.max():.1f} Ω")
print(f"coincident dip @ n={x[i3]:.3f}e12 (Vtg={vtg[i3]:.3f}, Vbg={vbg[i3]:.3f}): sr3={R3[i3]:.1f}Ω, sr2={R2[i3]:.0f}Ω")

fig, ax1 = plt.subplots(figsize=(9, 5))
fig.suptitle(f"Run 5 — density cut at B=0, D={DD.mean()/1e9:.2f} V/nm — Rxx2 vs Rxx3")
l1, = ax1.plot(x, R2/1e3, ".-", color="C0", label="Rxx2 = sr830_2 (4T, kΩ)")
ax1.axvline(x[i3], color="gray", ls=":", lw=1)
ax1.set_xlabel("n (e12 cm$^{-2}$)"); ax1.set_ylabel("Rxx2 (kΩ)", color="C0"); ax1.tick_params(axis='y', labelcolor="C0")
ax2 = ax1.twinx(); l2, = ax2.plot(x, R3, ".-", color="C3", label="Rxx3 = sr830_3 (Ω)")
ax2.set_ylabel("Rxx3 (Ω)", color="C3"); ax2.tick_params(axis='y', labelcolor="C3")
ax1.legend(handles=[l1, l2], fontsize=9); ax1.grid(alpha=0.3); plt.tight_layout(); plt.show()
