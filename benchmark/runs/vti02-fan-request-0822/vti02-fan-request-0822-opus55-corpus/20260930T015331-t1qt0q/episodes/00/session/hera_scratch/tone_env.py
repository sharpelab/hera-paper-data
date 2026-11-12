"""Sliding-window amplitude of specific tones vs B (run 6 electron, run 7 hole) — onset sanity for the censored 7.3 T tone."""
import numpy as np, warnings; warnings.filterwarnings("ignore")
from hera.analysis import open_run
def load(rid):
    r=open_run(f"data/{rid}"); B=r.col("magnet_field"); R=r.col("sr1_X")/(r.col("sr0_X")/-1e6)
    o=np.argsort(B); return B[o],R[o]
for rid,blo,tones in ((6,1.0,[7.3,22.4,29.6]),(7,0.5,[6.6,5.3,12.3])):
    B,R=load(rid); m=B>=blo; B,R=B[m],R[m]
    p=np.polyfit(B,R,7); dR=R-np.polyval(p,B)
    x=1/B; o=np.argsort(x); x,dR=x[o],dR[o]
    xu=np.linspace(x.min(),x.max(),4000); yu=np.interp(xu,x,dR)
    for F in tones:
        w=3.0/F; out=[]
        for c in np.arange(xu.min()+w/2, xu.max()-w/2, w/3):
            s=(xu>c-w/2)&(xu<c+w/2); xx=xu[s]; yy=yu[s]-yu[s].mean(); h=np.hanning(len(xx))
            a=2*abs(np.sum(yy*h*np.exp(-2j*np.pi*F*xx)))/h.sum()
            # noise: off-tone projections
            offs=[2*abs(np.sum(yy*h*np.exp(-2j*np.pi*f*xx)))/h.sum() for f in (F*1.5+3, F*1.8+5, F*2.3+7)]
            out.append((1/c, a, np.mean(offs)))
        print(f"run {rid} tone {F} T:", " ".join(f"{b:.2f}T:{a:.1f}/{nz:.1f}" for b,a,nz in out))
