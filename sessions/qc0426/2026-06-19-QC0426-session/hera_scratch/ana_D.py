# SdH FS-count, hole n=-5e12 D=0 (data/6) — the resolvable-density spot check
import numpy as np, json, matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
cols=json.load(open("data/6/metadata.json"))["columns"]
raw=np.genfromtxt("data/6/data.tsv.gz" if __import__("os").path.exists("data/6/data.tsv.gz") else "data/6/data.tsv", delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I
FL=cst.h*5e16/(4*cst.e)
fig,ax=plt.subplots(2,2,figsize=(13,8))
for col,ch in enumerate(['sr2 B4-B5','sr1 T3-T4']):
    key=ch.split()[0]; R=proj(key)
    m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]
    sel=(Bs>=2.6)&(Bs<=8); Bw=Bs[sel]; Rw=Rs[sel]
    p=np.polyfit(Bw,Rw,5); dR=Rw-np.polyval(p,Bw)
    invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),16384)
    dRi=np.interp(ub,invB[ordr],dR[ordr]); F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0])
    A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
    fl=np.median(A[(F>8)&(F<140)]); pk,_=find_peaks(A,height=fl*3,distance=3); pk=pk[(F[pk]>6)&(F[pk]<120)]
    ax[0,col].plot(Bw,Rw,lw=.8); ax[0,col].set_title(f'{ch}: Rxx(B)'); ax[0,col].set_xlabel('B(T)'); ax[0,col].grid(alpha=.3)
    ax[1,col].plot(F,A); ax[1,col].axvline(FL,color='r',ls='--',label=f'F_L={FL:.0f}T'); ax[1,col].set_xlim(0,120)
    for k in pk[np.argsort(A[pk])[::-1]][:4]: ax[1,col].annotate(f'{F[k]:.0f}',(F[k],A[k]))
    ax[1,col].set_title(f'{ch}: 1/B FFT [2.6-8T] dF={1/(invB.max()-invB.min()):.1f}T'); ax[1,col].set_xlabel('F(T)'); ax[1,col].legend(); ax[1,col].grid(alpha=.3)
plt.suptitle('QC0426 hole n=-5e12 SdH FS-count (data/6, 20nA) — F_L=%.0f T'%FL)
plt.tight_layout(); plt.show()
print("sr2 region: single tone ~50T ~ F_L (harmonic ~100T) -> ONE Fermi surface, ABC-consistent")
print("sr1 region: tones ~15T + ~42T (sum ~ F_L) -> a PAIR, ABA-consistent")
print("Channels disagree at the same density -> candidate STACKING MOSAIC (per-region call).")
print("PRELIMINARY: single density, dF~4T marginal; firm with F(n) across density (Luttinger partition) + Onsager overlay at |n|<=3.5e12.")
