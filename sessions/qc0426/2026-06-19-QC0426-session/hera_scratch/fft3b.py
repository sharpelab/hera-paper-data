import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/3"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']
    th=np.arctan2(np.median(Y),np.median(X))   # resistive phase
    Rpar=(X*np.cos(th)+Y*np.sin(th))/I          # resistive projection
    Rperp=(-X*np.sin(th)+Y*np.cos(th))/I        # quadrature (noise estimate)
    return Rpar,Rperp,np.degrees(th)
m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]
FL=cst.h*10e16/(4*cst.e)
fig,ax=plt.subplots(3,2,figsize=(12,10))
for col,ch in enumerate(['sr2','sr1']):
    Rpar,Rperp,th=proj(ch); Rpar=Rpar[m][o]; Rperp=Rperp[m][o]
    noise=np.std(np.diff(Rperp))/np.sqrt(2)
    print(f"{ch}: resistive phase={th:.0f} deg  Rpar med={np.median(Rpar):.1f} Ohm  quad-noise(pt)={noise:.2f} Ohm")
    for Blo,cc in [(1.5,'window')]:
        sel=(Bs>=Blo)&(Bs<=4.0); Bw=Bs[sel]; Rw=Rpar[sel]
        p=np.polyfit(Bw,Rw,5); dR=Rw-np.polyval(p,Bw)
        invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),4096)
        dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
        F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
        pk,_=find_peaks(A,height=A.max()*0.2,distance=4); pk=pk[(F[pk]>3)&(F[pk]<260)]
        pk=pk[np.argsort(A[pk])[::-1]]
        print(f"  [{Blo}-4T] dF={1/(invB.max()-invB.min()):.1f}T  amp(dR)~{np.std(dR):.2f}Ohm  peaks: "+", ".join(f"{F[k]:.0f}T(A{A[k]/A[pk[0]]:.2f})" for k in pk[:5]))
        ax[0,col].plot(Bw,dR,'.-',ms=2); ax[0,col].set_title(f'{ch} dR_par(B) [{Blo}-4T]'); ax[0,col].grid(alpha=.3)
        ax[1,col].plot(1/Bw,dR,'.-',ms=2); ax[1,col].set_title(f'{ch} dR vs 1/B'); ax[1,col].grid(alpha=.3)
        ax[2,col].plot(F,A); ax[2,col].axvline(FL,color='r',ls='--'); ax[2,col].set_xlim(0,200); ax[2,col].set_title(f'{ch} FFT (F_L={FL:.0f})'); ax[2,col].grid(alpha=.3)
        for k in pk[:4]: ax[2,col].annotate(f'{F[k]:.0f}',(F[k],A[k]))
plt.tight_layout(); plt.savefig('hera_scratch/fft3b.png',dpi=110); print("saved")
