import numpy as np, os, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/5"
cols=json.load(open(os.path.join(d,"metadata.json")))["columns"]
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
C={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else c+f".{seen[c]}"; seen[c]=seen.get(c,0)+1; C[k]=raw[:,i]
B=C['magnet_mag']; I=np.abs(C['sr0_X']/1e6)
def proj(ch):
    X=C[ch+'_X']; Y=C[ch+'_Y']; th=np.arctan2(np.median(Y),np.median(X))
    return (X*np.cos(th)+Y*np.sin(th))/I, (-X*np.sin(th)+Y*np.cos(th))/I
R2,q2=proj('sr2'); R1,q1=proj('sr1')
m=B>0.02; o=np.argsort(B[m]); B=B[m][o]; R2=R2[m][o]; R1=R1[m][o]; q2=q2[m][o]
FL=cst.h*10e16/(4*cst.e)
noise=np.std(np.diff(q2))/np.sqrt(2)
print(f"F_L(n=10e12)={FL:.0f}T  quad-noise={noise:.2f} Ohm")
# onset: sliding-window dRxx amplitude (detrended locally) vs noise
print("onset scan (sliding 0.8T window, sr2 dRxx amp vs noise %.2f):"%noise)
for bc in np.arange(2.5,7.6,0.5):
    sel=(B>bc-0.4)&(B<bc+0.4)
    if sel.sum()<15: continue
    p=np.polyfit(B[sel],R2[sel],2); dr=R2[sel]-np.polyval(p,B[sel])
    print(f"   B~{bc:.1f}T: dRxx_amp={np.std(dr):.2f} Ohm  (SNR {np.std(dr)/noise:.1f})")
# FFT over high-field windows
fig,ax=plt.subplots(2,2,figsize=(13,8))
for col,(ch,R) in enumerate([('sr2',R2),('sr1',R1)]):
    for Blo,cc in [(4.0,'C0'),(5.0,'C3')]:
        sel=(B>=Blo)&(B<=7.99); Bw=B[sel]; Rw=R[sel]
        p=np.polyfit(Bw,Rw,3); dR=Rw-np.polyval(p,Bw)
        invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),4096)
        dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
        F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
        fl=np.median(A[(F>15)&(F<200)])
        pk,_=find_peaks(A,height=fl*4,distance=4); pk=pk[(F[pk]>10)&(F[pk]<200)]; pk=pk[np.argsort(A[pk])[::-1]]
        lab=f"[{Blo:.0f}-8T] dF={1/(invB.max()-invB.min()):.0f}T"
        pks=", ".join(f"{F[k]:.0f}T(SNR{A[k]/fl:.1f})" for k in pk[:4]) if len(pk) else "no peaks>4x"
        print(f"  {ch} {lab}: dR_amp={np.std(dR):.2f}  {pks}")
        ax[0,col].plot(F,A,color=cc,label=lab); 
    ax[0,col].axvline(FL,color='k',ls='--',alpha=.5,label=f'F_L={FL:.0f}')
    ax[0,col].set_xlim(0,180); ax[0,col].set_title(f'{ch} FFT'); ax[0,col].legend(fontsize=8); ax[0,col].grid(alpha=.3)
    sel=(B>=4)&(B<=7.99); p=np.polyfit(B[sel],R[sel],3)
    ax[1,col].plot(1/B[sel],R[sel]-np.polyval(p,B[sel]),'.-',ms=3); ax[1,col].set_xlabel('1/B'); ax[1,col].set_title(f'{ch} dRxx vs 1/B [4-8T]'); ax[1,col].grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/fft5.png',dpi=110); print("saved")
