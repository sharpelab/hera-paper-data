import numpy as np, os, json
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/6"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I
FL=cst.h*5e16/(4*cst.e)
print(f"n=-5e12  F_L=(h/4e)n = {FL:.0f} T   (B range so far {B.min():.2f}-{B.max():.2f})")
for ch in ['sr2','sr1']:
    R=proj(ch); m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]
    sel=(Bs>=5.0)&(Bs<=8.0); Bw=Bs[sel]; Rw=Rs[sel]
    p=np.polyfit(Bw,Rw,3); dR=Rw-np.polyval(p,Bw)
    invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),8192)
    dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
    F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
    fl=np.median(A[(F>10)&(F<150)])
    pk,_=find_peaks(A,height=fl*4,distance=3); pk=pk[(F[pk]>5)&(F[pk]<150)]; pk=pk[np.argsort(A[pk])[::-1]]
    print(f"  {ch} [5-8T] dF={1/(invB.max()-invB.min()):.0f}T: peaks: "+", ".join(f"{F[k]:.0f}T(SNR{A[k]/fl:.1f})" for k in pk[:5]))
