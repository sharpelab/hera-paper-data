"""Gate C liveness analysis — runs 0-3 (gate-current-sanity-check)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

I_BIAS = 5e-9
SR0_GAIN = -1e6
LEGS = [("data/0", "TG 0->+3 V"), ("data/1", "TG 0->-3 V"),
        ("data/2", "BG 0->+4.5 V"), ("data/3", "BG 0->-4.5 V")]

fig, axes = plt.subplots(3, 4, figsize=(16, 9), sharex="col")
for j, (d, title) in enumerate(LEGS):
    run = open_run(d)
    swept = "k_2400_tg_volt" if "TG" in title else "k_2400_bg_volt"
    v = run.col_at(run.col_indices(swept)[0])  # setpoint column
    itg = run.col_at(run.col_indices("k_2400_tg_curr")[-1])
    ibg = run.col_at(run.col_indices("k_2400_bg_curr")[-1])
    sr0x = run.col_at(run.col_indices("sr0_X")[-1])
    i_drain = sr0x / SR0_GAIN

    # row 0: raw drain current
    ax = axes[0, j]
    ax.plot(v, i_drain * 1e9, lw=0.8, color="k")
    ax.set_title(title)
    ax.set_ylabel("I_drain (nA)" if j == 0 else "")
    ax.set_ylim(0, 6)

    # row 1: 4T resistances
    ax = axes[1, j]
    for ch, lbl in (("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5"), ("sr3_X", "sr3 T5-B6 (xy)")):
        x = run.col_at(run.col_indices(ch)[-1])
        ax.plot(v, x / I_BIAS, lw=0.8, label=lbl)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylabel("R = X/I (Ohm)" if j == 0 else "")
    if j == 0:
        ax.legend(fontsize=7)

    # row 2: gate currents
    ax = axes[2, j]
    ax.plot(v, itg * 1e12, lw=0.8, label="I_tg")
    ax.plot(v, ibg * 1e12, lw=0.8, label="I_bg")
    ax.set_ylabel("I_gate (pA)" if j == 0 else "")
    ax.set_xlabel("swept gate (V)")
    ax.set_ylim(-150, 150)
    if j == 0:
        ax.legend(fontsize=7)

    print(f"{d} {title}: I_drain {i_drain.min()*1e9:.2f}-{i_drain.max()*1e9:.2f} nA, "
          f"|I_tg|max {np.abs(itg).max()*1e12:.0f} pA, |I_bg|max {np.abs(ibg).max()*1e12:.0f} pA, "
          f"interrupted={run.interrupted}")

fig.suptitle("Gate C liveness — gate-current-sanity-check, runs 0-3 (B=0, T=1.15 K, I_bias=5 nA)")
fig.tight_layout()
fig.savefig("hera_scratch/gatec_liveness.png", dpi=110)
print("saved hera_scratch/gatec_liveness.png")
