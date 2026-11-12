import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, uniform_filter
from hera.analysis import open_run, summarize_run, GateCalibration

g = open_run("data/4")
print(summarize_run(g)); print("interrupted:", g.interrupted)
mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
NF = 101; nr = g.rows // NF
vtg = g.col_at(g.col_indices("k_tg_volt")[-1])[:nr*NF].reshape(nr, NF)
vbg = g.col_at(g.col_indices("k_bg_volt")[-1])[:nr*NF].reshape(nr, NF)
R = ((g.col("sr830_2_X")/mc["sr2_gain"])/Ib)[:nr*NF].reshape(nr, NF)   # sr2 4T Rxx
tg_axis, bg_axis = vtg[0], vbg[:,0]
print(f"grid {R.shape}  TG {tg_axis.min():.1f}..{tg_axis.max():.1f}  BG {bg_axis.min():.1f}..{bg_axis.max():.1f}")

itg = np.abs(g.col("k_tg_curr")); ibg = np.abs(g.col("k_bg_curr"))
print(f"leakage |I_tg|max {itg.max()*1e12:.0f} pA  |I_bg|max {ibg.max()*1e12:.0f} pA")

# candidate scan: any sub-kΩ / Rxx->0 ?
Rs = uniform_filter(R, 3)
print(f"\nsr2 4T Rxx: full {R.min():.0f}..{R.max():.0f} Ω  median {np.median(R):.0f} Ω")
for thr in (3000, 2000, 1000, 500):
    print(f"  3x3-smoothed Rxx < {thr} Ω: {(Rs<thr).sum()} pts ({100*(Rs<thr).sum()/R.size:.2f}%)")
im = np.unravel_index(np.argmin(Rs), Rs.shape)
print(f"  lowest smoothed Rxx {Rs[im]:.0f} Ω at Vtg={vtg[im]:.2f} Vbg={vbg[im]:.2f}")

# CNP + (n,D)
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R[i],2))] for i in range(nr)])
ins = (tg_cnp>tg_axis.min()+0.3)&(tg_cnp<tg_axis.max()-0.3)
slope,icpt = np.polyfit(bg_axis[ins], tg_cnp[ins], 1)
n0,_ = cal.n_D(np.array([icpt]),np.array([0.0]))
nn,DD = cal.n_D(vtg.ravel(),vbg.ravel()); nn=(nn-n0[0]).reshape(R.shape); DD=DD.reshape(R.shape)
print(f"(n,D) covered: n {nn.min()/1e4/1e12:.1f}..{nn.max()/1e4/1e12:.1f} e12 cm^-2 ; D {DD.min()/1e9:.2f}..{DD.max()/1e9:.2f} V/nm")
print(f"  lowest-Rxx pt: n={nn[im]/1e4/1e12:.2f}e12, D={DD[im]/1e9:.3f} V/nm")

fig,ax=plt.subplots(1,3,figsize=(18,5))
fig.suptitle("SC zoom: V_bg>0/V_tg<0 quadrant (0.07 V) — 4T Rxx sr2 — B~0 nominal (~2 mT trapped), 0.5 nA, 34 mK")
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[0].plot(slope*bg_axis[ins]+icpt,bg_axis[ins],"r-",lw=1,label=f"CNP slope {slope:.2f}")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 4T Rxx (kΩ, 0–30)"); ax[0].legend(fontsize=8); plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,4),cmap="inferno",shading="nearest")
ax[1].plot(vtg[im],vbg[im],"c*",ms=13,label=f"min {Rs[im]:.0f} Ω")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 zoom (0–4 kΩ) — candidate hunt"); ax[1].legend(fontsize=8); plt.colorbar(im1,ax=ax[1])
im2=ax[2].pcolormesh(nn/1e4/1e12,DD/1e9,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[2].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="sr2 4T Rxx (n,D)"); plt.colorbar(im2,ax=ax[2])
plt.tight_layout(); plt.savefig("hera_scratch/zoom_map.png",dpi=110); print("\nsaved hera_scratch/zoom_map.png")
