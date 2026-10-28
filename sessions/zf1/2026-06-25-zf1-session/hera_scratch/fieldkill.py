import json, gzip, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(run):
    md=json.load(open(f"{run}/metadata.json")); cols=md["columns"]
    p=f"{run}/data.tsv"; f=gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
    a=np.genfromtxt(f,delimiter="\t",invalid_raise=False); f.close(); a=a[~np.isnan(a).any(axis=1)]
    ix={};[ix.setdefault(c,j) for j,c in enumerate(cols)]
    return dict(B=a[:,ix["magnet_field"]]*1e3, R3=(a[:,ix["sr830_3_X"]]/100)/1e-9, T=a[:,ix["T"]]*1e3)

c=load("data/10")    # +50->0 coarse
p=load("data/11")    # +15->0 fine
m=load("data/12")    # -15->0 fine
# stitch fine symmetric
Bs=np.concatenate([m["B"], p["B"]]); Rs=np.concatenate([m["R3"], p["R3"]])
o=np.argsort(Bs); Bs=Bs[o]; Rs=Rs[o]

fig,ax=plt.subplots(1,2,figsize=(14,5))
ax[0].plot(c["B"],c["R3"],"k.-",ms=3,lw=.6,label="run10 +50→0 (coarse)")
ax[0].set_xlabel("B⊥ (mT)"); ax[0].set_ylabel("Rxx (Ω)"); ax[0].set_title("field-kill, full range to 50 mT"); ax[0].grid(alpha=.3); ax[0].legend()
ax[1].plot(Bs,Rs,"b.-",ms=4,lw=.7)
ax[1].set_xlim(-15,15); ax[1].set_xlabel("B⊥ (mT)"); ax[1].set_ylabel("Rxx (Ω)"); ax[1].set_title("fine symmetric (runs 11/12 stitched)"); ax[1].grid(alpha=.3); ax[1].axhline(0,color="gray",lw=.5); ax[1].axvline(0,color="gray",lw=.5)
fig.suptitle("zf1 runs 10-12 — B⊥ field-kill at the dome (n=-5.0e11, D=-0.64)")
fig.tight_layout(); fig.savefig("hera_scratch/fieldkill.png",dpi=110)

Rn=np.median(Rs[np.abs(Bs)>8]); R0=Rs[np.argmin(np.abs(Bs))]
half=0.5*(Rn+R0)
# B_c per side at 50% (interp on |B| vs R)
def bc_side(B,R,sign):
    sel=np.sign(B)==sign; Bb=np.abs(B[sel]); Rr=R[sel]; o=np.argsort(Bb)
    Bb=Bb[o]; Rr=Rr[o]
    cr=np.where(Rr>=half)[0]
    return np.interp(half,Rr,Bb) if len(cr) else np.nan
bcp=bc_side(Bs,Rs,+1); bcn=bc_side(Bs,Rs,-1)
bmin=Bs[np.argmin(Rs)]
print(f"R(B~0)={R0:.1f}Ω  normal(|B|>8mT)={Rn:.1f}Ω  half={half:.1f}Ω")
print(f"effective-zero (min Rxx) at B={bmin:.2f} mT  (Rmin={Rs.min():.1f}Ω)")
print(f"B_c⊥ (50%): +side {bcp:.2f} mT, -side {bcn:.2f} mT")
# coherence length (order of magnitude)
phi0=2.067e-15; Bc=np.nanmean([bcp,bcn])*1e-3
xi=np.sqrt(phi0/(2*np.pi*Bc))
print(f"mean B_c⊥={Bc*1e3:.2f} mT -> ξ ~ {xi*1e9:.0f} nm (Hc2=Φ0/2πξ², order-of-magnitude)")
print(f"T over fine sweeps: {min(p['T'].min(),m['T'].min()):.1f}-{max(p['T'].max(),m['T'].max()):.1f} mK")
print("saved hera_scratch/fieldkill.png")
