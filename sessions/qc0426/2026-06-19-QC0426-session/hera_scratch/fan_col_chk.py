import numpy as np, json, os
d="data/7"; meta=json.load(open(os.path.join(d,"metadata.json")))
cols=meta["columns"]; fast_sp=meta["fast_setpoints"]; nfast=len(fast_sp[0])
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
idx={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; idx[k]=i
ndone=raw.shape[0]//nfast
B=raw[:,idx['magnet_mag']]; I=np.abs(raw[:,idx['sr0_X']]/1e6)
maxR=np.max(np.abs(raw[:,idx['sr1_R']]/I)); print(f"rows {ndone}/157, max sr1 |R|={maxR:.0f} Ohm (overload at ~1090 @2e-5)")
# n=-5e12 column (Vbg~-1.811)
ci=int(np.argmin(np.abs(np.array(fast_sp[1])+1.811)))
def proj(ch):
    X=raw[:,idx[ch+'_X']]; Y=raw[:,idx[ch+'_Y']]; th=np.arctan2(np.median(Y),np.median(X)); return (X*np.cos(th)+Y*np.sin(th))/I
sel=np.arange(ndone)*nfast+ci
Bc=B[sel]; R2=proj('sr2')[sel]
o=np.argsort(Bc); Bc=Bc[o]; R2=R2[o]
m=(Bc>=3.5)
p=np.polyfit(Bc[m],R2[m],3); dR=R2[m]-np.polyval(p,Bc[m])
qn=np.std(np.diff(proj('sr2')[sel][o][m]))  # rough
print(f"n=-5e12 col: B {Bc.min():.2f}-{Bc.max():.2f}T, sr2 dRxx amp [3.5-{Bc.max():.1f}T] = {np.std(dR):.1f} Ohm")
