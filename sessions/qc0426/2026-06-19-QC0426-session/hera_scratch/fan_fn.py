# Fan F(n): per-column 1/B FFT, both channels, vs F_L(n) and the Luttinger partition
import numpy as np, json, os
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
Vbg_fast=np.array(fast_sp[1]); K=2.760e12
def proj(ch):
    X=raw[:,idx[ch+'_X']]; Y=raw[:,idx[ch+'_Y']]; th=np.arctan2(np.median(Y),np.median(X)); return (X*np.cos(th)+Y*np.sin(th))/I
def col_fft(ch, ci, Blo=3.5):
    sel=np.arange(ndone)*nfast+ci; Bc=B[sel]; Rc=proj(ch)[sel]
    o=np.argsort(Bc); Bc=Bc[o]; Rc=Rc[o]
    m=(Bc>=Blo)&(Bc<=8.0)
    if m.sum()<25: return None
    Bw=Bc[m]; Rw=Rc[m]; p=np.polyfit(Bw,Rw,4); dR=Rw-np.polyval(p,Bw)
    invB=1/Bw; ordr=np.argsort(invB); ub=np.linspace(invB[ordr].min(),invB[ordr].max(),16384)
    dRi=np.interp(ub,invB[ordr],dR[ordr]); F=np.fft.rfftfreq(len(ub),d=ub[1]-ub[0])
    A=np.abs(np.fft.rfft((dRi-dRi.mean())*np.hanning(len(dRi))))
    fl=np.median(A[(F>6)&(F<150)]); pk,_=find_peaks(A,height=fl*4,distance=3)
    pk=pk[(F[pk]>5)&(F[pk]<140)]; pk=pk[np.argsort(A[pk])[::-1]]
    return F,A,[(round(float(F[k]),1),round(float(A[k]/fl),1)) for k in pk[:5]], float(np.std(dR))
print(f"rows {ndone}/157. F_L=(h/4e)n.  Per-column tones (skip col0 throwaway):")
print(f"{'n(e12)':>8} {'F_L':>5} | sr2 peaks(F:SNR)            | sr1 peaks(F:SNR)")
results={}
for ci in range(1,nfast):
    n_cm=K*Vbg_fast[ci]; FL=cst.h*abs(n_cm)*1e4/(4*cst.e)
    r2=col_fft('sr2',ci); r1=col_fft('sr1',ci)
    if r2 is None: continue
    s2=" ".join(f"{f:.0f}:{s:.1f}" for f,s in r2[2]) if r2[2] else "(none)"
    s1=" ".join(f"{f:.0f}:{s:.1f}" for f,s in r1[2]) if r1 and r1[2] else "(none)"
    print(f"{n_cm/1e12:8.2f} {FL:5.0f} | {s2:26} | {s1}")
    results[round(float(n_cm/1e12),2)]=dict(FL=float(FL), sr2=r2[2], sr1=r1[2] if r1 else [])
np.save("hera_scratch/fan_results.npy", results, allow_pickle=True)
print("\nsaved fan_results.npy")
