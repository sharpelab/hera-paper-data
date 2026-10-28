import numpy as np, json, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
d="data/7"; meta=json.load(open(os.path.join(d,"metadata.json")))
cols=meta["columns"]; fast_sp=meta["fast_setpoints"]; nfast=len(fast_sp[0])
tsv=os.path.join(d,"data.tsv.gz") if os.path.exists(os.path.join(d,"data.tsv.gz")) else os.path.join(d,"data.tsv")
raw=np.genfromtxt(tsv,delimiter="\t")
idx={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; idx[k]=i
ndone=raw.shape[0]//nfast
B=raw[:,idx['magnet_mag']]; I=np.abs(raw[:,idx['sr0_X']]/1e6)
Vbg=np.array(fast_sp[1]); K=2.760e12
def proj(ch):
    X=raw[:,idx[ch+'_X']]; Y=raw[:,idx[ch+'_Y']]; th=np.arctan2(np.median(Y),np.median(X)); return (X*np.cos(th)+Y*np.sin(th))/I
def dom(ch,ci,Blo=3.5):
    sel=np.arange(ndone)*nfast+ci; Bc=B[sel]; Rc=proj(ch)[sel]; o=np.argsort(Bc); Bc=Bc[o]; Rc=Rc[o]
    m=(Bc>=Blo)&(Bc<=8);
    if m.sum()<25: return np.nan,np.nan
    Bw=Bc[m]; Rw=Rc[m]; dR=Rw-np.polyval(np.polyfit(Bw,Rw,4),Bw)
    invB=1/Bw; ub=np.linspace((1/Bw).min(),(1/Bw).max(),16384)
    dRi=np.interp(ub,np.sort(invB),dR[np.argsort(invB)])
    F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0]); A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
    band=(F>10)&(F<140); k=np.argmax(A*band); return F[k], A[k]/np.median(A[band])
ns=[]; FL=[]; f2=[]; f1=[]
for ci in range(1,nfast):
    n=K*Vbg[ci]; ns.append(n/1e12); FL.append(cst.h*abs(n)*1e4/(4*cst.e))
    f2.append(dom('sr2',ci)[0]); f1.append(dom('sr1',ci)[0])
ns=np.abs(np.array(ns)); FL=np.array(FL); f1=np.array(f1); f2=np.array(f2)
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
for a,(nm,f,c) in zip([ax[0],ax[0]],[('sr2 B4-B5',f2,'C0'),('sr1 T3-T4',f1,'C1')]):
    ax[0].plot(ns,f,'o-',color=c,label=nm)
ax[0].plot(ns,FL,'k--',label='F_L=(h/4e)n (single FS / ABC)')
ax[0].plot(ns,0.7*FL,'r:',alpha=.6,label='0.7 F_L (e.g. ABA BL if ML~0.3)')
ax[0].set_xlabel('|n| (1e12 cm^-2)'); ax[0].set_ylabel('dominant F (T)'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('Dominant SdH tone vs F_L across density')
# ratio F/F_L
ax[1].plot(ns,f2/FL,'o-',color='C0',label='sr2'); ax[1].plot(ns,f1/FL,'o-',color='C1',label='sr1')
ax[1].axhline(1.0,color='k',ls='--',label='F=F_L (ABC single FS)'); ax[1].axhline(0.7,color='r',ls=':',alpha=.6,label='ABA BL frac')
ax[1].set_xlabel('|n| (1e12 cm^-2)'); ax[1].set_ylabel('F_dominant / F_L'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3); ax[1].set_ylim(0,1.5)
ax[1].set_title('F/F_L (=1 => single Fermi surface)')
plt.suptitle(f'QC0426 fan (data/7) F(n) — rows {ndone}/157')
plt.tight_layout(); plt.savefig('hera_scratch/fan_fn.png',dpi=110)
# quantify
good=np.isfinite(f2)&(ns>4.3)  # clean higher-n columns
print(f"clean cols |n|>4.3e12: F_dom/F_L  sr2 = {np.nanmean((f2/FL)[good]):.2f}+-{np.nanstd((f2/FL)[good]):.2f}, sr1 = {np.nanmean((f1/FL)[good]):.2f}+-{np.nanstd((f1/FL)[good]):.2f}")
print("F/F_L ~ 1 => single Fermi surface carrying full density (ABC). <1 with a 2nd tone => ABA pair.")
print("saved fan_fn.png")
