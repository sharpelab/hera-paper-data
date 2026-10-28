"""Gate C disk verification — runs 0-3 (gate-current-sanity-check legs)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

I_BIAS = 5e-9
LEGS = {0: "TG 0->+3 V", 1: "TG 0->-3 V", 2: "BG 0->+4.5 V", 3: "BG 0->-4.5 V"}

fig, axes = plt.subplots(2, 4, figsize=(18, 7), sharex="col")
ok = True
for i, (rid, label) in enumerate(LEGS.items()):
    run = open_run(f"data/{rid}")
    print(f"--- run {rid}: {label} ---")
    print(summarize_run(run))
    if run.interrupted:
        print(f"!! run {rid} interrupted"); ok = False
    cols = list(run.cols)
    if rid == 0 and i == 0:
        print("columns:", cols)
    xname = "k_2400_tg_volt" if rid < 2 else "k_2400_bg_volt"
    # swept column is the setpoint column; fp'd volt col also exists — use fp'd
    V = run.col(xname)
    itg, ibg = run.col("k_2400_tg_curr"), run.col("k_2400_bg_curr")
    for nm, arr in (("I_tg", itg), ("I_bg", ibg)):
        mx = np.abs(arr).max()
        if mx > 1e-9:
            print(f"!! {nm} exceeded 1 nA: {mx:.3e}"); ok = False
        elif mx > 2e-10:
            print(f"warn {nm} above 200 pA: {mx:.3e}")
        else:
            print(f"{nm} max |I| = {mx*1e12:.0f} pA")
    ax = axes[0, i]
    for ch, c in (("sr1", "C0"), ("sr2", "C1"), ("sr3", "C2")):
        x = run.col(f"{ch}_X")
        if np.allclose(x, x[0]):
            print(f"!! {ch}_X flat across leg"); ok = False
        if np.isnan(x).any():
            print(f"!! {ch}_X has NaNs"); ok = False
        ax.plot(V, np.abs(x) / I_BIAS, c, label=f"{ch} |R|", lw=0.8)
    i0 = run.col("sr0_X") / 1e6  # Ithaco |gain| division -> A
    if np.allclose(i0, i0[0]):
        print("!! sr0_X flat"); ok = False
    ax.set_yscale("log"); ax.set_title(f"run {rid}: {label}")
    ax.set_ylabel("R (Ohm)") if i == 0 else None
    ax.legend(fontsize=7)
    ax2 = axes[1, i]
    ax2.plot(V, itg * 1e12, "C3", label="I_tg (pA)", lw=0.8)
    ax2.plot(V, ibg * 1e12, "C4", label="I_bg (pA)", lw=0.8)
    ax2.plot(V, np.abs(i0) * 1e9, "C5", label="|I_drain| (nA)", lw=0.8)
    ax2.set_xlabel(xname); ax2.legend(fontsize=7)
    ax2.set_ylabel("I (pA) / I_d (nA)") if i == 0 else None

fig.suptitle("Gate C — gate-current-sanity-check, runs 0-3 (raw, gain-divided)")
fig.tight_layout()
fig.savefig("hera_scratch/gatec_runs0-3.png", dpi=110)
print("VERDICT:", "ALL LEGS CLEAN" if ok else "ISSUES FOUND (see above)")
