g=run(8); mc=g.meta["measurement_config"]; Ib=mc["bias_voltage_1"]/mc["bias_resistor"]
vtg=g.col_at(g.col_indices("k_tg_volt")[-1]); vbg=g.col_at(g.col_indices("k_bg_volt")[-1])
nn,DD=cal.n_D(vtg,vbg); nn=nn/1e4/1e12; DD=DD/1e9
R2=(g.col("sr830_2_X")/mc["sr2_gain"])/Ib
X3=(g.col("sr830_3_X")/mc["sr3_gain"])/Ib; P3=g.col("sr830_3_P")
mag3=np.abs((g.col("sr830_3_X")/mc["sr3_gain"])/np.cos(np.deg2rad(P3)))/Ib
print(f"sr2 (4T): min {R2.min():.0f} Ω, median {np.median(R2):.0f} Ω, pts<3kΩ: {(R2<3000).sum()}")
print(f"sr3 X: min {X3.min():.1f} Ω ; sr3<8Ω localized to n[-0.51,-0.46] x D[-0.675,-0.652]")

fig,ax=plt.subplots(1,3,figsize=(19,5))
fig.suptitle("Run 8 — 8h nD-map — sr3 'dip' is NOT SC: where sr3 drops, the 4T Rxx (sr2) is HIGH")
s0=ax[0].scatter(nn,DD,c=np.clip(R2/1e3,0,20),s=4,cmap="inferno"); plt.colorbar(s0,ax=ax[0],label="kΩ")
ax[0].plot(-0.4654,-0.6501,"c+",ms=13,mew=2); ax[0].set(xlabel="n (e12)",ylabel="D (V/nm)",title="sr2 4T Rxx (trusted)")
s1=ax[1].scatter(nn,DD,c=np.clip(X3,0,40),s=4,cmap="inferno"); plt.colorbar(s1,ax=ax[1],label="Ω")
ax[1].plot(-0.4654,-0.6501,"c+",ms=13,mew=2); ax[1].set(xlabel="n (e12)",ylabel="D (V/nm)",title="sr3 X (marker)")
# D=-0.66 diagnostic cut
row=np.abs(DD+0.66)<0.003; o=np.argsort(nn[row]); x=nn[row][o]
axA=ax[2]; l1,=axA.plot(x,R2[row][o]/1e3,".-",color="C0",label="sr2 4T (kΩ)")
axA.set(xlabel="n (e12)",ylabel="sr2 4T (kΩ)"); axA.tick_params(axis='y',labelcolor="C0")
axB=axA.twinx(); l2,=axB.plot(x,mag3[row][o],".-",color="C1",label="sr3 |mag| (Ω)")
axB.set_ylabel("sr3 (Ω)",color="C1"); axB.tick_params(axis='y',labelcolor="C1")
axA.legend(handles=[l1,l2],fontsize=8,loc="upper left"); axA.set_title("D=-0.66 cut: sr3 down <-> sr2 UP")
plt.tight_layout(); plt.show()
