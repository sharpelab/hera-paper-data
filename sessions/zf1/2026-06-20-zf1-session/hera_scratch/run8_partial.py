import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration
g = open_run("data/8"); mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
vtg = g.col_at(g.col_indices("k_tg_volt")[-1]); vbg = g.col_at(g.col_indices("k_bg_volt")[-1])
R2 = (g.col("sr830_2_X")/mc["sr2_gain"])/Ib; R3 = (g.col("sr830_3_X")/mc["sr3_gain"])/Ib
cal = GateCalibration.from_thicknesses(23.6e-9,20e-9,0)
nn,DD = cal.n_D(vtg,vbg); nn=nn/1e4/1e12; DD=DD/1e9
print(f"run 8 partial: {g.rows} pts ; D mapped {DD.min():.3f}..{DD.max():.3f} ; n {nn.min():.3f}..{nn.max():.3f}")
print(f"sr2 min {R2.min():.0f} Ω ; sr3 min {R3.min():.1f} Ω ; pts sr2<5kΩ:{(R2<5000).sum()} sr3<8Ω:{(R3<8).sum()}")

fig,ax=plt.subplots(1,2,figsize=(14,5))
fig.suptitle(f"Run 8 partial ({g.rows} pts, D {DD.min():.3f}..{DD.max():.3f}) — does the dip reproduce in 2D?")
s0=ax[0].scatter(nn,DD,c=np.clip(R2/1e3,0,25),s=7,cmap="inferno"); plt.colorbar(s0,ax=ax[0],label="Rxx2 kΩ")
ax[0].plot(-0.523,-0.65,"c+",ms=12,mew=2); ax[0].set(xlabel="n",ylabel="D",title="sr2 (clip 0-25 kΩ)")
s1=ax[1].scatter(nn,DD,c=np.clip(R3,0,50),s=7,cmap="inferno"); plt.colorbar(s1,ax=ax[1],label="Rxx3 Ω")
ax[1].plot(-0.523,-0.65,"c+",ms=12,mew=2); ax[1].set(xlabel="n",ylabel="D",title="sr3 (clip 0-50 Ω)")
plt.tight_layout(); plt.savefig("hera_scratch/run8_partial.png",dpi=110)

# nearest mapped D-row to -0.65: extract its n-cut
row = (np.abs(DD+0.65)<0.003)
if row.sum()>5:
    o=np.argsort(nn[row]); ncut=nn[row][o]; r3cut=R3[row][o]; r2cut=R2[row][o]
    i=np.argmin(r3cut)
    print(f"D=-0.65 cut ({row.sum()} pts): sr3 min {r3cut[i]:.1f} Ω at n={ncut[i]:.3f} (run5 dip: 5.7 Ω at n=-0.52)")
print("saved run8_partial.png")
