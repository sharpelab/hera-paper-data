# Gate C consolidated figure: 4 legs, R per channel + gate currents vs swept V.
# Scratch prototype for the ana-notebook entry.
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

I_BIAS = 5e-9
LEGS = [int(a) for a in sys.argv[1:]] or [0, 1, 2, 3]

fig, axes = plt.subplots(2, len(LEGS), figsize=(4 * len(LEGS), 6), sharex="col")
for j, rid in enumerate(LEGS):
    run = open_run(f"data/{rid}")
    v = run.col_at(1)  # swept gate voltage (duplicated fp column)
    tag = "; ".join(run.tags) if hasattr(run, "tags") else ""
    axR, axI = axes[0, j], axes[1, j]
    for ch, lbl in [("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5"), ("sr3_X", "sr3 T5-B6 (xy)")]:
        axR.plot(v, run.col(ch) / I_BIAS, label=lbl, lw=0.8)
    axR.set_yscale("symlog", linthresh=10)
    axR.set_ylabel("R = X/I (Ω)")
    axR.set_title(f"run {rid}: {tag[:40]}", fontsize=8)
    axR.legend(fontsize=6)
    axI.plot(v, run.col("k_2400_tg_curr") * 1e12, label="I_tg (pA)", lw=0.8)
    axI.plot(v, run.col("k_2400_bg_curr") * 1e12, label="I_bg (pA)", lw=0.8)
    axI.set_ylabel("I_gate (pA)")
    axI.set_xlabel(run.cols[1])
    axI.legend(fontsize=6)
fig.suptitle("QC0426 gate C — gate-current-sanity-check legs (B=0, T≈1.17 K, 5 nA @ 13 Hz)")
fig.tight_layout()
fig.savefig("hera_scratch/gatec_legs.png", dpi=120)
print("saved hera_scratch/gatec_legs.png")
