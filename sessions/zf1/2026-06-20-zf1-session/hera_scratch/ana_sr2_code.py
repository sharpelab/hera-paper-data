# Step-1 gatemap redone with the CORRECT 4T Rxx channel = sr830_2.
from scipy.ndimage import gaussian_filter1d, uniform_filter
NF = 101
def Rg(g, nrows):  # sr830_2 = 4T Rxx (corrected)
    mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
    return ((g.col("sr830_2_X")/mc["sr2_gain"])/Ib)[:nrows*NF].reshape(nrows, NF)
r2, r3 = run(2), run(3); n2 = 44
vtg = np.vstack([r2.col_at(r2.col_indices("k_tg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_tg_volt")[-1]).reshape(17,NF)])
vbg = np.vstack([r2.col_at(r2.col_indices("k_bg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_bg_volt")[-1]).reshape(17,NF)])
R = np.vstack([Rg(r2,n2), Rg(r3,17)])               # 4T Rxx (sr2), 61x101
tg_axis, bg_axis = vtg[0], vbg[:,0]
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R[i],2))] for i in range(61)])
ins = (tg_cnp>tg_axis.min()+0.3)&(tg_cnp<tg_axis.max()-0.3)
slope, icpt = np.polyfit(bg_axis[ins], tg_cnp[ins], 1)
n0,_ = cal.n_D(np.array([icpt]), np.array([0.0]))
nn, DD = cal.n_D(vtg.ravel(), vbg.ravel()); nn=(nn-n0[0]).reshape(R.shape); DD=DD.reshape(R.shape)
Rs = uniform_filter(R,3); im=np.unravel_index(np.argmin(Rs),Rs.shape)
print(f"sr2 4T Rxx: {R.min():.0f}..{R.max():.0f} Ω, metal ~{np.median(R[(R>500)&(R<8000)]):.0f} Ω")
print(f"CNP: Vtg={slope:.3f}*Vbg+{icpt:.3f}, cap ratio {-slope:.3f} (prior 1.18)")
print(f"(n,D) covered: n {nn.min()/1e4/1e12:.1f}..{nn.max()/1e4/1e12:.1f} e12 cm^-2 ; D {DD.min()/1e9:.2f}..{DD.max()/1e9:.2f} V/nm")
print(f"lowest smoothed sr2 {Rs[im]:.0f} Ω at Vtg={vtg[im]:.2f} Vbg={vbg[im]:.2f} (n={nn[im]/1e4/1e12:.2f}e12, D={DD[im]/1e9:.3f})")
print(f"pts with sr2<2kΩ: {(Rs<2000).sum()} ; <1kΩ: {(Rs<1000).sum()}  -> NO Rxx->0 region")

fig, ax = plt.subplots(1,3, figsize=(18,5))
fig.suptitle("Step-1 gatemap — 4T Rxx = sr830_2 (CORRECTED) — B~0, 0.5 nA, 34 mK")
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[0].plot(slope*bg_axis[ins]+icpt,bg_axis[ins],"r-",lw=1,label=f"CNP slope {slope:.2f}")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 4T Rxx (kΩ, 0–30)"); ax[0].legend(fontsize=8); plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,5),cmap="inferno",shading="nearest")
ax[1].plot(vtg[im],vbg[im],"c*",ms=13,label=f"min {Rs[im]:.0f} Ω (just metal)")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 zoom (0–5 kΩ) — no sub-kΩ dome"); ax[1].legend(fontsize=8); plt.colorbar(im1,ax=ax[1])
im2=ax[2].pcolormesh(nn/1e4/1e12,DD/1e9,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[2].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="sr2 4T Rxx (n,D)"); plt.colorbar(im2,ax=ax[2])
plt.tight_layout(); plt.show()
