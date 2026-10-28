# Gate C — liveness analysis (gate-current-sanity-check, runs 0-3)
# Raw first: per leg, gate currents vs swept V; then 4T resistances vs swept V.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from hera.analysis import open_run

LEGS = [
    (0, "TG 0→+3 V", "k_2400_tg_volt"),
    (1, "TG 0→−3 V", "k_2400_tg_volt"),
    (2, "BG 0→+4.5 V", "k_2400_bg_volt"),
    (3, "BG 0→−4.5 V", "k_2400_bg_volt"),
]
I_BIAS = 1e-9  # 0.1 V / 100 MOhm liveness drive

# --- raw: gate currents
fig, axes = plt.subplots(2, 4, figsize=(16, 6), sharey="row")
for j, (fid, label, sweptcol) in enumerate(LEGS):
    r = open_run(f"data/{fid}")
    v = r.col(sweptcol)
    axes[0, j].plot(v, r.col("k_2400_tg_curr") * 1e12, lw=0.8, label="I_tg")
    axes[0, j].plot(v, r.col("k_2400_bg_curr") * 1e12, lw=0.8, label="I_bg")
    axes[0, j].set_title(f"run {fid}: {label}")
    axes[0, j].set_xlabel(f"{sweptcol} (V)")
    axes[0, j].set_ylabel("I_gate (pA)")
    axes[0, j].legend(fontsize=7)
    # raw: 4T resistances (X / I_bias, gains 1) + drain current
    for ch, nm in ((r.col("sr1_X"), "sr1 T3-T4"), (r.col("sr2_X"), "sr2 B4-B5"),
                   (r.col("sr3_X"), "sr3 T5-B6 (xy)")):
        axes[1, j].plot(v, ch / I_BIAS, lw=0.8, label=nm)
    ax2 = axes[1, j].twinx()
    ax2.plot(v, np.abs(r.col("sr0_X") / -1e6) * 1e9, "k--", lw=0.6, alpha=0.5)
    ax2.set_ylabel("|I_drain| (nA)", fontsize=7)
    axes[1, j].set_xlabel(f"{sweptcol} (V)")
    axes[1, j].set_ylabel("R = X/I_bias (Ohm)")
    axes[1, j].set_yscale("symlog", linthresh=10)
    axes[1, j].legend(fontsize=7)
fig.suptitle("Gate C liveness (gate-current-sanity-check): runs 0-3, drive ~1 nA @ 13 Hz, B=0, T=1.17 K")
fig.tight_layout()
fig.savefig("hera_scratch/gatec_liveness.png", dpi=110)
print("saved hera_scratch/gatec_liveness.png")

# --- numbers for the verdict
for fid, label, sweptcol in LEGS:
    r = open_run(f"data/{fid}")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    i0 = np.abs(r.col("sr0_X") / -1e6)
    print(f"run {fid} {label}: |Itg|max={np.abs(itg).max():.2e} A, "
          f"|Ibg|max={np.abs(ibg).max():.2e} A, "
          f"I_drain med={np.median(i0)*1e12:.0f} pA, "
          f"R_sr1 end={r.col('sr1_X')[-1]/I_BIAS:.1f} Ohm, "
          f"interrupted={r.interrupted}")
