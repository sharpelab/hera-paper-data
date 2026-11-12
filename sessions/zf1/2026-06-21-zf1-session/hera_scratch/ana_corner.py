import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
from scipy.ndimage import gaussian_filter
import scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e

r=open_run("data/9"); print(summarize_run(r))
cfg=json.load(open("data/9/metadata.json"))["measurement_config"]
N_tg,N_bg=51,49
tg=r.col("k_tg_volt").reshape(N_tg,N_bg); bg=r.col("k_bg_volt").reshape(N_tg,N_bg)
I=(r.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
X4=r.col("sr830_3_X").reshape(N_tg,N_bg); Rxx=(X4/cfg["sr3_gain"])/I
itg=r.col("k_tg_curr").reshape(N_tg,N_bg); ibg=r.col("k_bg_curr").reshape(N_tg,N_bg)
n=((c_tg*tg+c_bg*bg)/cst.e+n_off)*1e-4; D=(c_tg*tg-c_bg*bg)/(2*cst.epsilon_0)*1e-9
clip=np.abs(X4)>2e-4*0.98

print(f"D range [{D.min():.3f},{D.max():.3f}] V/nm ; n range [{n.min()/1e11:+.1f},{n.max()/1e11:+.1f}]e11")
print(f"LEAKAGE |I_tg|max={np.nanmax(np.abs(itg)):.2e} |I_bg|max={np.nanmax(np.abs(ibg)):.2e} A")
print(f"clipped(>~2kΩ): {clip.mean()*100:.0f}%")
print(f"Rxx: GLOBAL MIN={np.nanmin(Rxx):.1f} Ω  p1={np.nanpercentile(Rxx,1):.1f}  median={np.nanmedian(Rxx):.0f}")
# hunt: lowest-Rxx points and where they are
lowm=Rxx<10
print(f"points Rxx<10Ω: {lowm.sum()}  ; Rxx<5Ω: {(Rxx<5).sum()}")
if lowm.sum():
    print(f"  low-Rxx at n=[{n[lowm].min()/1e11:+.1f},{n[lowm].max()/1e11:+.1f}]e11 D=[{D[lowm].min():.2f},{D[lowm].max():.2f}]")
# residual to expose local dips
Rc=np.clip(Rxx,0,500); Rs=gaussian_filter(Rc,2); dR=Rc-Rs
print(f"most negative residual (deepest local dip): {np.nanmin(dR):.1f} Ω at "
      f"n={n.ravel()[np.nanargmin(dR)]/1e11:+.1f}e11 D={D.ravel()[np.nanargmin(dR)]:.2f}")

fig,ax=plt.subplots(1,3,figsize=(17,5))
sc=ax[0].scatter(n.ravel()/1e11,D.ravel(),c=np.clip(Rxx.ravel(),0,150),s=14,cmap='inferno')
ax[0].set(title="4T Rxx (Ω, clip 150) — extremal-D wedge",xlabel="n(1e11)",ylabel="D(V/nm)");plt.colorbar(sc,ax=ax[0])
sc=ax[1].scatter(n.ravel()/1e11,D.ravel(),c=dR.ravel(),s=14,cmap='coolwarm',vmin=-25,vmax=25)
ax[1].set(title="Rxx - smooth (local dip=blue)",xlabel="n(1e11)");plt.colorbar(sc,ax=ax[1])
sc=ax[2].scatter(n.ravel()/1e11,D.ravel(),c=(np.abs(itg)*1e12).ravel(),s=14,cmap='viridis')
ax[2].set(title="|I_tg| leak (pA)",xlabel="n(1e11)");plt.colorbar(sc,ax=ax[2])
plt.tight_layout();plt.savefig("hera_scratch/corner.png",dpi=100);print("saved corner.png")
