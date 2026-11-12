"""Full analysis of survey gatemap run 4: verify, CNP-slope fit, (n,D) render."""
import json, gzip, os
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import GateCalibration

RUN = "data/4"

def load(run):
    md = json.load(open(f"{run}/metadata.json")); cols = md["columns"]
    p = f"{run}/data.tsv"
    f = gzip.open(p+".gz", "rt") if os.path.exists(p+".gz") else open(p)
    a = np.genfromtxt(f, delimiter="\t", invalid_raise=False); f.close()
    a = a[~np.isnan(a).any(axis=1)]
    ix = {}; [ix.setdefault(c, j) for j, c in enumerate(cols)]
    return a, ix

a, ix = load(RUN)
vtg = a[:, ix["k_tg_volt"]]; vbg = a[:, ix["k_bg_volt"]]
itg = a[:, ix["k_tg_curr"]]; ibg = a[:, ix["k_bg_curr"]]
x1 = a[:, ix["sr830_1_X"]]; x2 = a[:, ix["sr830_2_X"]]; x3 = a[:, ix["sr830_3_X"]]
R2 = (x2/100)/1e-9; R3 = (x3/100)/1e-9
N = len(a)
print(f"=== VERIFY (gatemap.md) ===  rows={N} (expect 10201)")
print(f"  complete: {N==10201}")
print(f"  leakage |I_tg|max={np.abs(itg).max()*1e12:.1f} pA  |I_bg|max={np.abs(ibg).max()*1e12:.1f} pA  (<1nA: {np.abs(itg).max()<1e-9 and np.abs(ibg).max()<1e-9})")
print(f"  sr830_1 flat? {np.allclose(x1,x1[0])}  sr830_2 flat? {np.allclose(x2,x2[0])}  sr830_3 flat? {np.allclose(x3,x3[0])}")
print(f"  NaNs: {np.isnan(a).any()}")

# --- CNP ridge fit on 4T ---
rows = np.unique(np.round(vtg, 3))
pts = []
for vt in rows:
    m = np.round(vtg,3)==vt
    bg = vbg[m]; r = R3[m]; o=np.argsort(bg); bg=bg[o]; r=r[o]
    rs = gaussian_filter1d(r,2); k=np.argmax(rs)
    if k<=1 or k>=len(bg)-2: continue
    if rs[k] < 3*np.median(rs) or rs[k] < 200: continue
    pts.append((vt, bg[k]))
pts=np.array(pts); vt=pts[:,0]; vb=pts[:,1]
keep=np.ones(len(vt),bool)
for _ in range(3):
    c=np.polyfit(vt[keep],vb[keep],1); res=vb-np.polyval(c,vt); s=np.std(res[keep]); keep=np.abs(res)<2*s
slope,intc=np.polyfit(vt[keep],vb[keep],1)
resid=np.std((vb-np.polyval((slope,intc),vt))[keep])
ratio=-slope
print(f"\n=== CNP fit (4T 30-31) ===")
print(f"  {keep.sum()}/{len(vt)} ridge rows; dV_bg/dV_tg={slope:+.4f} intercept={intc:+.4f}V resid={resid*1e3:.1f}mV")
print(f"  c_tg/c_bg = {ratio:.4f}  (prior t_bg/t_tg = {20/23.6:.4f}; agree {100*(1-abs(ratio-20/23.6)/(20/23.6)):.1f}%)")
# CNP crosses V_bg=0 at V_tg = intc-as-Vbg... line is Vbg=slope*Vtg+intc -> Vtg(Vbg=0)= -intc/slope
vtg0 = -intc/slope
print(f"  CNP at V_bg=0: V_tg={vtg0:+.3f} V")

# --- calibration: prior c's (ratio validated), n_offset from CNP ---
cal0 = GateCalibration.from_thicknesses(23.6e-9,20e-9,0)
n_at_cnp = cal0.n_D(np.array([vtg0]),np.array([0.0]))[0][0]
n_off = -n_at_cnp
cal = GateCalibration.from_thicknesses(23.6e-9,20e-9,0,n_offset=n_off)
print(f"  n_offset set to {n_off:.3e} m^-2 ({n_off/1e4/1e11:.3f}e11 cm^-2); CNP closure n_residual along ridge:")
nrid,Drid = cal.n_D(vt[keep], vb[keep])
print(f"    max|n| on ridge = {np.abs(nrid).max()/1e4/1e11:.3f}e11 cm^-2 (closure quality)")

# --- (n,D) render ---
# reshape to grid (slow=vtg 101, fast=vbg 101)
ntg=len(rows)
assert N==ntg*101 or N==10201, f"non-rect {N}"
VT=vtg.reshape(101,101); VB=vbg.reshape(101,101)
nG,DG = cal.n_D(VT.ravel(), VB.ravel()); nG=nG.reshape(101,101)/1e4/1e11; DG=DG.reshape(101,101)/1e9
R2g=R2.reshape(101,101); R3g=R3.reshape(101,101)

fig,ax=plt.subplots(1,2,figsize=(15,6))
# panel 0: 2T full overview (n axis +/-15); panel 1: 2T zoom on hole/D<0 candidate region
specs=[(ax[0],R2g/1e3,"2T R (5-4) [kΩ] — overview",50,(-15,15),(-0.75,0.7)),
       (ax[1],R2g/1e3,"2T R (5-4) [kΩ] — hole / D<0 zoom",20,(-12,2),(-0.75,-0.15))]
for axi,Rg,ttl,vmax,xl,yl in specs:
    pc=axi.pcolormesh(nG,DG,Rg,shading="auto",cmap="viridis",vmin=0,vmax=vmax)
    plt.colorbar(pc,ax=axi)
    axi.plot(nrid/1e4/1e11,Drid/1e9,"r.",ms=2,label="CNP ridge (4T)")
    axi.add_patch(plt.Rectangle((-6,-0.75),2,0.25,fill=False,ec="white",lw=1.5,ls="--"))
    axi.set_xlabel("n (1e11 cm^-2)"); axi.set_ylabel("D (V/nm)"); axi.set_title(ttl)
    axi.axhline(0,color="gray",lw=.5); axi.axvline(0,color="gray",lw=.5)
    axi.set_xlim(*xl); axi.set_ylim(*yl)
ax[0].legend(loc="upper right",fontsize=8)
fig.suptitle(f"zf1 survey gatemap (run 4) — (n,D); c_tg/c_bg={ratio:.3f}; dashed=SC target (D<0,|D|>0.5,n~-5e11)")
fig.tight_layout(); fig.savefig("hera_scratch/map_nD.png",dpi=110)
print("\nsaved hera_scratch/map_nD.png")

# --- where is 2T lowest on the hole/D<0 side (candidate hunt)? ---
mask = (nG<-2)&(nG>-9)&(DG<-0.2)
if mask.any():
    R2m=R2g.copy(); R2m[~mask]=np.inf
    j=np.unravel_index(np.argmin(R2m),R2m.shape)
    print(f"min 2T on hole/D<0 side: n={nG[j]:.2f}e11, D={DG[j]:+.2f}V/nm, R2={R2g[j]/1e3:.2f}kΩ, R3={R3g[j]:.1f}Ω at V=({VT[j]:+.2f},{VB[j]:+.2f})")
