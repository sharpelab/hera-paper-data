import json, gzip, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

run="data/9"
md=json.load(open(f"{run}/metadata.json")); cols=md["columns"]
p=f"{run}/data.tsv"; f=gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
a=np.genfromtxt(f,delimiter="\t",invalid_raise=False); f.close(); a=a[~np.isnan(a).any(axis=1)]
ix={}; [ix.setdefault(c,j) for j,c in enumerate(cols)]
# dc205 swept voltage (first occurrence is setpoint)
vdc_idx=[i for i,c in enumerate(cols) if "dc205" in c]
Vdc=a[:, vdc_idx[0]] if vdc_idx else a[:, ix.get("dc205_1_voltage")]
Idc=Vdc/1e8*1e9   # nA
Iac=0.5e-9
dVdI=(a[:,ix["sr830_3_X"]]/100)/Iac   # Ω (4T 30-31)
dVdI2=(a[:,ix["sr830_2_X"]]/100)/Iac  # 2T
N=len(a); half=N//2
fwd=slice(0,half); bwd=slice(half,N)

fig,ax=plt.subplots(1,2,figsize=(14,5))
ax[0].plot(Idc[fwd],dVdI[fwd],"b-",lw=1,label="fwd -15→+15")
ax[0].plot(Idc[bwd],dVdI[bwd],"r-",lw=1,alpha=.7,label="bwd +15→-15")
ax[0].set_xlabel("I_dc (nA)"); ax[0].set_ylabel("dV/dI 4T (Ω)"); ax[0].set_title("dV/dI vs I_dc (full)"); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].axhline(0,color="gray",lw=.5); ax[0].axvline(0,color="gray",lw=.5)
ax[1].plot(Idc[fwd],dVdI[fwd],"b.-",ms=3,lw=.7,label="fwd")
ax[1].plot(Idc[bwd],dVdI[bwd],"r.-",ms=3,lw=.7,alpha=.7,label="bwd")
ax[1].set_xlim(-80,80); ax[1].set_xlabel("I_dc (nA)"); ax[1].set_ylabel("dV/dI 4T (Ω)"); ax[1].set_title("zoom ±80 nA"); ax[1].legend(); ax[1].grid(alpha=.3); ax[1].axhline(0,color="gray",lw=.5)
fig.suptitle("zf1 run 9 — bias spectroscopy at dome optimum (n=-5.0e11, D=-0.64)")
fig.tight_layout(); fig.savefig("hera_scratch/bias.png",dpi=110)

# normal-state dV/dI (high bias) and zero-bias value
Rn=np.median(dVdI[np.abs(Idc)>120])
R0=np.median(dVdI[np.abs(Idc)<3])
print(f"normal-state dV/dI (|I|>120nA): {Rn:.1f} Ω")
print(f"zero-bias dV/dI (|I|<3nA): {R0:.1f} Ω")
# Ic via threshold crossing at 50% of normal (per fwd branch, from 0 outward)
thr=0.5*Rn
def ic_branch(Idc_b,dVdI_b,sign):
    m=(np.sign(Idc_b)==sign)&(np.abs(Idc_b)>1)
    xi=Idc_b[m]; yi=dVdI_b[m]; o=np.argsort(np.abs(xi)); xi=xi[o]; yi=yi[o]
    cross=np.where(yi>=thr)[0]
    return abs(xi[cross[0]]) if len(cross) else np.nan
icp=ic_branch(Idc[fwd],dVdI[fwd],+1); icn=ic_branch(Idc[fwd],dVdI[fwd],-1)
print(f"Ic (50% normal threshold, fwd): I_c+ ≈ {icp:.0f} nA, I_c- ≈ {icn:.0f} nA  (thr={thr:.0f}Ω)")
# switching-peak location (max dV/dI within ±100nA, per sign)
for sgn,lab in [(+1,"+"),(-1,"-")]:
    m=(np.sign(Idc)==sgn)&(np.abs(Idc)<100)
    if m.any():
        j=np.argmax(dVdI[m]); print(f"  peak {lab}: dV/dI={dVdI[m][j]:.0f}Ω at I_dc={Idc[m][j]:.0f}nA")
print("saved hera_scratch/bias.png")
