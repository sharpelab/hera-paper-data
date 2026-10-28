"""Gate C read: four gate-current-sanity-check legs (runs 0-3). Raw R = (sr1_X/gain)/I_drain per point."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels

runs = [open_run(f"data/{i}") for i in range(4)]
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for r in runs:
    print(summarize_run(r)); print("tags:", r.tags, "| interrupted:", r.interrupted)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    V = r.col(r.swept_axis)
    I = r.col("sr0_X") / ch["sr0"].gain          # drain current, A (gain-divided)
    R = (r.col("sr1_X") / ch["sr1"].gain) / I     # Rxx B_1-B_2, Ohm
    i_tg, i_bg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    T = r.col("T_sample")
    gate = r.swept_axis.replace("_volt", "")
    k = np.argmax(np.abs(R))
    print(f"  {gate}: V {V[0]:+.2f}->{V[-1]:+.2f} V | R {np.abs(R).min():.0f}-{np.abs(R).max():.0f} Ohm, "
          f"max at V={V[k]:+.3f} | I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA | "
          f"I_tg {i_tg.min()*1e12:+.0f}..{i_tg.max()*1e12:+.0f} pA, I_bg {i_bg.min()*1e12:+.0f}..{i_bg.max()*1e12:+.0f} pA | "
          f"T {T.min():.3f}-{T.max():.3f} K")
    a = ax[0, 0] if "tg" in gate else ax[0, 1]
    a.plot(V, np.abs(R), ".-", ms=3, label=f"run {r.path.name}")
    a.set_xlabel(gate + " (V)"); a.set_ylabel("|Rxx| B_1-B_2 (Ohm)"); a.legend()
    b = ax[1, 0] if "tg" in gate else ax[1, 1]
    b.plot(V, i_tg * 1e12, ".-", ms=3, label=f"I_tg run {r.path.name}")
    b.plot(V, i_bg * 1e12, ".-", ms=3, label=f"I_bg run {r.path.name}")
    b.set_xlabel(gate + " (V)"); b.set_ylabel("gate current (pA)"); b.legend(fontsize=7)
fig.suptitle("vti-02 gate C: gate-current-sanity-check, runs 0-3 (B=0, Vsi=0, other gate 0)")
fig.tight_layout(); fig.savefig("hera_scratch/gatec_legs.png", dpi=110)
print("saved hera_scratch/gatec_legs.png")
