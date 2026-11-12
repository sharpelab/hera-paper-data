# Gate C raw traces — runs 0-3, re-formed from TSV (plot.png is the monitor, not the measurement)
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run

I_BIAS = 5e-9
SR0_GAIN = -1e6
LEGS = {0: "TG 0→+3 V", 1: "TG 0→−3 V", 2: "BG 0→+4.5 V", 3: "BG 0→−4.5 V"}

fig, axes = plt.subplots(2, 4, figsize=(16, 6.5))
for i, (rid, label) in enumerate(LEGS.items()):
    run = open_run(f"data/{rid}")
    xname = "k_2400_tg_volt" if rid < 2 else "k_2400_bg_volt"
    V = run.col(xname)
    ax = axes[0, i]
    for ch in ("sr1", "sr2", "sr3"):
        ax.plot(V, np.abs(run.col(f"{ch}_X")) / I_BIAS, lw=0.8, label=f"|{ch}| R")
    ax.set_yscale("log")
    ax.set_title(f"run {rid}: {label}", fontsize=9)
    ax.legend(fontsize=7)
    if i == 0:
        ax.set_ylabel("|R| (Ohm)")
    ax2 = axes[1, i]
    ax2.plot(V, run.col("k_2400_tg_curr") * 1e12, lw=0.8, label="I_tg (pA)")
    ax2.plot(V, run.col("k_2400_bg_curr") * 1e12, lw=0.8, label="I_bg (pA)")
    ax2.plot(V, np.abs(run.col("sr0_X") / SR0_GAIN) * 1e12 / 1e3, lw=0.8, label="I_drain (nA)")
    ax2.set_xlabel(xname)
    ax2.legend(fontsize=7)
    if i == 0:
        ax2.set_ylabel("I_gate (pA) / I_drain (nA)")
    # numeric summary per leg
    print(f"run {rid} ({label}): rows {len(V)}/251, "
          f"max|I_tg| {np.abs(run.col('k_2400_tg_curr')).max()*1e12:.0f} pA, "
          f"max|I_bg| {np.abs(run.col('k_2400_bg_curr')).max()*1e12:.0f} pA, "
          f"I_drain {np.abs(run.col('sr0_X')/SR0_GAIN).mean()*1e9:.2f} nA, "
          f"sr1 R [{np.abs(run.col('sr1_X')).min()/I_BIAS:.0f}, {np.abs(run.col('sr1_X')).max()/I_BIAS:.0f}] Ohm")
fig.suptitle("Gate C: gate-current-sanity-check, runs 0-3 (raw, TSV re-formed)")
fig.tight_layout()
plt.show()
