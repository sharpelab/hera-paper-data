import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

fig,ax=plt.subplots(1,2,figsize=(13,5))
for fid,lab,c in [(12,'sweep A (+50->0)','C0'),(13,'sweep B (-50->0)','C1')]:
    try:
        r=open_run(f"data/{fid}")
    except Exception as e:
        print(f"run {fid}: not available ({e})"); continue
    cfg=json.load(open(f"data/{fid}/metadata.json"))["measurement_config"]
    Bmt=r.col("magnet_field")*1e3
    I_ac=r.col("sr830_1_X")/cfg["sr1_gain"]
    Rxx=(r.col("sr830_3_X")/cfg["sr3_gain"])/I_ac
    Tm=r.col("T")*1e3
    print(f"run {fid}: {summarize_run(r).splitlines()[1].strip()}  B=[{Bmt.min():.1f},{Bmt.max():.1f}]mT")
    print(f"  Rxx: min={np.nanmin(Rxx):.2f}Ω at B={Bmt[np.nanargmin(Rxx)]:+.1f}mT ; at |B|>40mT={np.nanmedian(Rxx[np.abs(Bmt)>40]):.0f}Ω")
    print(f"  T during sweep: {Tm.min():.0f}-{Tm.max():.0f} mK (heating check)")
    ax[0].plot(Bmt,Rxx,'.-',ms=3,color=c,label=lab)
    ax[1].plot(Bmt,Tm,'.-',ms=3,color=c,label=lab)
ax[0].set(xlabel="B (mT)",ylabel="Rxx (Ω)",title="B⊥ field-killing at SC arc min (Idc=0)"); ax[0].axhline(0,c='gray',lw=.5); ax[0].axvline(0,c='gray',lw=.4); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].set(xlabel="B (mT)",ylabel="T (mK)",title="sample T (ramp-heating check)"); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("hera_scratch/bperp.png",dpi=120); print("saved bperp.png")
