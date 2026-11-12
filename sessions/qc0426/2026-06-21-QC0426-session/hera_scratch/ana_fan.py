import os, numpy as np, hera.analysis as a
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
MDIR = r"C:\Users\DGG\VTI_local_data\zack\20260621-QC0426"
run = a.open_run(os.path.join(MDIR,"data","4"))
fg=a.fan_grids(run); B=np.asarray(fg.slow); rg=a.resistance_grids(fg); R1=rg.R["sr1"]
ncol=R1.shape[1]; ns=np.linspace(-0.7,-2.5,ncol); FL=np.array([float(a.luttinger_frequency(abs(n)*1e16)) for n in ns])
print("fan: %dx%d, B[%.2f,%.2f], not interrupted=%s"%(R1.shape[0],ncol,B.min(),B.max(),not run.interrupted))
# dominant tone per column (cut 1.0, f>6 to skip the ~6T MR-bg artifact)
Fdom=np.full(ncol,np.nan)
f,mag=a.sdh_fft(R1,B,b_range=(1.0,7.9),bg_degree=5)
for c in range(ncol):
    m=mag[c]; sel=f>6; ff,mm=f[sel],m[sel]
    pk,_=find_peaks(mm,prominence=mm.max()*0.2)
    if len(pk): Fdom[c]=ff[pk[np.argmax(mm[pk])]]
fig,ax=plt.subplots(1,2,figsize=(14,5))
im=ax[0].pcolormesh(ns,B,np.log10(np.abs(R1)),shading="auto",cmap="inferno")
plt.colorbar(im,ax=ax[0],label="log10 Rxx (Ω)"); ax[0].set_xlabel("n (1e12 cm⁻²)"); ax[0].set_ylabel("B (T)"); ax[0].set_title("sr1 Rxx(n,B) — Landau fan")
ax[1].plot(ns,FL,"k--",lw=2,label="F_L = h|n|/4e")
ax[1].plot(ns,FL/2,"gray",ls=":",label="F_L/2")
ax[1].scatter(ns,Fdom,s=20,c="r",label="dominant SdH tone")
ax[1].set_xlabel("n (1e12 cm⁻²)"); ax[1].set_ylabel("F (T)"); ax[1].set_title("Dominant F(n) tracks F_L (main pocket = full Luttinger density)"); ax[1].legend(fontsize=8); ax[1].set_ylim(0,30)
fig.suptitle("Run 4 fan — F(n): dominant pocket at F_L; sub-F_L structure ambiguous (see scratch diagnostics)")
fig.tight_layout(); plt.show()
print("dominant tone / F_L: median=%.2f (1.0 = main pocket carries full density)"%np.nanmedian(Fdom/FL))
