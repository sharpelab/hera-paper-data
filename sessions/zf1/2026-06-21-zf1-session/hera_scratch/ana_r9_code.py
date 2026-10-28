import json, scipy.constants as cst
from scipy.ndimage import gaussian_filter
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
g=run(9); cfg=json.load(open(Path(file_path)/"9"/"metadata.json"))["measurement_config"]
N_tg,N_bg=51,49
tg=g.col("k_tg_volt").reshape(N_tg,N_bg); bg=g.col("k_bg_volt").reshape(N_tg,N_bg)
I=(g.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
Rxx=(g.col("sr830_3_X").reshape(N_tg,N_bg)/cfg["sr3_gain"])/I
n=((c_tg*tg+c_bg*bg)/cst.e+n_off)*1e-4; D=(c_tg*tg-c_bg*bg)/(2*cst.epsilon_0)*1e-9
print(f"coverage: D=[{D.min():.3f},{D.max():.3f}] V/nm  n=[{n.min()/1e11:+.0f},{n.max()/1e11:+.0f}]e11")
print(f"leakage |I_tg|max={np.nanmax(np.abs(g.col('k_tg_curr'))):.1e} A; Rxx global min={np.nanmin(Rxx):.1f} Ω")
low=Rxx<10
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
sc=ax[0].scatter(n.ravel()/1e11,D.ravel(),c=np.clip(Rxx.ravel(),0,30),s=16,cmap='viridis')
ax[0].scatter(n[low]/1e11,D[low],s=55,facecolors='none',edgecolors='r',label='Rxx<10Ω')
ax[0].scatter([-5],[-0.67],marker='*',s=220,c='cyan',edgecolors='k',label='candidate')
ax[0].set(title="4T Rxx (Ω, 0-30) — extremal-D wedge",xlabel="n(1e11)",ylabel="D(V/nm)");ax[0].legend();plt.colorbar(sc,ax=ax[0])
Rc=np.clip(Rxx,0,500); dR=Rc-gaussian_filter(Rc,2)
sc=ax[1].scatter(n.ravel()/1e11,D.ravel(),c=dR.ravel(),s=16,cmap='coolwarm',vmin=-15,vmax=15)
ax[1].set(title="Rxx − smooth (local dip=blue)",xlabel="n(1e11)");plt.colorbar(sc,ax=ax[1])
plt.tight_layout(); plt.show()
