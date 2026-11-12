import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run
import scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e

def load(fid):
    r=open_run(f"data/{fid}"); cfg=json.load(open(f"data/{fid}/metadata.json"))["measurement_config"]
    vtg=r.col("k_tg_volt"); vbg=r.col("k_bg_volt")
    I=r.col("sr830_1_X")/cfg["sr1_gain"]; X4=r.col("sr830_3_X")
    Rxx=(X4/cfg["sr3_gain"])/I
    n=((c_tg*vtg+c_bg*vbg)/cst.e+n_off)*1e-4
    D=(c_tg*vtg-c_bg*vbg)/(2*cst.epsilon_0)*1e-9
    clip=np.abs(X4)>2e-4*0.98
    return n,np.median(D),Rxx,clip

fig,ax=plt.subplots(figsize=(8,5))
for fid,c in [(5,'C0'),(6,'C1'),(7,'C2')]:
    n,D,Rxx,clip=load(fid)
    ax.plot(n/1e11,Rxx,'-',color=c,lw=1.2,label=f"run{fid} D={D:+.2f} V/nm")
    if clip.sum(): ax.plot(n[clip]/1e11,Rxx[clip],'.',color=c,ms=4,alpha=.4)
    cand=(n<-4e11)&(n>-6e11)
    print(f"run{fid} D={D:+.2f}: clip {int(clip.sum())}/200; candidate band Rxx med={np.nanmedian(Rxx[cand]):.0f} min={np.nanmin(Rxx[cand]):.0f} Ω; "
          f"global min={np.nanmin(Rxx):.1f} Ω; deep-hole floor={np.nanmedian(Rxx[n<-7e11]):.0f} Ω")
ax.axhline(0,c='gray',lw=.5); ax.axvspan(-6,-4,color='cyan',alpha=.12,label='prior n band')
ax.set(xlabel="n (1e11 cm^-2)",ylabel="4T Rxx (Ω)",ylim=(-5,400),
       title="Clean n-linecuts (sr3 fixed): no Rxx→0 anywhere; gap toward CNP, metallic into deep hole")
ax.legend(); plt.tight_layout(); plt.savefig("hera_scratch/clean_linecuts.png",dpi=110); print("saved")
