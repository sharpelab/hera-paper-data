import gzip, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(rid):
    md=json.load(open(f"data/{rid}/metadata.json")); cols=md["columns"]
    with gzip.open(f"data/{rid}/data.tsv.gz","rt") as f: arr=np.genfromtxt(f,delimiter="\t")
    idx={}; [idx.setdefault(c,i) for i,c in enumerate(cols)]
    d={k:arr[:,idx[k]] for k in idx}
    return d
# device-card arithmetic: I_bias = 0.1V/100MOhm = 1 nA; Rxx = (sr830_3_X/100)/I_bias
Ibias=1e-9
def Rxx(d): return (d["sr830_3_X"]/100.0)/Ibias
def R2T(d): return (d["sr830_2_X"]/100.0)/Ibias

legs={0:("k_tg",+6),1:("k_tg",-7),2:("k_bg",+4.2),3:("k_bg",-4)}
D={r:load(r) for r in legs}

fig,ax=plt.subplots(2,2,figsize=(11,7),sharex="col")
# TG column: legs 0(+) and 1(-), x=V_tg
for r,c in [(1,"-"),(0,"+")]:
    d=D[r]; v=d["k_tg_volt"]
    o=np.argsort(v)
    ax[0,0].plot(v[o],d["k_tg_curr"][o]*1e12,".",ms=3,label=f"leg{r}")
    ax[1,0].plot(v[o],Rxx(d)[o],".",ms=3)
ax[0,0].set_title("TG axis (BG=0)"); ax[0,0].set_ylabel("k_tg leakage (pA)")
ax[1,0].set_ylabel("4T Rxx 30-31 (Ω)"); ax[1,0].set_xlabel("V_tg (V)")
# BG column: legs 2(+) and 3(-), x=V_bg
for r in [3,2]:
    d=D[r]; v=d["k_bg_volt"]; o=np.argsort(v)
    ax[0,1].plot(v[o],d["k_bg_curr"][o]*1e12,".",ms=3,label=f"leg{r}")
    ax[1,1].plot(v[o],Rxx(d)[o],".",ms=3)
ax[0,1].set_title("BG axis (TG=0)"); ax[0,1].set_ylabel("k_bg leakage (pA)")
ax[1,1].set_ylabel("4T Rxx 30-31 (Ω)"); ax[1,1].set_xlabel("V_bg (V)")
for a in ax.flat: a.grid(alpha=.3)
fig.suptitle("zf1 Gate-C liveness — leakage + 4T Rxx vs each gate (other gate=0), base T, B≈0")
fig.tight_layout()
fig.savefig("hera_scratch/gateC_liveness.png",dpi=110)
# numeric summary
for r,(g,ep) in legs.items():
    d=D[r]; cc=d[g+"_curr"]
    print(f"leg{r} {g}->{ep:+g}V: leak med {np.median(cc)*1e12:+.1f} pA, |max| {np.max(np.abs(cc))*1e12:.1f} pA; Rxx range {Rxx(d).min():.1f}-{Rxx(d).max():.1f} Ω")
print("saved hera_scratch/gateC_liveness.png")
