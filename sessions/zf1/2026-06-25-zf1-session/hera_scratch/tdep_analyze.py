import json, gzip, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(run):
    md=json.load(open(f"{run}/metadata.json")); cols=md["columns"]
    p=f"{run}/data.tsv"; f=gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
    a=np.genfromtxt(f,delimiter="\t",invalid_raise=False); f.close(); a=a[~np.isnan(a).any(axis=1)]
    ix={};[ix.setdefault(c,j) for j,c in enumerate(cols)]
    vidx=[i for i,c in enumerate(cols) if "dc205" in c]
    Idc=a[:,vidx[0]]/1e8*1e9
    dVdI=(a[:,ix["sr830_3_X"]]/100)/0.5e-9
    T=np.median(a[:,ix["T"]])*1e3
    return Idc,dVdI,T

runs=list(range(13,21))
Ts=[]; Ics=[]; R0s=[]; Rns=[]
fig,ax=plt.subplots(1,3,figsize=(18,5))
cmap=plt.cm.viridis(np.linspace(0,1,len(runs)))
for k,r in enumerate(runs):
    Idc,dVdI,T=load(f"data/{r}")
    o=np.argsort(Idc); Idc,dVdI=Idc[o],dVdI[o]
    Rn=np.median(dVdI[np.abs(Idc)>45]); R0=np.median(dVdI[np.abs(Idc)<2.5])
    thr=0.5*Rn
    def ic(sign):
        m=(np.sign(Idc)==sign)&(np.abs(Idc)>0.5); x=np.abs(Idc[m]); y=dVdI[m]; oo=np.argsort(x); x,y=x[oo],y[oo]
        # Ic = first |I| reaching thr; if R0 already > thr (no SC), Ic=0
        if y[0]>=thr: return 0.0
        c=np.where(y>=thr)[0]; return x[c[0]] if len(c) else np.nan
    Icv=np.nanmean([ic(1),ic(-1)])
    Ts.append(T); Ics.append(Icv); R0s.append(R0); Rns.append(Rn)
    ax[0].plot(Idc,dVdI,color=cmap[k],lw=1,label=f"{T:.0f} mK")
ax[0].set_xlabel("I_dc (nA)"); ax[0].set_ylabel("dV/dI (Ω)"); ax[0].set_title("dV/dI(I_dc) vs T"); ax[0].legend(fontsize=7,ncol=2); ax[0].set_xlim(-60,60); ax[0].grid(alpha=.3)
Ts=np.array(Ts); Ics=np.array(Ics); R0s=np.array(R0s); Rns=np.array(Rns)
ax[1].plot(Ts,Ics,"o-",color="crimson"); ax[1].set_xlabel("T (mK)"); ax[1].set_ylabel("Ic (nA)"); ax[1].set_title("Ic(T)"); ax[1].grid(alpha=.3); ax[1].axhline(0,color="gray",lw=.5)
ax[2].plot(Ts,R0s,"o-",color="navy",label="R0 (zero-bias)"); ax[2].plot(Ts,Rns,"s--",color="gray",label="Rn (normal)",ms=4)
ax[2].set_xlabel("T (mK)"); ax[2].set_ylabel("dV/dI (Ω)"); ax[2].set_title("zero-bias R0(T) & normal Rn(T)"); ax[2].legend(); ax[2].grid(alpha=.3)
fig.suptitle("zf1 runs 13-20 — Ic(T) ladder at the dome (n=-5.0e11, D=-0.64)")
fig.tight_layout(); fig.savefig("hera_scratch/tdep.png",dpi=110)

print("T(mK)  Ic(nA)  R0(Ω)  Rn(Ω)")
for T,I,R,N in zip(Ts,Ics,R0s,Rns): print(f"  {T:6.0f}  {I:5.1f}  {R:6.1f}  {N:5.1f}")
# Tc estimates
# (a) R0 reaches 50% of high-T normal
Rn_norm=np.median(Rns[-3:]); halfR=0.5*Rn_norm
Tc_R=np.interp(halfR, R0s, Ts)
# (b) Ic -> 0 linear extrapolation from the collapsing points (Ic between 0 and base)
mask=(Ics<0.9*Ics[0])&(Ics>0)
if mask.sum()>=2:
    cT=np.polyfit(Ics[mask],Ts[mask],1); Tc_I=np.polyval(cT,0)
else: Tc_I=np.nan
print(f"normal Rn~{Rn_norm:.1f}Ω; Tc(R0=50% normal)~{Tc_R:.0f} mK; Tc(Ic->0 extrap)~{Tc_I:.0f} mK")
print("saved hera_scratch/tdep.png")
