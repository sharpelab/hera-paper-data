import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

r=open_run("data/11"); print(summarize_run(r))
cfg=json.load(open("data/11/metadata.json"))["measurement_config"]
print("comment:", cfg.get("comment"))
vdc=r.col("dc205_1_voltage")
Idc=vdc/cfg["bias_resistor"]*1e9          # nA
I_ac=r.col("sr830_1_X")/cfg["sr1_gain"]   # AC current (A)
dVdI=(r.col("sr830_3_X")/cfg["sr3_gain"])/I_ac   # differential R (Ohm)
N=len(vdc); half=N//2
print(f"pts {N}, Idc range [{Idc.min():.1f},{Idc.max():.1f}] nA")
print(f"dV/dI: min={np.nanmin(dVdI):.2f} Ω  at Idc={Idc[np.nanargmin(dVdI)]:.2f} nA")
print(f"dV/dI at |Idc|<1nA (zero-bias): {np.nanmedian(dVdI[np.abs(Idc)<1]):.2f} Ω")
print(f"dV/dI at |Idc|>15nA (high bias / normal): {np.nanmedian(dVdI[np.abs(Idc)>15]):.1f} Ω")
# critical current: where dV/dI rises through a threshold (e.g. half of normal)
try:
    from sharpelab_nb.sc import extract_critical_current
    icn,icp=extract_critical_current(Idc[:half], dVdI[:half], threshold=10)
    print(f"extract_critical_current (fwd, thr=10Ω): Ic- = {icn:.2f}, Ic+ = {icp:.2f} nA")
except Exception as e:
    print("extract_critical_current unavailable:", e)

fig,ax=plt.subplots(figsize=(8,5))
ax.plot(Idc[:half],dVdI[:half],'.-',ms=3,label='forward')
ax.plot(Idc[half:],dVdI[half:],'.-',ms=3,alpha=.6,label='backward')
ax.set(xlabel="I_dc (nA)",ylabel="dV/dI (Ω)",title="Run 11 — bias spectroscopy at n=-5.02e11, D=-0.673, B=0")
ax.axhline(0,c='gray',lw=.5); ax.legend(); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig("hera_scratch/bias.png",dpi=120); print("saved bias.png")
