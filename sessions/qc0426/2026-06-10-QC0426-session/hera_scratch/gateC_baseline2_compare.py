"""Gate C — compare run 1 (B=0 density cut, D=+0.25) against the reference pack.

Four checks per README: resistance scale, CNP position, shape, drain current.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

eps0 = 8.8541878128e-12
e = 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
c_bg = eps0 * 3 / 12e-9

# --- reference ---
ref = np.loadtxt(r"reference/baseline_B0_densitycut_Dp0p25.csv")
ref_vtg, ref_vbg, ref_n, ref_I, ref_R1, ref_R2 = ref.T

# --- session run 1 ---
run = open_run(r"data/1")
vtg = run.col("DC_bias")
vbg = run.col("k_bg_volt")
I = run.col("sr0_X") / (-1e6)
R1 = run.col("sr1_X") / I
R2 = run.col("sr2_X") / I
n = (c_tg * vtg + c_bg * vbg) / e * 1e-16  # -> 1e12 cm^-2

def cnp(nv, R):
    k = np.nanargmax(np.abs(R))
    return nv[k], abs(R[k])

for name, (nn, RR), (rn, rR) in [
    ("sr1", (n, R1), (ref_n, ref_R1)),
    ("sr2", (n, R2), (ref_n, ref_R2)),
]:
    n_new, r_new = cnp(nn, RR)
    n_ref, r_ref = cnp(rn, rR)
    print(f"{name}: CNP peak {r_new/1e3:.2f} kOhm at n={n_new:+.3f}e12  "
          f"(ref {r_ref/1e3:.2f} kOhm at n={n_ref:+.3f}e12)  "
          f"ratio {r_new/r_ref:.2f}, dn={n_new-n_ref:+.3f}e12")

print(f"drain |I|: session {np.abs(I).mean()*1e9:.3f} nA mean "
      f"(min {np.abs(I).min()*1e9:.3f}), ref {np.abs(ref_I).mean()*1e9:.3f} nA")

fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
for ax, RR, rR, name in [(axes[0], R1, ref_R1, "sr1 (09-01)"),
                         (axes[1], R2, ref_R2, "sr2 (12-20)")]:
    ax.semilogy(ref_n, np.abs(rR), "k-", lw=1, label="reference (06-09)")
    ax.semilogy(n, np.abs(RR), "r--", lw=1, label="run 1 (today)")
    ax.set_xlabel(r"n (10$^{12}$ cm$^{-2}$)")
    ax.set_ylabel(r"|R$_{xx}$| ($\Omega$)")
    ax.set_title(name)
    ax.legend(fontsize=8)
fig.suptitle("Gate C baseline 2 — B=0 density cut, D=+0.25 V/nm, Si=+50 V")
fig.tight_layout()
fig.savefig(r"hera_scratch/gateC_baseline2_compare.png", dpi=140)
print("saved hera_scratch/gateC_baseline2_compare.png")
