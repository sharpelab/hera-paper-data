# Run 4 — RAW Landau fan (the missing raw-first plot). Rxx(n,B) and Rxy(n,B) re-formed from
# data/4 TSV, plus per-column background-subtracted dRxx(n,B) where the LL/SdH minima fan out.
import numpy as np, json
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, luttinger_frequency

run = open_run("data/4"); md = json.load(open("data/4/metadata.json"))
cols=md["columns"]; ci={c:i for i,c in enumerate(cols)}
NB=len(md["slow_setpoints"][0]); NF=len(md["fast_setpoints"][0])
A=np.column_stack([run.col(c) for c in cols]).reshape(NB,NF,len(cols))
B=A[:,0,ci["magnet_mag"]]; I=A[:,:,ci["sr0_X"]]/1e6
c_tg,c_bg,n_off=1.7027e-3,2.2004e-3,-1.581e15
n12=((c_tg*A[0,:,ci["DC_bias"]]+c_bg*A[0,:,ci["k_2400_volt"]])/1.602176634e-19+n_off)/1e16
R={ch:np.abs(A[:,:,ci[f"{ch}_X"]]/I) for ch in ("sr1","sr2","sr3")}   # (NB, NF)

def dRxx(Rg):                              # per-column 5th-poly background removed
    D=np.full_like(Rg,np.nan)
    for j in range(NF):
        if Rg[:,j].max()>540: continue     # skip clipped low-n columns
        D[:,j]=Rg[:,j]-np.polyval(np.polyfit(B,Rg[:,j],5),B)
    return D

fig,ax=plt.subplots(2,2,figsize=(15,10),constrained_layout=True)
# raw Rxx sr1
im=ax[0,0].pcolormesh(n12,B,np.clip(R["sr1"],0,400),shading="auto",cmap="viridis")
fig.colorbar(im,ax=ax[0,0],label="Rxx (Ω, clip 400)"); ax[0,0].set_title("RAW Rxx(n,B) — sr1 (T3-T4)")
# dRxx sr1 — the Landau fan (diagonal LL minima)
d=dRxx(R["sr1"]); v=np.nanpercentile(np.abs(d),98)
im=ax[0,1].pcolormesh(n12,B,d,shading="auto",cmap="RdBu_r",vmin=-v,vmax=v)
fig.colorbar(im,ax=ax[0,1],label="ΔRxx (Ω, bkgd removed)"); ax[0,1].set_title("ΔRxx(n,B) — sr1: SdH/LL fan")
# raw Rxx sr2
im=ax[1,0].pcolormesh(n12,B,np.clip(R["sr2"],0,300),shading="auto",cmap="viridis")
fig.colorbar(im,ax=ax[1,0],label="Rxx (Ω, clip 300)"); ax[1,0].set_title("RAW Rxx(n,B) — sr2 (B4-B5)")
# raw Rxy sr3
im=ax[1,1].pcolormesh(n12,B,np.clip(R["sr3"],0,1000),shading="auto",cmap="magma")
fig.colorbar(im,ax=ax[1,1],label="Rxy (Ω, clip 1000)"); ax[1,1].set_title("RAW Rxy(n,B) — sr3 (Hall)")
for a in ax.ravel(): a.set_xlabel("n (1e12 cm^-2)"); a.set_ylabel("B (T)")
fig.suptitle("Run 4 — electron Landau fan, RAW (re-formed from TSV). Diagonal stripes in ΔRxx = the fanning LL minima.")
plt.show()
print("raw fan: B %.2f-%.2f T x n %.2f-%.2f e12; clipped low-n columns (n<~%.1f) excluded from ΔRxx"
      %(B.min(),B.max(),n12.min(),n12.max(), n12[(R['sr1'].max(0)>540)].max() if (R['sr1'].max(0)>540).any() else 0))
