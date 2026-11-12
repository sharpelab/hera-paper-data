import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, uniform_filter
from hera.analysis import open_run, GateCalibration

NF = 101
def grid(run, name, nrows):
    g = run
    col = (g.col(name + "_X")/g.meta["measurement_config"][{"sr830_3":"sr3","sr830_2":"sr2","sr830_1":"sr1"}[name]+"_gain"])
    Ib = g.meta["measurement_config"]["bias_voltage_1"]/g.meta["measurement_config"]["bias_resistor"]
    R = (col/Ib)[:nrows*NF].reshape(nrows, NF)
    return R

r2 = open_run("data/2"); r3 = open_run("data/3")
n2 = 44  # complete rows of run 2
vtg2 = r2.col_at(r2.col_indices("k_tg_volt")[-1])[:n2*NF].reshape(n2, NF)
vbg2 = r2.col_at(r2.col_indices("k_bg_volt")[-1])[:n2*NF].reshape(n2, NF)
vtg3 = r3.col_at(r3.col_indices("k_tg_volt")[-1]).reshape(17, NF)
vbg3 = r3.col_at(r3.col_indices("k_bg_volt")[-1]).reshape(17, NF)

R3 = np.vstack([grid(r2,"sr830_3",n2), grid(r3,"sr830_3",17)])   # 4T Rxx, 61x101
R2 = np.vstack([grid(r2,"sr830_2",n2), grid(r3,"sr830_2",17)])   # 2T
vtg = np.vstack([vtg2, vtg3]); vbg = np.vstack([vbg2, vbg3])
tg_axis = vtg[0]; bg_axis = vbg[:,0]
print(f"full map: {R3.shape}  TG {tg_axis.min():.1f}..{tg_axis.max():.1f}  BG {bg_axis.min():.1f}..{bg_axis.max():.1f}")

# CNP fit (full)
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R3[i],2))] for i in range(R3.shape[0])])
inside = (tg_cnp > tg_axis.min()+0.3) & (tg_cnp < tg_axis.max()-0.3)
slope, icpt = np.polyfit(bg_axis[inside], tg_cnp[inside], 1)
print(f"CNP (full): Vtg = {slope:.3f}*Vbg + {icpt:.3f}  ({inside.sum()}/61 rows)  cap ratio {-slope:.3f}")

# (n,D) reprojection — geometry prior; n_offset so CNP -> n=0
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
nn, DD = cal.n_D(vtg.ravel(), vbg.ravel())
nn = nn.reshape(R3.shape); DD = DD.reshape(R3.shape)
# n offset from CNP line (Vtg=icpt at Vbg=0)
n0, _ = cal.n_D(np.array([icpt]), np.array([0.0]))
nn = nn - n0[0]
print(f"(n,D) covered: n {nn.min()/1e16:.2f}..{nn.max()/1e16:.2f} e16 m^-2 ({nn.min()/1e4/1e12:.2f}..{nn.max()/1e4/1e12:.2f} e12 cm^-2)")
print(f"               D {DD.min()/1e9:.2f}..{DD.max()/1e9:.2f} GV/m ({DD.min()/1e9*1e-9*1e9:.3f} ..)")  # V/nm below
print(f"               D {DD.min()/1e9:.3f}..{DD.max()/1e9:.3f} V/nm")

# candidate scan
print("\n=== candidate scan (full map) ===")
metal = np.median(R3[(R3>5)&(R3<60)])
print(f"metal Rxx ~{metal:.1f} Ω; run1 noise floor ~2.6 Ω")
R3s = uniform_filter(R3, size=3)
for thr in (6,4,2):
    m = R3s < thr
    print(f"  3x3-smoothed Rxx < {thr} Ω: {m.sum()} pts ({100*m.sum()/R3.size:.2f}%)")
imin = np.unravel_index(np.argmin(R3s), R3s.shape)
print(f"  lowest smoothed Rxx {R3s[imin]:.1f} Ω at Vtg={vtg[imin]:.2f} Vbg={vbg[imin]:.2f} (n={nn[imin]/1e4/1e12:.2f}e12 cm^-2, D={DD[imin]/1e9:.3f} V/nm)")

# render full
fig, ax = plt.subplots(1, 3, figsize=(19,5.5))
fig.suptitle("Run 2+3 stitched Step-1 gatemap (61x101, full box) — 4T Rxx — B~0, 0.5 nA, 34 mK", y=1.02)
im0=ax[0].pcolormesh(tg_axis,bg_axis,np.clip(R3,-5,80),cmap="viridis",shading="nearest")
ax[0].plot(slope*bg_axis[inside]+icpt,bg_axis[inside],"r-",lw=1,label=f"CNP slope {slope:.2f}")
ax[0].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="4T Rxx (Ω, 0–80)"); ax[0].legend(fontsize=8)
plt.colorbar(im0,ax=ax[0])
im1=ax[1].pcolormesh(tg_axis,bg_axis,np.clip(R3,-3,12),cmap="inferno",shading="nearest")
ax[1].set(xlabel="k_tg (V)",ylabel="k_bg (V)",title="4T Rxx zoom (0–12 Ω) — candidate hunt"); plt.colorbar(im1,ax=ax[1])
im2=ax[2].pcolormesh(nn/1e4/1e12,DD/1e9,np.clip(R3,-5,80),cmap="viridis",shading="nearest")
ax[2].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="4T Rxx in (n,D) [prior scale]"); plt.colorbar(im2,ax=ax[2])
plt.tight_layout(); plt.savefig("hera_scratch/full_map.png",dpi=110,bbox_inches="tight")
print("\nsaved hera_scratch/full_map.png")
