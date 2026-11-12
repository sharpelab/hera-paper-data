import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run
import scipy.constants as cst

r=open_run("data/2"); cfg=json.load(open("data/2/metadata.json"))["measurement_config"]
N_bg,N_tg=121,81
TG=r.col("k_tg_volt").reshape(N_tg,N_bg); BG=r.col("k_bg_volt").reshape(N_tg,N_bg)
I=(r.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
X4=r.col("sr830_3_X").reshape(N_tg,N_bg); V4=X4/cfg["sr3_gain"]
Rxx=V4/I
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
n=((c_tg*TG+c_bg*BG)/cst.e+n_off)*1e-4; D=((c_tg*TG-c_bg*BG)/(2*cst.epsilon_0))*1e-9
clip=np.abs(X4)>5e-6*0.98

print(f"clipped fraction: {clip.mean()*100:.0f}%")
print(f"UNCLIPPED Rxx: min={np.nanmin(Rxx[~clip]):.1f}  p1={np.nanpercentile(Rxx[~clip],1):.1f}  median={np.nanmedian(Rxx[~clip]):.1f} Ω")
# genuine low-Rxx away from CNP (|n|>0.5e11) and unclipped
offcnp=(~clip)&(np.abs(n)>0.5e11)
lowmask=offcnp&(Rxx<8)
print(f"genuine low-Rxx (<8Ω, unclipped, off-CNP): {lowmask.sum()} pts")
if lowmask.sum():
    print(f"  at n=[{n[lowmask].min()/1e11:+.1f},{n[lowmask].max()/1e11:+.1f}]e11 D=[{D[lowmask].min():+.2f},{D[lowmask].max():+.2f}]")
# where is the device most conducting on the hole side at high |D|?
hole=(n<-2e11)&(np.abs(D)>0.4)&(~clip)
print(f"hole-side high|D| unclipped: {hole.sum()} pts, Rxx min={np.nanmin(Rxx[hole]) if hole.sum() else float('nan'):.1f} median={np.nanmedian(Rxx[hole]) if hole.sum() else float('nan'):.1f}")

fig,ax=plt.subplots(1,2,figsize=(13,5.5))
Rm=np.where(clip,np.nan,Rxx)
sc=ax[0].scatter(n.ravel()/1e11,D.ravel(),c=np.clip(Rm.ravel(),0,50),s=7,cmap='viridis')
ax[0].set(title="Rxx (Ω) unclipped only (clipped=white)",xlabel="n(1e11)",ylabel="D(V/nm)");plt.colorbar(sc,ax=ax[0])
ax[0].axhline(0,c='k',lw=.3);ax[0].axvline(0,c='k',lw=.3)
# clip mask map
sc=ax[1].scatter(n.ravel()/1e11,D.ravel(),c=clip.ravel().astype(float),s=7,cmap='Reds')
ax[1].set(title="clipped (Rxx>~50Ω) = red",xlabel="n(1e11)",ylabel="D(V/nm)");plt.colorbar(sc,ax=ax[1])
plt.tight_layout();plt.savefig("hera_scratch/map_lowR.png",dpi=100);print("saved map_lowR.png")
