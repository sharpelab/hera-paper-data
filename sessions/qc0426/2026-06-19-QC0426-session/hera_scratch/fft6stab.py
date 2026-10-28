import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
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
print(f"F_L={FL:.1f}T.  FFT stability: peaks across windows (Blo) x detrend. Real=stable, artifact=wanders.")
fig,ax=plt.subplots(1,2,figsize=(13,5))
for col,ch in enumerate(['sr2','sr1']):
    R=proj(ch); m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]
    print(f"\n{ch}:")
    for Blo in [2.6,3.0,3.5,4.0]:
        sel=(Bs>=Blo)&(Bs<=8); Bw=Bs[sel]; Rw=Rs[sel]
        if len(Bw)<40: continue
        p=np.polyfit(Bw,Rw,5); dR=Rw-np.polyval(p,Bw)
        invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),16384)
        dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
        F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
        fl=np.median(A[(F>8)&(F<140)])
        pk,_=find_peaks(A,height=fl*3,distance=3); pk=pk[(F[pk]>6)&(F[pk]<140)]; pk=pk[np.argsort(A[pk])[::-1]]
        dF=1/(invB.max()-invB.min())
        print(f"  [{Blo:.1f}-8T] dF={dF:.1f}T  peaks(F,SNR): "+", ".join(f"{F[k]:.0f}({A[k]/fl:.1f})" for k in pk[:5]))
        if Blo==3.0:
            ax[col].plot(F,A/A.max(),label=f'Blo={Blo}')
    # show 2.6 and 4.0 overlaid for stability
    for Blo,ls in [(2.6,'--'),(4.0,':')]:
        sel=(Bs>=Blo)&(Bs<=8); Bw=Bs[sel]; Rw=Rs[sel]
        if len(Bw)<40: continue
        p=np.polyfit(Bw,Rw,5); dR=Rw-np.polyval(p,Bw); invB=1/Bw; ordr=np.argsort(invB)
        ub=np.linspace(invB[ordr].min(),invB[ordr].max(),16384); dRi=np.interp(ub,invB[ordr],dR[ordr])
        F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
        ax[col].plot(F,A/A.max(),ls,alpha=.6,label=f'Blo={Blo}')
    ax[col].axvline(FL,color='r',ls='--',alpha=.5); ax[col].set_xlim(0,120); ax[col].set_title(f'{ch} FFT vs window'); ax[col].legend(fontsize=8); ax[col].grid(alpha=.3); ax[col].set_xlabel('F(T)')
plt.tight_layout(); plt.savefig('hera_scratch/fft6stab.png',dpi=110); print("\nsaved")
