# Run 2+3 — Step-1 pristine-field gatemap, stitched (run 2 rows 0-43 + run 3 rows 44-60).
from scipy.ndimage import gaussian_filter1d, uniform_filter
NF = 101
def Rgrid(g, srtag, nrows):
    mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
    return ((g.col(f"{srtag}_X")/mc[{"sr830_3":"sr3","sr830_2":"sr2"}[srtag]+"_gain"])/Ib)[:nrows*NF].reshape(nrows, NF)

r2, r3 = run(2), run(3); n2 = 44
vtg = np.vstack([r2.col_at(r2.col_indices("k_tg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_tg_volt")[-1]).reshape(17,NF)])
vbg = np.vstack([r2.col_at(r2.col_indices("k_bg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_bg_volt")[-1]).reshape(17,NF)])
R3 = np.vstack([Rgrid(r2,"sr830_3",n2), Rgrid(r3,"sr830_3",17)])   # 4T Rxx, 61x101
tg_axis, bg_axis = vtg[0], vbg[:,0]

# CNP fit + (n,D) reprojection (geometry prior; ratio data-validated, abs scale prior)
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R3[i],2))] for i in range(61)])
ins = (tg_cnp>tg_axis.min()+0.3)&(tg_cnp<tg_axis.max()-0.3)
slope, icpt = np.polyfit(bg_axis[ins], tg_cnp[ins], 1)
n0,_ = cal.n_D(np.array([icpt]), np.array([0.0]))
nn, DD = cal.n_D(vtg.ravel(), vbg.ravel()); nn=(nn-n0[0]).reshape(R3.shape); DD=DD.reshape(R3.shape)
print(f"CNP: Vtg={slope:.3f}*Vbg+{icpt:.3f}  cap ratio c_bg/c_tg={-slope:.3f} (prior 23.6/20=1.18)")
print(f"(n,D) covered: n {nn.min()/1e4/1e12:.1f}..{nn.max()/1e4/1e12:.1f} e12 cm^-2 ; D {DD.min()/1e9:.2f}..{DD.max()/1e9:.2f} V/nm")
R3s = uniform_filter(R3,3); im=np.unravel_index(np.argmin(R3s),R3s.shape)
print(f"metal Rxx ~{np.median(R3[(R3>5)&(R3<60)]):.1f} Ω ; lowest smoothed {R3s[im]:.1f} Ω at "
      f"Vtg={vtg[im]:.2f} Vbg={vbg[im]:.2f} (n={nn[im]/1e4/1e12:.2f}e12, D={DD[im]/1e9:.3f} V/nm)")
print(f"3x3-smoothed Rxx<4 Ω: {(R3s<4).sum()} pts ; <2 Ω: {(R3s<2).sum()} pts (noise floor ~2.6 Ω)")

fig, ax = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Run 2+3 stitched Step-1 gatemap (61x101) — 4T Rxx — B~0 pristine, 0.5 nA, 34 mK")
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R3,-5,80),cmap="viridis",shading="nearest")
ax[0].plot(slope*bg_axis[ins]+icpt,bg_axis[ins],"r-",lw=1,label=f"CNP slope {slope:.2f}")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="4T Rxx (Ω, 0–80)"); ax[0].legend(fontsize=8); plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R3,-3,12),cmap="inferno",shading="nearest")
ax[1].plot(vtg[im],vbg[im],"c*",ms=14,label=f"min {R3s[im]:.1f} Ω")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="4T Rxx zoom (0–12 Ω) — candidate hunt"); ax[1].legend(fontsize=8); plt.colorbar(im1,ax=ax[1])
im2=ax[2].pcolormesh(nn/1e4/1e12,DD/1e9,np.clip(R3,-5,80),cmap="viridis",shading="nearest")
ax[2].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="4T Rxx (n,D) [ratio-valid, abs=prior]"); plt.colorbar(im2,ax=ax[2])
plt.tight_layout(); plt.show()
