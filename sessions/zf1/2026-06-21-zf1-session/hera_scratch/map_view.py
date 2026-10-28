import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

r = open_run("data/2")
print(summarize_run(r))
print("interrupted:", r.interrupted)
cfg = json.load(open("data/2/metadata.json"))["measurement_config"]

tg = r.col("k_tg_volt"); bg = r.col("k_bg_volt")
I  = r.col("sr830_1_X")/cfg["sr1_gain"]              # device current (A), actual
V4 = r.col("sr830_3_X")/cfg["sr3_gain"]             # 4T voltage (V)
V2 = r.col("sr830_2_X")/cfg["sr2_gain"]             # 2T voltage (V)
Rxx = V4/I                                          # 4T R using ACTUAL current
R2  = V2/I

N_bg=121; N_tg=81
print("total", len(tg), "expect", N_bg*N_tg)
TG=tg.reshape(N_tg,N_bg); BG=bg.reshape(N_tg,N_bg); RXX=Rxx.reshape(N_tg,N_bg); R2g=R2.reshape(N_tg,N_bg)
II=I.reshape(N_tg,N_bg)
# snake check
print("row0 BG[0],BG[-1]:", BG[0,0], BG[0,-1], " row1:", BG[1,0], BG[1,-1])

fig,ax=plt.subplots(1,3,figsize=(16,5))
im=ax[0].pcolormesh(BG,TG,np.clip(RXX,0,200),shading='auto',cmap='inferno')
ax[0].set_title("4T Rxx (Ω, clip 200)");ax[0].set_xlabel("BG (V)");ax[0].set_ylabel("TG (V)");plt.colorbar(im,ax=ax[0])
im=ax[1].pcolormesh(BG,TG,np.log10(np.clip(RXX,1,1e5)),shading='auto',cmap='inferno')
ax[1].set_title("log10 4T Rxx");ax[1].set_xlabel("BG (V)");plt.colorbar(im,ax=ax[1])
im=ax[2].pcolormesh(BG,TG,II*1e9,shading='auto',cmap='viridis')
ax[2].set_title("device I (nA)");ax[2].set_xlabel("BG (V)");plt.colorbar(im,ax=ax[2])
plt.tight_layout();plt.savefig("hera_scratch/map_view.png",dpi=100)
print("saved map_view.png")
print("Rxx stats: min %.1f  p1 %.1f  median %.1f  max %.0f"%(np.nanmin(Rxx),np.nanpercentile(Rxx,1),np.nanmedian(Rxx),np.nanmax(Rxx)))
