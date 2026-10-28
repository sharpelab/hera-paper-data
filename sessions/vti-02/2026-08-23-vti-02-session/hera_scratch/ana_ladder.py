"""Arrhenius analysis of the cnp-t-ladder runs.
usage: menv python hera_scratch/ana_ladder.py <first_run_id> [last_run_id]
Each run: 5 TG windows at fixed V_bg; peak R per window; fit ln R vs 1/T on the high-T branch.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from hera.analysis import open_run

first = int(sys.argv[1]); last = int(sys.argv[2]) if len(sys.argv) > 2 else first + 10
D_LABELS = {0.40: "-0.11", 0.00: "0", -0.45: "+0.10", -0.80: "+0.19", -1.15: "+0.28"}
data = {}   # vb -> list of (T, Rpk)
for rid in range(first, last + 1):
    try:
        r = open_run(f"data/{rid}")
    except Exception:
        continue
    if r.recipe != "cnp-t-ladder":
        continue
    mc = r.meta["measurement_config"]
    vb = r.col("k_2400_bg_volt"); vt = r.col("k_2400_tg_volt")
    I = r.col("sr0_X") / mc["sr0_gain"]; R = np.abs(r.col("sr1_X") / I); T = r.col("T_sample")
    Tm = np.median(T)
    for v in np.unique(np.round(vb, 3)):
        m = np.isclose(np.round(vb, 3), v)
        data.setdefault(float(v), []).append((Tm, float(np.max(R[m])), rid))
    print(f"run {rid}: T_med {Tm:.2f} K (spread {T.max()-T.min():.2f}), windows {len(np.unique(np.round(vb,3)))}")
fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
print("\nD-D0    T(K) -> R_pk(Ohm)")
for v in sorted(data):
    arr = np.array(sorted(data[v]))
    lab = D_LABELS.get(round(v, 2), f"vb={v:+.2f}")
    ax[0].semilogy(arr[:, 0], arr[:, 1], "o-", label=f"D−D0={lab}")
    ax[1].semilogy(1.0 / arr[:, 0], arr[:, 1], "o-", label=f"D−D0={lab}")
    hi = arr[arr[:, 0] >= 8]
    line = f"  {lab:>6}: " + "  ".join(f"{t:.1f}K:{rr:.0f}" for t, rr, _ in arr)
    print(line)
    if len(hi) >= 3:
        p = np.polyfit(1.0 / hi[:, 0], np.log(hi[:, 1]), 1)
        print(f"        high-T (>=8 K) Arrhenius slope: Delta = {p[0] * cst.k / cst.e * 1e3 * 2:.1f} meV (2*slope, gap) ; R(inf)={np.exp(p[1]):.0f}")
ax[0].set_xlabel("T (K)"); ax[0].set_ylabel("R_CNP (Ω)"); ax[0].legend(fontsize=8)
ax[1].set_xlabel("1/T (1/K)"); ax[1].legend(fontsize=8); ax[1].set_title("Arrhenius")
fig.tight_layout(); fig.savefig("hera_scratch/ladder_arrhenius.png", dpi=110); print("saved hera_scratch/ladder_arrhenius.png")
