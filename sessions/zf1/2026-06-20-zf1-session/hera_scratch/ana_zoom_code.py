from scipy.ndimage import gaussian_filter1d, uniform_filter
g = run(4); mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
NF=101; nr=g.rows//NF
vtg=g.col_at(g.col_indices("k_tg_volt")[-1])[:nr*NF].reshape(nr,NF)
vbg=g.col_at(g.col_indices("k_bg_volt")[-1])[:nr*NF].reshape(nr,NF)
R=((g.col("sr830_2_X")/mc["sr2_gain"])/Ib)[:nr*NF].reshape(nr,NF)   # sr2 4T Rxx
tg_axis,bg_axis=vtg[0],vbg[:,0]
Rs=uniform_filter(R,3); im=np.unravel_index(np.argmin(Rs),Rs.shape)
print(f"sr2 4T Rxx {R.min():.0f}..{R.max():.0f} Ω, median {np.median(R):.0f} Ω")
print(f"pts<3kΩ:{(Rs<3000).sum()} <2kΩ:{(Rs<2000).sum()} <1kΩ:{(Rs<1000).sum()}  -> NO Rxx->0")
print(f"lowest smoothed {Rs[im]:.0f} Ω at Vtg={vtg[im]:.2f} Vbg={vbg[im]:.2f}")
tg_cnp=np.array([tg_axis[np.argmax(gaussian_filter1d(R[i],2))] for i in range(nr)])
ins=(tg_cnp>tg_axis.min()+0.3)&(tg_cnp<tg_axis.max()-0.3); slope,icpt=np.polyfit(bg_axis[ins],tg_cnp[ins],1)
n0,_=cal.n_D(np.array([icpt]),np.array([0.0])); nn,DD=cal.n_D(vtg.ravel(),vbg.ravel())
nn=(nn-n0[0]).reshape(R.shape); DD=DD.reshape(R.shape)
print(f"(n,D) covered: n {nn.min()/1e4/1e12:.1f}..{nn.max()/1e4/1e12:.1f} e12 ; D {DD.min()/1e9:.2f}..{DD.max()/1e9:.2f} V/nm")

fig,ax=plt.subplots(1,2,figsize=(13,5))
fig.suptitle("Run 4 — SC zoom V_bg>0/V_tg<0 (0.07 V) — sr2 4T Rxx — B~0 nominal (~2 mT trapped)")
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 4T Rxx (kΩ, 0–30)"); plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,4),cmap="inferno",shading="nearest")
ax[1].plot(vtg[im],vbg[im],"c*",ms=13,label=f"min {Rs[im]:.0f} Ω (metal)")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="zoom 0–4 kΩ — no sub-kΩ dome"); ax[1].legend(fontsize=8); plt.colorbar(im1,ax=ax[1])
plt.tight_layout(); plt.show()
