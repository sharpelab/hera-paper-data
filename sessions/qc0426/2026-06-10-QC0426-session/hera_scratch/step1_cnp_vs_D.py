"""Step 1 — Rxx(CNP) vs D at B=0, run 2. Per-channel, log scale."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

eps0 = 8.8541878128e-12
e = 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
c_bg = eps0 * 3 / 12e-9

run = open_run(r"data/2")
vtg = run.col("DC_bias")
vbg = run.col("k_bg_volt")
I = run.col("sr0_X") / (-1e6)
n = (c_tg * vtg + c_bg * vbg) / e * 1e-16
D = 0.5 * (c_tg * vtg - c_bg * vbg) / eps0 * 1e-9  # V/nm

chans = {"sr1 (09-01)": run.col("sr1_X") / I,
         "sr2 (12-20)": run.col("sr2_X") / I,
         "sr3 (09-12)": run.col("sr3_X") / I}

print(f"D range: {D.min():+.3f} .. {D.max():+.3f} V/nm; |n| max {np.abs(n).max():.3f}e12")
print(f"drain |I|: {np.abs(I).min()*1e9:.3f} - {np.abs(I).max()*1e9:.3f} nA")
for name, R in chans.items():
    aR = np.abs(R)
    # dynamic range over D, and value near D = 0 vs extremes
    i0 = np.argmin(np.abs(D))
    print(f"{name}: R(D~0) = {aR[i0]/1e3:.2f} k, max {aR.max()/1e3:.2f} k at D={D[np.argmax(aR)]:+.2f}, "
          f"min {aR.min()/1e3:.3f} k at D={D[np.argmin(aR)]:+.2f}, "
          f"ratio max/min = {aR.max()/aR.min():.1f}")

fig, ax = plt.subplots(figsize=(7, 4.5))
for name, R in chans.items():
    ax.semilogy(D, np.abs(R), lw=1.2, label=name)
ax.set_xlabel("D (V/nm)")
ax.set_ylabel(r"|R| ($\Omega$)")
ax.set_title("Run 2 — Rxx along CNP line vs D, B=0, Si=+50 V, T~1.16 K")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(r"hera_scratch/step1_cnp_vs_D.png", dpi=140)
print("saved hera_scratch/step1_cnp_vs_D.png")
