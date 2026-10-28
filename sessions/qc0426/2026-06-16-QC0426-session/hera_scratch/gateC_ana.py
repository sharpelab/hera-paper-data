import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("interrupted:", run.interrupted)
print("cols:", list(run.cols))

vtg = run.col("DC_bias")
I = run.col("sr0_X") / (-1e6)          # current channel, gain -1e6
I_bias = 5e-9

def R(name):
    return run.col(name) / I_bias

# Leakage
for c in run.cols:
    if "curr" in c.lower():
        print(f"leak {c}: max|I| = {np.abs(run.col(c)).max():.3e} A")

print("I (drain) med/min/max nA:", np.median(I)*1e9, I.min()*1e9, I.max()*1e9)

fig, ax = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
for nm, col in [("sr1 Rxx T3-T4","sr1_X"), ("sr2 Rxx B4-B5","sr2_X")]:
    r = R(col)
    icnp = np.argmax(r)
    print(f"{nm}: Rxx peak {r[icnp]:.1f} ohm at DC_bias = {vtg[icnp]:.3f} V "
          f"(edge med ~{np.median(r[:10]):.1f}/{np.median(r[-10:]):.1f} ohm)")
    ax[0].plot(vtg, r, label=nm)
ax[0].set_ylabel("Rxx (ohm)"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[0].set_title("Gate C scout — file_id 0, BG=Si=0, B=0")

rxy = R("sr3_X")
ax[1].plot(vtg, rxy, label="sr3 Rxy T5-B6", color="C2")
ax[1].axhline(0, color="k", lw=.5)
ax[1].set_ylabel("Rxy (ohm)"); ax[1].set_xlabel("DC_bias / TG (V)")
ax[1].legend(); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig("hera_scratch/gateC_scout.png", dpi=110)
print("saved hera_scratch/gateC_scout.png")
