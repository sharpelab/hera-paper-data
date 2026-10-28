# Gate C analysis — gate-current-sanity-check runs 0-3
# Raw per-leg traces: lock-in X (raw volts, gain noted) + gate currents.
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = ["0", "1", "2", "3"]
LEG = {"0": "TG 0->+7 V", "1": "TG 0->-6 V", "2": "BG 0->+4.5 V", "3": "BG 0->-4.5 V"}

fig, axes = plt.subplots(3, 4, figsize=(16, 9), sharex="col")
for j, run in enumerate(RUNS):
    try:
        meta = json.load(open(f"data/{run}/metadata.json"))
        cols = meta.get("columns") or meta.get("column_names")
        d = np.loadtxt(f"data/{run}/data.tsv")
    except Exception as e:
        print(f"run {run}: {e}")
        continue
    c = {name: d[:, k] for k, name in enumerate(cols) if name != cols[1] or k == 1}
    v = d[:, 1]
    swept = cols[1]
    # row 0: lock-in X raw
    ax = axes[0, j]
    for sr, col in (("sr0", "sr0_X"), ("sr1", "sr1_X"), ("sr2", "sr2_X"), ("sr3", "sr3_X")):
        ax.plot(v, np.abs(d[:, cols.index(col)]), label=sr, lw=0.8)
    ax.set_yscale("log"); ax.set_title(f"run {run}: {LEG[run]}")
    if j == 0: ax.set_ylabel("|X| (V, raw)")
    ax.legend(fontsize=6)
    # row 1: swept gate current
    ax = axes[1, j]
    icol = "k_2400_tg_curr" if "tg" in swept else "k_2400_bg_curr"
    ax.plot(v, d[:, cols.index(icol)] * 1e12, lw=0.8, color="C3")
    ax.axhline(0, color="k", lw=0.3)
    if j == 0: ax.set_ylabel("swept-gate I (pA)")
    # row 2: parked gate current
    ax = axes[2, j]
    pcol = "k_2400_bg_curr" if "tg" in swept else "k_2400_tg_curr"
    ax.plot(v, d[:, cols.index(pcol)] * 1e12, lw=0.8, color="C4")
    if j == 0: ax.set_ylabel("parked-gate I (pA)")
    ax.set_xlabel(swept + " (V)")
plt.tight_layout()
plt.savefig("hera_scratch/gatec_overview.png", dpi=110)
print("saved hera_scratch/gatec_overview.png")
