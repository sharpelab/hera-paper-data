import numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

m=json.load(open("data/2/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/2/data.tsv.gz")
B=d[:,ci["magnet_mag"]]; I_bias=5e-9
F_tot=abs(-4.0e12*1e4)*6.62607e-34/(4*1.602177e-19)
print(f"Luttinger F_tot(n=-4e12) = {F_tot:.1f} T")

def spec(col, Blo, Bhi, detr, N=2048):
    sel=(B>=Blo)&(B<=Bhi); x=1.0/B[sel]; R=d[sel,ci[col]]/I_bias
    o=np.argsort(x); x,R=x[o],R[o]
    xu=np.linspace(x.min(),x.max(),N); Ru=np.interp(xu,x,R); dx=xu[1]-xu[0]
    if detr[0]=="poly":
        osc=Ru-np.polyval(np.polyfit(xu,Ru,detr[1]),xu)
    else:  # gaussian high-pass, sigma in x-units
        sig=detr[1]/dx; osc=Ru-gaussian_filter1d(Ru,sig)
    w=osc*np.hanning(N)
    F=np.fft.rfftfreq(N,d=dx); A=np.abs(np.fft.rfft(w))
    return F,A,x.max()-x.min()

detrenders=[("poly",6),("poly",8),("gauss",0.045)]
windows=[("B[2.5,7.95]",2.5,7.95),("B[1.5,7.95]",1.5,7.95)]
fig,ax=plt.subplots(len(windows),2,figsize=(13,8))
for wi,(wl,Blo,Bhi) in enumerate(windows):
    for col,c in [("sr1_X","C0"),("sr2_X","C1")]:
        axc=ax[wi][0 if col=="sr1_X" else 1]
        print(f"\n--- {col} {wl} (dF_res~{1/(1/Blo-1/Bhi):.1f} T) ---")
        for dt in detrenders:
            F,A,span=spec(col,Blo,Bhi,dt)
            k=(F>3)&(F<55); Fk,Ak=F[k],A[k]/A[(F>3)&(F<55)].max()
            pk,_=find_peaks(Ak,height=0.3,distance=10)
            pk=pk[np.argsort(Ak[pk])[::-1]][:4]; peaks=sorted(Fk[pk])
            print(f"  {dt}: peaks[T]={', '.join(f'{p:.1f}' for p in peaks)}")
            axc.plot(Fk,Ak,label=f"{dt[0]}{dt[1]}",lw=.9)
        axc.axvline(F_tot,color='g',ls='--',lw=.8)
        axc.set_title(f"{col} {wl}"); axc.set_xlabel("F (T)"); axc.legend(fontsize=7)
plt.tight_layout(); plt.savefig("hera_scratch/gonogo_fft2.png",dpi=110)
print("\nsaved hera_scratch/gonogo_fft2.png")
