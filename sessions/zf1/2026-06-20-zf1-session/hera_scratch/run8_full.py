import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration
g = open_run("data/8"); mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
vtg = g.col_at(g.col_indices("k_tg_volt")[-1]); vbg = g.col_at(g.col_indices("k_bg_volt")[-1])
R2 = (g.col("sr830_2_X")/mc["sr2_gain"])/Ib; R3 = (g.col("sr830_3_X")/mc["sr3_gain"])/Ib
cal = GateCalibration.from_thicknesses(23.6e-9,20e-9,0)
nn,DD = cal.n_D(vtg,vbg); nn=nn/1e4/1e12; DD=DD/1e9
ndip, Ddip = -0.4654, -0.6501
print(f"run 8: {g.rows} pts ; n {nn.min():.2f}..{nn.max():.2f} ; D {DD.min():.3f}..{DD.max():.3f}")
print(f"sr2: min {R2.min():.0f} Ω, median {np.median(R2):.0f} Ω")
print(f"sr3: min {R3.min():.1f} Ω, median {np.median(R3):.1f} Ω")
for thr in (5000,3000,2000): print(f"  sr2<{thr}Ω: {(R2<thr).sum()} ({100*(R2<thr).mean():.1f}%)")
for thr in (10,5,2): print(f"  sr3<{thr}Ω: {(R3<thr).sum()} ({100*(R3<thr).mean():.1f}%)")

# where is sr3 lowest? (localized vs band) — look at the lowest-sr3 cluster extent
lowm = R3 < 8
if lowm.sum():
    print(f"sr3<8Ω region: n {nn[lowm].min():.3f}..{nn[lowm].max():.3f} ({(nn[lowm].max()-nn[lowm].min()):.3f} wide), "
          f"D {DD[lowm].min():.3f}..{DD[lowm].max():.3f}")

fig,ax=plt.subplots(1,2,figsize=(15,5.5))
fig.suptitle("Run 8 — 8h nD-map (20572 pts) — SC-candidate extent — B~0 nominal, 0.5 nA, 34 mK")
s0=ax[0].scatter(nn,DD,c=np.clip(R2/1e3,0,20),s=4,cmap="inferno"); plt.colorbar(s0,ax=ax[0],label="Rxx2 (kΩ)")
ax[0].plot(ndip,Ddip,"c+",ms=14,mew=2,label="run-5 dip"); ax[0].legend(fontsize=8,loc="upper right")
ax[0].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="sr2 4T Rxx (0–20 kΩ)")
s1=ax[1].scatter(nn,DD,c=np.clip(R3,0,40),s=4,cmap="inferno"); plt.colorbar(s1,ax=ax[1],label="Rxx3 (Ω)")
ax[1].plot(ndip,Ddip,"c+",ms=14,mew=2); ax[1].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="sr3 marker (0–40 Ω)")
plt.tight_layout(); plt.savefig("hera_scratch/run8_full.png",dpi=115); print("saved run8_full.png")
