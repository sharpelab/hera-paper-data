import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

run = open_run("data/0")
mc = run.meta["measurement_config"]
Ibias = mc["bias_voltage_1"] / mc["bias_resistor"]
vbg = run.col_at(run.col_indices("k_bg_volt")[-1])

i_sr1 = run.col("sr830_1_X") / mc["sr1_gain"]
R2 = (run.col("sr830_2_X")/1e2)/Ibias
R3 = (run.col("sr830_3_X")/1e2)/Ibias
itg = run.col("k_tg_curr"); ibg = run.col("k_bg_curr")

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
fig.suptitle(f"Gate C liveness — zf1 run 0 — k_bg sweep at k_tg=0, B~0, T=34mK, I_bias={Ibias*1e12:.0f}pA", fontsize=11)

ax[0,0].plot(vbg, i_sr1*1e12, ".-", ms=3)
ax[0,0].axhline(Ibias*1e12, color="r", ls=":", label=f"I_bias {Ibias*1e12:.0f}pA")
ax[0,0].set(xlabel="k_bg (V)", ylabel="I sr830_1 (pA)", title="current channel 5-4 (alive: pinned at I_bias)")
ax[0,0].legend(fontsize=8)

ax[0,1].plot(vbg, R2/1e3, ".-", ms=3)
ax[0,1].set(xlabel="k_bg (V)", ylabel="R 2T (kΩ)", title="sr830_2 5-4 (2-terminal): CNP peak ~+0.1V")

ax[1,0].plot(vbg, R3, ".-", ms=3, color="C2")
ax[1,0].axhline(0, color="k", lw=0.5)
ax[1,0].set(xlabel="k_bg (V)", ylabel="R 4T Rxx (Ω)", title="sr830_3 30-31 (4-TERMINAL Rxx): CNP peak 657Ω @ k_bg~0")

ax[1,1].plot(vbg, np.abs(itg)*1e12, ".-", ms=3, label="|I_tg|")
ax[1,1].plot(vbg, np.abs(ibg)*1e12, ".-", ms=3, label="|I_bg|")
ax[1,1].axhline(100, color="r", ls=":", label="100 pA watch")
ax[1,1].set(xlabel="k_bg (V)", ylabel="gate leakage (pA)", title="leakage (nplci=10): <45 pA, clean")
ax[1,1].legend(fontsize=8)

plt.tight_layout()
out = "hera_scratch/gateC_liveness.png"
plt.savefig(out, dpi=110)
print("saved", out)
