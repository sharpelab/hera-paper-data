import json, scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
g=run(10); cfg=json.load(open(Path(file_path)/"10"/"metadata.json"))["measurement_config"]
N_tg,N_bg=41,26
tg=g.col("k_tg_volt").reshape(N_tg,N_bg); bg=g.col("k_bg_volt").reshape(N_tg,N_bg)
I=(g.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
Rxx=(g.col("sr830_3_X").reshape(N_tg,N_bg)/cfg["sr3_gain"])/I
n=((c_tg*tg+c_bg*bg)/cst.e+n_off)*1e-4; D=(c_tg*tg-c_bg*bg)/(2*cst.epsilon_0)*1e-9
im=np.unravel_index(np.nanargmin(Rxx),Rxx.shape)
print(f"arc min Rxx={np.nanmin(Rxx):.2f} Ω at n={n[im]/1e11:+.2f}e11 D={D[im]:.3f} V/nm (TG={tg[im]:.3f} BG={bg[im]:.3f})")
print(f"pixels <6 Ω: {(Rxx<6).sum()}; <10 Ω: {(Rxx<10).sum()} (contiguous arc)")
fig,ax=plt.subplots(1,2,figsize=(13,5))
sc=ax[0].pcolormesh(n/1e11,D,np.clip(Rxx,0,25),shading='auto',cmap='viridis')
ax[0].plot(n[im]/1e11,D[im],'r*',ms=18,label='min 0.6 Ω')
ax[0].set(title="4T Rxx (Ω, 0-25) zoom — low-Rxx arc",xlabel="n(1e11)",ylabel="D(V/nm)");ax[0].legend();plt.colorbar(sc,ax=ax[0])
for di in (-3,0,3):
    k=np.clip(im[0]+di,0,N_tg-1); ax[1].plot(n[k]/1e11,Rxx[k],'.-',ms=3,label=f"D~{np.median(D[k]):.3f}")
ax[1].set(title="Rxx(n) through the arc",xlabel="n(1e11)",ylabel="Rxx(Ω)",ylim=(0,40));ax[1].legend(fontsize=8);ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout(); plt.show()
