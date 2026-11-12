import json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run
from scipy.ndimage import gaussian_filter1d

def load(i):
    r = open_run(f"data/{i}")
    cfg = json.load(open(Path("data")/str(i)/"metadata.json"))["measurement_config"]
    Ib = cfg["bias_voltage_1"]/cfg["bias_resistor"]
    bg = r.col_at(1)
    return r, cfg, Ib, bg

r1, c1, Ib1, bg1 = load(1)
print(summarize_run(r1))
print("I_bias run1 =", Ib1)

x2 = r1.col("sr830_2_X"); p2 = r1.col("sr830_2_P")
x3 = r1.col("sr830_3_X"); p3 = r1.col("sr830_3_P")
R2 = (x2/c1["sr2_gain"])/Ib1
R3 = (x3/c1["sr3_gain"])/Ib1

print(f"\n2T: X med={np.median(x2):.3e} V  range[{np.min(x2):.3e},{np.max(x2):.3e}]  R2 med={np.median(R2)/1e3:.2f} kΩ")
print(f"2T phase P: med={np.median(p2):.1f}  range[{np.min(p2):.1f},{np.max(p2):.1f}] deg")
print(f"4T: X med={np.median(x3):.3e} V  R3 med={np.median(R3):.1f} Ω  R3 max={np.nanmax(R3):.0f} Ω")
print(f"4T phase P: med={np.median(p3):.1f}  range[{np.min(p3):.1f},{np.max(p3):.1f}] deg")

# compare 2T run0 vs run1
r0, c0, Ib0, bg0 = load(0)
R2_0 = (r0.col("sr830_2_X")/c0["sr2_gain"])/Ib0
print(f"\nrun0 2T CNP={np.nanmax(R2_0)/1e3:.1f} kΩ baseline={np.nanmin(R2_0)/1e3:.1f} kΩ")
print(f"run1 2T max={np.nanmax(R2)/1e3:.2f} kΩ min={np.nanmin(R2)/1e3:.2f} kΩ (flat? std={np.std(R2):.1f} Ω)")

R3s = gaussian_filter1d(R3,2)
icnp = int(np.nanargmax(R3s))
noise = np.nanstd(R3[bg1>2.5])
print(f"\n4T CNP at BG={bg1[icnp]:+.3f} V  R3s_peak={R3s[icnp]:.0f} Ω; metallic σ(BG>2.5)={noise:.2f} Ω -> SNR~{R3s[icnp]/noise:.0f}")
print(f"4T low-Rxx (BG=+4.2 end) ~{np.median(R3[bg1>3.5]):.1f} Ω")

fig,ax=plt.subplots(3,1,figsize=(7,9),sharex=True)
ax[0].plot(bg0,R2_0/1e3,'.-',ms=2,label='run0 40pA'); ax[0].plot(bg1,R2/1e3,'.-',ms=2,label='run1 1nA')
ax[0].set_ylabel("2T R (kΩ)"); ax[0].legend(); ax[0].set_title("Run 1 (1 nA) vs Run 0 (40 pA)")
ax[1].plot(bg1,R3,'.-',ms=2); ax[1].plot(bg1,R3s,'k-'); ax[1].set_ylabel("4T R (Ω) run1"); ax[1].axhline(0,c='gray',lw=.5)
ax[2].plot(bg1,p2,'.-',ms=2,label='2T phase'); ax[2].plot(bg1,p3,'.-',ms=2,label='4T phase')
ax[2].set_ylabel("phase (deg)"); ax[2].set_xlabel("BG (V)"); ax[2].legend()
plt.tight_layout(); plt.savefig("hera_scratch/run1.png",dpi=110)
print("saved hera_scratch/run1.png")
