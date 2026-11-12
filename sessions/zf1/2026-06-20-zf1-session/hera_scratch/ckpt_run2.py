import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

g = open_run("data/2")
print(summarize_run(g))
print("interrupted:", g.interrupted)
mc = g.meta["measurement_config"]; Ibias = mc["bias_voltage_1"]/mc["bias_resistor"]

vtg = g.col_at(g.col_indices("k_tg_volt")[-1])
vbg = g.col_at(g.col_indices("k_bg_volt")[-1])
n = len(vtg); print(f"landed points: {n}  (~{n/101:.1f} BG rows of 61)")

itg = np.abs(g.col("k_tg_curr")); ibg = np.abs(g.col("k_bg_curr"))
R3 = (g.col("sr830_3_X")/mc["sr3_gain"])/Ibias   # 4T Rxx
R2 = (g.col("sr830_2_X")/mc["sr2_gain"])/Ibias

# --- SAFETY: leakage, esp at the +6 / -7 TG corners (first time at +6) ---
print("\n=== leakage ===")
print(f"  |I_tg| max {itg.max()*1e12:.0f} pA @ (tg={vtg[itg.argmax()]:+.2f}, bg={vbg[itg.argmax()]:+.2f})")
print(f"  |I_bg| max {ibg.max()*1e12:.0f} pA @ (tg={vtg[ibg.argmax()]:+.2f}, bg={vbg[ibg.argmax()]:+.2f})")
hi = vtg > 5.5
print(f"  near +6 V TG (tg>5.5, {hi.sum()} pts): |I_tg| max {itg[hi].max()*1e12:.0f} pA")
lo = vtg < -6.5
print(f"  near -7 V TG (tg<-6.5, {lo.sum()} pts): |I_tg| max {itg[lo].max()*1e12:.0f} pA")

# --- channel health ---
print("\n=== health ===")
i1 = g.col("sr830_1_X")/mc["sr1_gain"]
print(f"  current sr1 med {np.median(i1)*1e12:.0f} pA (I_bias {Ibias*1e12:.0f})")
print(f"  4T Rxx: med {np.median(R3):.1f} Ω  min {R3.min():.1f}  max {R3.max():.1f}")
print(f"  any sub-metal low-Rxx? pts with R3<5 Ω: {(R3<5).sum()}  ; R3<0: {(R3<0).sum()} (X~0 noise)")

# --- re-form partial map (scatter of landed pts) ---
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle(f"Run 2 partial gatemap ({n} pts, ~{n/101:.0f}/61 BG rows) — 4T Rxx & leakage — B~0, 0.5 nA")
sc0 = ax[0].scatter(vtg, vbg, c=np.clip(R3, -10, 120), s=8, cmap="viridis")
ax[0].set(xlabel="k_tg (V)", ylabel="k_bg (V)", title="4T Rxx sr3 (Ω, clipped 0–120)")
plt.colorbar(sc0, ax=ax[0])
sc1 = ax[1].scatter(vtg, vbg, c=itg*1e12, s=8, cmap="inferno", vmax=120)
ax[1].set(xlabel="k_tg (V)", ylabel="k_bg (V)", title="|I_tg| leakage (pA)")
plt.colorbar(sc1, ax=ax[1])
plt.tight_layout()
plt.savefig("hera_scratch/ckpt_run2.png", dpi=110)
print("\nsaved hera_scratch/ckpt_run2.png")
