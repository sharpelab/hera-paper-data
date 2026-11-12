import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
import scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
r=open_run("data/10"); print(summarize_run(r))
cfg=json.load(open("data/10/metadata.json"))["measurement_config"]
N_tg,N_bg=41,26
tg=r.col("k_tg_volt").reshape(N_tg,N_bg); bg=r.col("k_bg_volt").reshape(N_tg,N_bg)
I=(r.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
X4=r.col("sr830_3_X").reshape(N_tg,N_bg); Rxx=(X4/cfg["sr3_gain"])/I
P4=r.col("sr830_3_P").reshape(N_tg,N_bg)
itg=r.col("k_tg_curr").reshape(N_tg,N_bg); ibg=r.col("k_bg_curr").reshape(N_tg,N_bg)
n=((c_tg*tg+c_bg*bg)/cst.e+n_off)*1e-4; D=(c_tg*tg-c_bg*bg)/(2*cst.epsilon_0)*1e-9

print(f"coverage n=[{n.min()/1e11:+.1f},{n.max()/1e11:+.1f}]e11  D=[{D.min():.3f},{D.max():.3f}] V/nm")
print(f"leakage |I_tg|max={np.nanmax(np.abs(itg)):.1e} |I_bg|max={np.nanmax(np.abs(ibg)):.1e} A")
print(f"Rxx: global min={np.nanmin(Rxx):.2f} Ω  median={np.nanmedian(Rxx):.1f} Ω")
imin=np.unravel_index(np.nanargmin(Rxx),Rxx.shape)
print(f"MIN at TG={tg[imin]:.3f} BG={bg[imin]:.3f}  n={n[imin]/1e11:+.2f}e11 D={D[imin]:.3f} V/nm")
# contiguity: how many pixels below thresholds, and is the min a cluster?
for th in (10,8,6):
    m=Rxx<th
    print(f"  Rxx<{th}Ω: {m.sum()} px")
# region around the min
i0,j0=imin
sub=Rxx[max(0,i0-3):i0+4, max(0,j0-3):j0+4]
print("Rxx (Ω) patch around min:\n", np.array2string(sub,precision=1,suppress_small=True))
print(f"phase at min={P4[imin]:.1f}°  (metallic band median {np.median(P4[(Rxx>15)&(Rxx<40)]):.1f}°)")

fig,ax=plt.subplots(1,2,figsize=(13,5.5))
sc=ax[0].pcolormesh(n/1e11,D,Rxx,shading='auto',cmap='viridis',vmin=0,vmax=25)
ax[0].plot(n[imin]/1e11,D[imin],'r*',ms=18)
ax[0].set(title=f"4T Rxx (Ω) zoom — min {np.nanmin(Rxx):.1f}Ω",xlabel="n(1e11)",ylabel="D(V/nm)");plt.colorbar(sc,ax=ax[0])
# Rxx vs n at the min's D row and neighbors
for di in (-4,-2,0,2,4):
    k=np.clip(i0+di,0,N_tg-1)
    ax[1].plot(n[k]/1e11,Rxx[k],'.-',ms=3,label=f"D~{np.median(D[k]):.3f}")
ax[1].axhline(0,c='gray',lw=.5); ax[1].set(title="Rxx(n) through the spot",xlabel="n(1e11)",ylabel="Rxx(Ω)",ylim=(0,40)); ax[1].legend(fontsize=7)
plt.tight_layout();plt.savefig("hera_scratch/zoom.png",dpi=110);print("saved zoom.png")
