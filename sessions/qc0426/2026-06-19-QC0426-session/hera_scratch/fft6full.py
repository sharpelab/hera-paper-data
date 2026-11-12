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
    return (X*np.cos(th)+Y*np.sin(th))/I, (-X*np.sin(th)+Y*np.cos(th))/I
FL=cst.h*5e16/(4*cst.e)
print(f"n=-5e12  F_L=(h/4e)n = {FL:.1f} T   rows={len(B)}  B {B.min():.2f}-{B.max():.2f}T")
fig,ax=plt.subplots(2,2,figsize=(13,8))
res={}
for col,ch in enumerate(['sr2','sr1']):
    R,q=proj(ch); m=B>0.02; o=np.argsort(B[m]); Bs=B[m][o]; Rs=R[m][o]; qs=q[m][o]
    noise=np.std(np.diff(qs))/np.sqrt(2)
    # onset: lowest B where local dRxx amp > 3*noise
    onset=None
    for bc in np.arange(0.6,4,0.1):
        sl=(Bs>bc-0.25)&(Bs<bc+0.25)
        if sl.sum()>8:
            dd=Rs[sl]-np.polyval(np.polyfit(Bs[sl],Rs[sl],2),Bs[sl])
            if np.std(dd)>3*noise: onset=bc; break
    Blo=max(onset or 1.2, 0.9)
    sel=(Bs>=Blo)&(Bs<=8); Bw=Bs[sel]; Rw=Rs[sel]
    # two detrenders (stability)
    peaks_by_dt={}
    for dt in [3,5]:
        p=np.polyfit(Bw,Rw,dt); dR=Rw-np.polyval(p,Bw)
        invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),16384)
        dRi=np.interp(ub,invB[ordr],dR[ordr]); win=np.hanning(len(dRi))
        F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*win))
        fl=np.median(A[(F>8)&(F<150)])
        pk,_=find_peaks(A,height=fl*4,distance=4); pk=pk[(F[pk]>5)&(F[pk]<150)]; pk=pk[np.argsort(A[pk])[::-1]]
        peaks_by_dt[dt]=[(round(F[k],1),round(A[k]/fl,1)) for k in pk[:6]]
        if dt==5:
            ax[0,col].plot(F,A); ax[0,col].axvline(FL,color='r',ls='--',label=f'F_L={FL:.0f}')
            for k in pk[:5]: ax[0,col].annotate(f'{F[k]:.0f}',(F[k],A[k]))
            ax[0,col].set_xlim(0,140); ax[0,col].set_title(f'{ch} FFT [{Blo:.1f}-8T] dF={1/(invB.max()-invB.min()):.1f}T'); ax[0,col].legend(); ax[0,col].grid(alpha=.3)
            ax[1,col].plot(1/Bw,dR,'-'); ax[1,col].set_xlabel('1/B'); ax[1,col].set_title(f'{ch} dRxx onset~{onset:.1f}T noise={noise:.2f}'); ax[1,col].grid(alpha=.3)
    print(f"  {ch}: onset~{onset:.1f}T noise={noise:.2f} window[{Blo:.1f},8]")
    print(f"     poly3 peaks: {peaks_by_dt[3]}")
    print(f"     poly5 peaks: {peaks_by_dt[5]}")
    res[ch]=peaks_by_dt[5]
plt.tight_layout(); plt.savefig('hera_scratch/fft6full.png',dpi=110)
# Luttinger check
print(f"\nLuttinger: F_L={FL:.1f}T. ABC->single tone at F_L; ABA->pair summing to F_L.")
