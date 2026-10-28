import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration
g=open_run("data/8"); mc=g.meta["measurement_config"]; Ib=mc["bias_voltage_1"]/mc["bias_resistor"]
vtg=g.col_at(g.col_indices("k_tg_volt")[-1]); vbg=g.col_at(g.col_indices("k_bg_volt")[-1])
cal=GateCalibration.from_thicknesses(23.6e-9,20e-9,0); nn,DD=cal.n_D(vtg,vbg); nn=nn/1e4/1e12; DD=DD/1e9
R2=(g.col("sr830_2_X")/mc["sr2_gain"])/Ib
X3=(g.col("sr830_3_X")/mc["sr3_gain"])/Ib; P3=g.col("sr830_3_P")
mag3=np.abs((g.col("sr830_3_X")/mc["sr3_gain"])/np.cos(np.deg2rad(P3)))/Ib

# D = -0.66 row (the dip's D)
row=np.abs(DD+0.66)<0.003
o=np.argsort(nn[row]); x=nn[row][o]
fig,ax1=plt.subplots(figsize=(9,5.5))
fig.suptitle("Run 8, D=-0.66 cut — where sr3 dips, the true 4T Rxx (sr2) is HIGH -> not SC")
l1,=ax1.plot(x,R2[row][o]/1e3,".-",color="C0",label="sr2 = 4T Rxx (kΩ)  [trusted]")
ax1.set_xlabel("n (e12 cm$^{-2}$)"); ax1.set_ylabel("sr2 4T Rxx (kΩ)",color="C0"); ax1.tick_params(axis='y',labelcolor="C0")
ax1.axvline(-0.487,color="gray",ls=":")
ax2=ax1.twinx()
l2,=ax2.plot(x,X3[row][o],".-",color="C3",label="sr3 X (Ω)")
l3,=ax2.plot(x,mag3[row][o],".-",color="C1",alpha=0.6,label="sr3 |mag| (Ω)")
ax2.set_ylabel("sr3 (Ω)",color="C3"); ax2.tick_params(axis='y',labelcolor="C3")
ax1.legend(handles=[l1,l2,l3],fontsize=9,loc="upper left"); ax1.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("hera_scratch/dip_verdict.png",dpi=120)
i=np.argmin(X3[row][o])
print(f"at sr3-X min (n={x[i]:.3f}): sr3 X={X3[row][o][i]:.1f}Ω, sr3 mag={mag3[row][o][i]:.1f}Ω, sr2 4T={R2[row][o][i]/1e3:.1f}kΩ")
print("saved dip_verdict.png")
