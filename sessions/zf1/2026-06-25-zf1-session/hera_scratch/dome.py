import json, gzip, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=-0.362e11*1e4)

run="data/8"
md=json.load(open(f"{run}/metadata.json")); cols=md["columns"]
p=f"{run}/data.tsv"; f=gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
a=np.genfromtxt(f,delimiter="\t",invalid_raise=False); f.close(); a=a[~np.isnan(a).any(axis=1)]
ix={}; [ix.setdefault(c,j) for j,c in enumerate(cols)]
n,D=cal.n_D(a[:,ix["k_tg_volt"]],a[:,ix["k_bg_volt"]]); n=n/1e4/1e11; D=D/1e9
R3=(a[:,ix["sr830_3_X"]]/100)/1e-9
I=a[:,ix["sr830_1_X"]]/-1e6*1e9

# regular grid for render
ni=np.linspace(-6.5,-3.5,121); Di=np.linspace(-0.66,-0.55,56)
NN,DD=np.meshgrid(ni,Di)
Rg=griddata((n,D),R3,(NN,DD),method="linear")

fig,ax=plt.subplots(1,2,figsize=(15,6))
pc=ax[0].pcolormesh(NN,DD,Rg,shading="auto",cmap="inferno",vmin=0,vmax=40); plt.colorbar(pc,ax=ax[0],label="Rxx (Ω)")
ax[0].set_title("4T Rxx dome (linear, vmax 40Ω)")
# contour of low-R
pc2=ax[1].pcolormesh(NN,DD,Rg,shading="auto",cmap="inferno",vmin=0,vmax=10); plt.colorbar(pc2,ax=ax[1],label="Rxx (Ω)")
try: ax[1].contour(NN,DD,Rg,levels=[2,5],colors=["cyan","white"],linewidths=1)
except Exception: pass
ax[1].set_title("low-R zoom (vmax 10Ω); cyan=2Ω white=5Ω")
for axi in ax:
    axi.set_xlabel("n (1e11 cm^-2)"); axi.set_ylabel("D (V/nm)")
fig.suptitle("zf1 run 8 — SC candidate dome Rxx(n,D)")
fig.tight_layout(); fig.savefig("hera_scratch/dome.png",dpi=110)

# optimum + extent
lowmask = R3 < 2
print(f"points with Rxx<2Ω: {lowmask.sum()}")
if lowmask.sum():
    print(f"  n range [{n[lowmask].min():.2f},{n[lowmask].max():.2f}]e11, D range [{D[lowmask].min():.3f},{D[lowmask].max():.3f}]")
jm=np.argmin(R3)
print(f"GLOBAL min Rxx={R3[jm]:.2f}Ω at n={n[jm]:.2f}e11, D={D[jm]:.3f}, V=({a[jm,ix['k_tg_volt']]:+.3f},{a[jm,ix['k_bg_volt']]:+.3f}), I={I[jm]:.3f}nA")
# dome optimum: centroid of Rxx<2 region
if lowmask.sum():
    print(f"  Rxx<2 centroid: n={n[lowmask].mean():.2f}e11, D={D[lowmask].mean():.3f}")
# Rxx<5 extent in n at the most-negative accessible D
for Dtarget in [-0.66,-0.65,-0.64,-0.62,-0.60]:
    sel=np.abs(D-Dtarget)<0.006
    if sel.any():
        rr=R3[sel]; nn=n[sel]; o=np.argsort(nn)
        lo=nn[rr<5]
        print(f"  D≈{Dtarget}: min Rxx {rr.min():.1f}Ω; Rxx<5Ω over n=[{lo.min():.2f},{lo.max():.2f}]" if (rr<5).any() else f"  D≈{Dtarget}: min Rxx {rr.min():.1f}Ω (no <5Ω)")
print("saved hera_scratch/dome.png")
