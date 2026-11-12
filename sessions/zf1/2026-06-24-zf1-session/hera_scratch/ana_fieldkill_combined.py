"""Field-kill combined: pass A (data/10, +50->0) + pass B (data/11, -50->0).
Rxx vs controller-B across both -> locate effective zero (dip minimum) + the kill."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run

def load(rid):
    g = open_run(f"data/{rid}")
    B = g.col_at(g.col_indices("magnet_field")[0]) * 1e3
    R = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100.0) / 1e-9
    T = g.col("T")
    return B, R, T, g.interrupted

bA, rA, tA, iA = load(10)
bB, rB, tB, iB = load(11)
print("pass A interrupted", iA, " T[%.4f,%.4f]" % (tA.min(), tA.max()))
print("pass B interrupted", iB, " T[%.4f,%.4f]" % (tB.min(), tB.max()))

B = np.concatenate([bB, bA]); R = np.concatenate([rB, rA])
o = np.argsort(B); B, R = B[o], R[o]
kmin = int(np.argmin(R))
print("MIN Rxx = %.2f ohm at controller B = %+.1f mT  (= effective zero / SC field max)" % (R[kmin], B[kmin]))
print("Rxx at controller 0: %.1f ohm; far-field ~%.1f ohm" %
      (R[np.argmin(np.abs(B))], np.median(R[np.abs(B) > 40])))

fig, ax = plt.subplots(figsize=(9,5))
ax.plot(bB, rB, ".-", ms=3, label="pass B (-50->0)")
ax.plot(bA, rA, ".-", ms=3, label="pass A (+50->0)")
ax.axvline(B[kmin], color="b", ls="--", lw=1, label=f"effective zero ~{B[kmin]:+.1f} mT")
ax.plot(B[kmin], R[kmin], "k*", ms=12)
ax.set_xlabel("controller B_perp (mT)"); ax.set_ylabel("4T Rxx (ohm)")
ax.set_title("Field-kill at n=-0.55, D=-0.6 (zero DC bias): dip at effective zero, killed by +/-B")
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.savefig("hera_scratch/fieldkill_combined.png", dpi=120)
print("saved")
