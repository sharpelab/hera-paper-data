import numpy as np, os, json
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/4"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I
FL=cst.h*10e16/(4*cst.e)
print(f"data/4 rows so far: {len(B)}  B {B.min():.2f}-{B.max():.2f}  F_L={FL:.0f}T")
for ch in ['sr2','sr1']:
    R=proj(ch); m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]
    sel=(Bs>=1.9)&(Bs<=4.0); Bw=Bs[sel]; Rw=Rs[sel]
    if len(Bw)<30: print(f"{ch}: too few pts"); continue
    p=np.polyfit(Bw,Rw,4); dR=Rw-np.polyval(p,Bw)
    invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),4096)
    dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
    F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
    band=(F>15)&(F<200); noise=np.median(A[band])
    pk,_=find_peaks(A,height=noise*4,distance=4); pk=pk[(F[pk]>15)&(F[pk]<200)]; pk=pk[np.argsort(A[pk])[::-1]]
    print(f"{ch} [1.9-4T] dF={1/(invB.max()-invB.min()):.1f}T  dR_amp={np.std(dR):.2f} noise_floor(FFT)={noise:.2f}")
    if len(pk): print("   peaks>4xfloor: "+", ".join(f"{F[k]:.0f}T(SNR{A[k]/noise:.1f})" for k in pk[:5]))
    else: print("   NO peaks > 4x noise floor -> SdH not resolved in this window")
