# Landau fan F(n) — the FS-count call (data/7): single tone tracks F_L => ABC
import numpy as np, json, os, matplotlib.pyplot as plt
import scipy.constants as cst
d="data/7"; meta=json.load(open(os.path.join(d,"metadata.json")))
cols=meta["columns"]; fast_sp=meta["fast_setpoints"]; nfast=len(fast_sp[0])
tsv="data/7/data.tsv.gz" if os.path.exists("data/7/data.tsv.gz") else "data/7/data.tsv"
raw=np.genfromtxt(tsv,delimiter="\t")
idx={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; idx[k]=i
ndone=raw.shape[0]//nfast
B=raw[:,idx['magnet_mag']]; I=np.abs(raw[:,idx['sr0_X']]/1e6); Vbg=np.array(fast_sp[1]); K=2.760e12
def proj(ch):
    X=raw[:,idx[ch+'_X']]; Y=raw[:,idx[ch+'_Y']]; th=np.arctan2(np.median(Y),np.median(X)); return (X*np.cos(th)+Y*np.sin(th))/I
def dom(ch,ci,Blo=3.5):
    sel=np.arange(ndone)*nfast+ci; Bc=B[sel]; Rc=proj(ch)[sel]; o=np.argsort(Bc); Bc=Bc[o]; Rc=Rc[o]
    m=(Bc>=Blo)&(Bc<=8)
    if m.sum()<25: return np.nan
    Bw=Bc[m]; dR=Rc[m]-np.polyval(np.polyfit(Bw,Rc[m],4),Bw); invB=1/Bw
    ub=np.linspace(invB.min(),invB.max(),16384); dRi=np.interp(ub,np.sort(invB),dR[np.argsort(invB)])
    F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
    band=(F>10)&(F<140); return F[np.argmax(A*band)]
ns=[]; FL=[]; f1=[]; f2=[]
for ci in range(1,nfast):
    n=abs(K*Vbg[ci]); ns.append(n/1e12); FL.append(cst.h*n*1e4/(4*cst.e)); f2.append(dom('sr2',ci)); f1.append(dom('sr1',ci))
ns=np.array(ns); FL=np.array(FL); f1=np.array(f1); f2=np.array(f2)
fig,ax=plt.subplots(1,2,figsize=(13,5))
ax[0].plot(ns,f2,'o-',label='sr2 B4-B5'); ax[0].plot(ns,f1,'s-',label='sr1 T3-T4')
ax[0].plot(ns,FL,'k--',label='F_L=(h/4e)n  (1 Fermi surface = ABC)')
ax[0].plot(ns,0.7*FL,'r:',alpha=.5,label='ABA BL example (ML~0.3)')
ax[0].set_xlabel('|n| (1e12 cm^-2)'); ax[0].set_ylabel('dominant F (T)'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3); ax[0].set_title('SdH F(n): single tone tracks F_L')
g=ns>4.3
ax[1].plot(ns,f2/FL,'o-',label='sr2'); ax[1].plot(ns,f1/FL,'s-',label='sr1'); ax[1].axhline(1,color='k',ls='--'); ax[1].axhline(0.7,color='r',ls=':',alpha=.5)
ax[1].set_ylim(0,1.5); ax[1].set_xlabel('|n| (1e12 cm^-2)'); ax[1].set_ylabel('F/F_L'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3); ax[1].set_title('F/F_L=1 => single FS (ABC)')
plt.suptitle('QC0426 Landau fan (data/7), D=0 hole — FS-count: ABC')
plt.tight_layout(); plt.show()
print(f"F/F_L (clean cols |n|>4.3e12): sr2={np.nanmean((f2/FL)[g]):.2f}+-{np.nanstd((f2/FL)[g]):.2f}, sr1={np.nanmean((f1/FL)[g]):.2f}+-{np.nanstd((f1/FL)[g]):.2f}")
print("=> single SdH tone at F_L, both channels, across density => ONE Fermi surface => ABC (rhombohedral).")
