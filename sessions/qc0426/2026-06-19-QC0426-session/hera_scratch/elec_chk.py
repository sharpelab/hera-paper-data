import numpy as np, json, os
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/8"; cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X)); return (X*np.cos(th)+Y*np.sin(th))/I
FL=cst.h*5e16/(4*cst.e)
print(f"electron n=+5e12 F_L={FL:.0f}T  B {B.min():.2f}-{B.max():.2f}T  rows {len(B)}")
for ch in ['sr2','sr1']:
    R=proj(ch); m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]
    sel=(Bs>=3.5)&(Bs<=8); Bw=Bs[sel]
    if sel.sum()<25: print(f"  {ch}: B range too short yet"); continue
    dR=Rs[sel]-np.polyval(np.polyfit(Bw,Rs[sel],4),Bw); invB=1/Bw
    ub=np.linspace(invB.min(),invB.max(),16384); dRi=np.interp(ub,np.sort(invB),dR[np.argsort(invB)])
    F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
    fl=np.median(A[(F>10)&(F<140)]); pk,_=find_peaks(A,height=fl*4,distance=3); pk=pk[(F[pk]>5)&(F[pk]<140)]; pk=pk[np.argsort(A[pk])[::-1]]
    print(f"  {ch}: dRxx amp={np.std(dR):.1f} Ohm  peaks: "+", ".join(f"{F[k]:.0f}T(SNR{A[k]/fl:.1f})" for k in pk[:4]))
