# Run 11 — Fig 5 verify: 1D dV/dI vs I_dc at base, B_eff0, optimum (Ic check)
g = run(11)
Vdc = g.col_at(g.col_indices('dc205_1_voltage')[0]); Idc = Vdc/1e8*1e9     # nA
dVdI = (g.col_at(g.col_indices('sr830_3_X')[0])/100)/0.5e-9                # ohm
B = g.col_at(g.col_indices('magnet_field')[0]).mean()*1e3; T = g.col('T').mean()*1e3
fwd = slice(0,151); bwd = slice(151,302)
zb = np.median(dVdI[np.abs(Idc)<3])
ipk = abs(Idc[fwd][np.argmax(dVdI[fwd][Idc[fwd]>0])])
print(f"B={B:.4f} mT (true {B+0.366:.3f}); T={T:.0f} mK; zero-bias dV/dI={zb:.2f} ohm; switching peak ~+/-{ipk:.0f} nA, {np.nanmax(dVdI):.0f} ohm")
fig,ax = plt.subplots(figsize=(8,5))
ax.plot(Idc[fwd], dVdI[fwd], '-', lw=1, label='fwd (-80->+80 nA)')
ax.plot(Idc[bwd], dVdI[bwd], '-', lw=1, alpha=0.7, label='bwd (+80->-80 nA)')
ax.axhline(0, color='k', lw=0.5); ax.set_xlabel(r'$I_{dc}$ (nA)'); ax.set_ylabel(r'$dV/dI$ ($\Omega$)')
ax.set_title('Fig 5 verify — dV/dI vs $I_{dc}$, base, B$_{eff0}$ (run 11)'); ax.legend(); ax.set_ylim(-10,200)
plt.tight_layout(); plt.show()
