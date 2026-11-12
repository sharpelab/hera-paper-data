# --- Run 5: bias spectroscopy at the optimum — the supercurrent. RAW dV/dI. ---
g5 = open_run(Path(file_path)/"5"); print(summarize_run(g5))
Vdc = g5.col_at(g5.cols.index("dc205_1_voltage"))
Idc = Vdc/1e8*1e9                                   # nA (100 MΩ)
Iac = g5.col("sr830_1_X")/(-1e6)
dVdI = np.abs((g5.col("sr830_3_X")/100.0)/Iac)       # Ω
o=np.argsort(Idc); Idc,dVdI=Idc[o],dVdI[o]
zb=dVdI[np.abs(Idc)<2].mean(); nm=dVdI[np.abs(Idc)>120].mean(); thr=zb+0.5*(nm-zb)
icp=np.abs(Idc[(Idc>0)&(dVdI>=thr)]).min(); icn=np.abs(Idc[(Idc<0)&(dVdI>=thr)]).min()
print(f"zero-bias dV/dI={zb:.2f} Ω; normal={nm:.1f} Ω; Ic+={icp:.1f} Ic-={icn:.1f} nA")
fig,ax=plt.subplots(figsize=(8,5))
ax.plot(Idc,dVdI,".-",ms=4)
ax.axhline(thr,color="grey",ls=":",lw=.8,label=f"half-rise {thr:.0f}Ω")
ax.axvline(icp,color="r",ls="--",lw=.8); ax.axvline(-icn,color="b",ls="--",lw=.8)
ax.set_xlabel("I_dc (nA)"); ax.set_ylabel("dV/dI (Ω)")
ax.set_title(f"Run 5 — supercurrent at n=−4.65e11, D=−0.65: Ic±≈{icp:.0f}/{icn:.0f} nA")
ax.legend(); ax.grid(alpha=.3); plt.show()
