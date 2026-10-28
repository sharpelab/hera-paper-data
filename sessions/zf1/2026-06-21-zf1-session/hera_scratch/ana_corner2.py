import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run
import scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
r=open_run("data/9"); cfg=json.load(open("data/9/metadata.json"))["measurement_config"]
N_tg,N_bg=51,49
tg=r.col("k_tg_volt").reshape(N_tg,N_bg); bg=r.col("k_bg_volt").reshape(N_tg,N_bg)
I=(r.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
X4=r.col("sr830_3_X").reshape(N_tg,N_bg); Rxx=(X4/cfg["sr3_gain"])/I
P4=r.col("sr830_3_P").reshape(N_tg,N_bg)
n=((c_tg*tg+c_bg*bg)/cst.e+n_off)*1e-4; D=(c_tg*tg-c_bg*bg)/(2*cst.epsilon_0)*1e-9

# the sub-10Ohm points: are they contiguous and is phase sane?
low=np.argwhere(Rxx<10)
print("sub-10Ω points (row,col): n(e11) D(V/nm) Rxx(Ω) phase(deg)")
for i,j in low:
    print(f"  ({i:2d},{j:2d})  n={n[i,j]/1e11:+5.1f}  D={D[i,j]:+.2f}  Rxx={Rxx[i,j]:5.1f}  P={P4[i,j]:+6.1f}")
# compare: typical metallic phase (median over Rxx 15-40Ω band)
band=(Rxx>15)&(Rxx<40)
print(f"\nmetallic-band phase median={np.median(P4[band]):.1f}° (low-R points should match if real)")
# deep-hole vs candidate-n low points
print(f"min Rxx at n>-8e11 (candidate-ish): {np.nanmin(Rxx[n>-8e11]):.1f} Ω")
print(f"min Rxx at n<-12e11 (deep hole metal): {np.nanmin(Rxx[n<-12e11]):.1f} Ω")

# zoomed map, fine scale 0-30
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
sc=ax[0].scatter(n.ravel()/1e11,D.ravel(),c=np.clip(Rxx.ravel(),0,30),s=22,cmap='viridis')
ax[0].scatter(n[Rxx<10]/1e11,D[Rxx<10],s=60,facecolors='none',edgecolors='r',label='Rxx<10Ω')
ax[0].set(title="Rxx (Ω, 0-30) extremal-D wedge",xlabel="n(1e11)",ylabel="D(V/nm)");ax[0].legend();plt.colorbar(sc,ax=ax[0])
# Rxx vs n colored by D
for k in range(0,N_tg,8):
    ax[1].plot(n[k]/1e11,Rxx[k],'-',lw=1,label=f"D~{np.median(D[k]):.2f}")
ax[1].set(title="Rxx(n) per TG row",xlabel="n(1e11)",ylabel="Rxx(Ω)",ylim=(0,80));ax[1].legend(fontsize=7);ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout();plt.savefig("hera_scratch/corner2.png",dpi=110);print("saved corner2.png")
