import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, uniform_filter
from hera.analysis import open_run, GateCalibration

NF = 101
def Rgrid(g, srtag, gainkey, nrows):
    mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
    return ((g.col(f"{srtag}_X")/mc[gainkey])/Ib)[:nrows*NF].reshape(nrows, NF)

r2, r3 = open_run("data/2"), open_run("data/3"); n2 = 44
vtg = np.vstack([r2.col_at(r2.col_indices("k_tg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_tg_volt")[-1]).reshape(17,NF)])
vbg = np.vstack([r2.col_at(r2.col_indices("k_bg_volt")[-1])[:n2*NF].reshape(n2,NF),
                 r3.col_at(r3.col_indices("k_bg_volt")[-1]).reshape(17,NF)])
# *** 4T Rxx = sr830_2 (operator correction 2026-06-20) ***
R = np.vstack([Rgrid(r2,"sr830_2","sr2_gain",n2), Rgrid(r3,"sr830_2","sr2_gain",17)])
tg_axis, bg_axis = vtg[0], vbg[:,0]
print(f"sr2 (4T Rxx) grid {R.shape}  range {R.min():.0f}..{R.max():.0f} Ω  median {np.median(R):.0f} Ω")

# CNP fit on sr2
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R[i],2))] for i in range(61)])
ins = (tg_cnp>tg_axis.min()+0.3)&(tg_cnp<tg_axis.max()-0.3)
slope, icpt = np.polyfit(bg_axis[ins], tg_cnp[ins], 1)
print(f"CNP (sr2): Vtg={slope:.3f}*Vbg+{icpt:.3f}  ({ins.sum()}/61)  cap ratio {-slope:.3f} (prior 1.18)")

cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
n0,_ = cal.n_D(np.array([icpt]), np.array([0.0]))
nn, DD = cal.n_D(vtg.ravel(), vbg.ravel()); nn=(nn-n0[0]).reshape(R.shape); DD=DD.reshape(R.shape)

# candidate scan: look for sr2 collapsing toward 0 (SC), well below the kΩ metal
metal = np.median(R[(R>500)&(R<8000)])
print(f"\nmetal Rxx (sr2) ~{metal:.0f} Ω")
Rs = uniform_filter(R, 3)
for thr in (2000, 1000, 500, 200):
    m = Rs < thr
    print(f"  3x3-smoothed sr2 < {thr} Ω: {m.sum()} pts ({100*m.sum()/R.size:.2f}%)")
im = np.unravel_index(np.argmin(Rs), Rs.shape)
print(f"  lowest smoothed sr2 = {Rs[im]:.0f} Ω at Vtg={vtg[im]:.2f} Vbg={vbg[im]:.2f} "
      f"(n={nn[im]/1e4/1e12:.2f}e12 cm^-2, D={DD[im]/1e9:.3f} V/nm)")
print(f"  (SC would show sr2 -> ~0, well below the ~{metal:.0f} Ω metal)")

fig, ax = plt.subplots(1,3, figsize=(18,5))
fig.suptitle("Run 2+3 Step-1 gatemap — 4T Rxx = sr830_2 (corrected) — B~0, 0.5 nA, 34 mK")
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[0].plot(slope*bg_axis[ins]+icpt,bg_axis[ins],"r-",lw=1,label=f"CNP slope {slope:.2f}")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 4T Rxx (kΩ, 0–30)"); ax[0].legend(fontsize=8); plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R/1e3,0,5),cmap="inferno",shading="nearest")
ax[1].plot(vtg[im],vbg[im],"c*",ms=14,label=f"min {Rs[im]:.0f} Ω")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="sr2 zoom (0–5 kΩ) — candidate hunt"); ax[1].legend(fontsize=8); plt.colorbar(im1,ax=ax[1])
im2=ax[2].pcolormesh(nn/1e4/1e12,DD/1e9,np.clip(R/1e3,0,30),cmap="viridis",shading="nearest")
ax[2].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="sr2 4T Rxx (n,D)"); plt.colorbar(im2,ax=ax[2])
plt.tight_layout(); plt.savefig("hera_scratch/full_map_sr2.png",dpi=110); print("\nsaved hera_scratch/full_map_sr2.png")
