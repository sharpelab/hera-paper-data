import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sweep import raster
from sharpelab_nb.gates import calculate_gate_voltages

DTG, DBG, EP = 23.6, 20.0, 3.0
TGL, TGH, BGL, BGH = -7.0, 6.0, -4.0, 4.2
N_LO, N_HI = -0.70, -0.10
D_LO, D_HI = -0.70, -0.45        # D_LO generous; sanitize clips beyond Vbg=4.2
SEC_PER_PT = 1.4                 # measured-ish multisweep rate (3 lock-ins + delay 1.2)
TARGET_HR = 8.0

def inrange(vt, vb): return (vt>TGL)&(vt<TGH)&(vb>BGL)&(vb<BGH)

# accessible negative-D boundary vs n (where Vbg hits 4.2)
print("Vbg=4.2 boundary (max accessible -D) vs n:")
for n in np.arange(-0.7, -0.05, 0.1):
    Dg = np.arange(-0.45, -0.85, -0.005)
    vt, vb = calculate_gate_voltages(n*np.ones_like(Dg), Dg, dtg=DTG, dbg=DBG, ep=EP)
    okD = Dg[inrange(vt, vb)]
    print(f"  n={n:+.2f}: D accessible {okD.min():.3f}..{okD.max():.3f}")

# tune NX,NY for ~TARGET_HR
aspect = (N_HI-N_LO)/(D_HI-D_LO)
for NY in (90, 100, 110, 120, 130):
    NX = int(round(NY*aspect))
    verts = np.array([[N_LO,D_LO],[N_HI,D_LO],[N_HI,D_HI],[N_LO,D_HI],[N_LO,D_LO]])
    ns, Ds = raster.rasterize(verts, NX, NY, 0)
    vt, vb = calculate_gate_voltages(ns, Ds, dtg=DTG, dbg=DBG, ep=EP)
    ok = inrange(vt, vb)
    hrs = ok.sum()*SEC_PER_PT/3600
    print(f"NX={NX} NY={NY}: raster {len(ns)}, in-range {ok.sum()} ({100*ok.mean():.0f}%), "
          f"dn={ (N_HI-N_LO)/NX:.4f} dD={(D_HI-D_LO)/NY:.4f}  ~{hrs:.1f} h")

# final preview NX=240 NY=100
NX,NY=240,100
verts=np.array([[N_LO,D_LO],[N_HI,D_LO],[N_HI,D_HI],[N_LO,D_HI],[N_LO,D_LO]])
ns,Ds=raster.rasterize(verts,NX,NY,0)
vt,vb=calculate_gate_voltages(ns,Ds,dtg=DTG,dbg=DBG,ep=EP)
ok=inrange(vt,vb)
fig,ax=plt.subplots(1,2,figsize=(13,5))
ax[0].scatter(vt[ok],vb[ok],s=1,c="C0"); ax[0].scatter(vt[~ok],vb[~ok],s=1,c="C3")
ax[0].axhline(4.2,color="k",ls=":"); ax[0].set(xlabel="Vtg",ylabel="Vbg",title=f"{ok.sum()} in-range pts -> gates")
ax[1].scatter(ns[ok],Ds[ok],s=1,c="C0"); ax[1].scatter(ns[~ok],Ds[~ok],s=1,c="C3",label="clip (Vbg>4.2)")
ax[1].plot(-0.4654,-0.6501,"y*",ms=16,label="run-5 dip"); ax[1].legend(fontsize=8)
ax[1].set(xlabel="n (e12 cm^-2)",ylabel="D (V/nm)",title="(n,D) coverage")
plt.tight_layout(); plt.savefig("hera_scratch/nd_design2.png",dpi=110); print("saved nd_design2.png ; in-range",ok.sum())
