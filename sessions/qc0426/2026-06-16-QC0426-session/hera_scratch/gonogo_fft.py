import numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

m=json.load(open("data/2/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/2/data.tsv.gz")
B=d[:,ci["magnet_mag"]]; I_bias=5e-9
# Luttinger total-frequency expectation at this n
n_cm2=-4.0e12; F_tot_expect=abs(n_cm2*1e4)*6.62607e-34/(4*1.602177e-19)
print(f"n={n_cm2:.1e} cm^-2 -> Luttinger F_tot = {F_tot_expect:.1f} T (sum of pockets)")

def fft_window(R, Blo, Bhi, npad=4096, polydeg=2):
    sel=(B>=Blo)&(B<=Bhi)
    Bw=B[sel]; Rw=R[sel]
    x=1.0/Bw                              # oscillation periodic in x=1/B
    order=np.argsort(x); x=x[order]; Rw=Rw[order]
    xu=np.linspace(x.min(), x.max(), npad)
    Ru=np.interp(xu, x, Rw)
    Ru=Ru-np.polyval(np.polyfit(xu,Ru,polydeg),xu)   # detrend
    Ru=Ru*np.hanning(len(Ru))
    F=np.fft.rfftfreq(npad, d=(xu[1]-xu[0]))          # cycles per 1/B = Tesla
    A=np.abs(np.fft.rfft(Ru))
    return F, A, sel.sum()

fig,ax=plt.subplots(2,2,figsize=(13,9))
windows=[("low-field B[0.4,3.0] (ML)",0.4,3.0),("high-field B[1.0,7.95] (BL)",1.0,7.95)]
for col,row in [("sr1_X",0),("sr2_X",1)]:
    R=d[:,ci[col]]/I_bias
    for w,(lbl,Blo,Bhi) in enumerate(windows):
        F,A,npts=fft_window(R,Blo,Bhi)
        keep=(F>0.3)&(F<60)
        Fk,Ak=F[keep],A[keep]
        pk,_=find_peaks(Ak,height=Ak.max()*0.15,distance=8)
        pk=pk[np.argsort(Ak[pk])[::-1]][:5]
        peaks=sorted(Fk[pk])
        print(f"{col} {lbl}: {npts} pts, peaks[T] = {', '.join(f'{p:.1f}' for p in peaks)}")
        ax[row,w].plot(Fk,Ak/Ak.max())
        for p in peaks: ax[row,w].axvline(p,color='r',ls=':',lw=.8); ax[row,w].text(p,1.0,f'{p:.1f}',fontsize=7,color='r')
        ax[row,w].axvline(F_tot_expect,color='g',ls='--',lw=.8)
        ax[row,w].set_title(f"{col} {lbl}"); ax[row,w].set_xlabel("F (T)"); ax[row,w].set_xlim(0,55)
plt.tight_layout(); plt.savefig("hera_scratch/gonogo_fft.png",dpi=110)
print("saved hera_scratch/gonogo_fft.png  (green dashed = Luttinger F_tot)")

# Also raw R vs 1/B for sr1 (eyeball)
fig2,ax2=plt.subplots(figsize=(8,4))
R1=d[:,ci["sr1_X"]]/I_bias; sel=B>0.4
ax2.plot(1/B[sel],R1[sel],lw=.6); ax2.set_xlabel("1/B (1/T)"); ax2.set_ylabel("sr1 Rxx (ohm)")
ax2.set_title("sr1 Rxx vs 1/B (raw)")
plt.tight_layout(); plt.savefig("hera_scratch/gonogo_rawosc.png",dpi=110)
print("saved hera_scratch/gonogo_rawosc.png")
