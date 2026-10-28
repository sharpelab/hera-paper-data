"""Step-3 field-kill: Rxx(B) at candidate. Did B_perp quench the dip?"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
g = open_run("data/10"); print(summarize_run(g)); print("interrupted", g.interrupted)
B = g.col_at(g.col_indices("magnet_field")[0]) * 1e3        # mT
R4 = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100.0) / 1e-9   # 4T Rxx [ohm]
T = g.col("T")
itg = np.abs(g.col("k_tg_curr"))
o = np.argsort(B)
Bs, Rs = B[o], R4[o]
r0 = Rs[np.argmin(np.abs(Bs))]                  # Rxx near B=0
rN = np.median(Rs[Bs > 0.8*Bs.max()])           # normal state at high B
thr = r0 + 0.5*(rN - r0)
bc = Bs[np.argmax(Rs > thr)] if (Rs > thr).any() else np.nan
print("Rxx(B~0)=%.2f ohm  normal(highB)=%.1f ohm  half-recovery B_c~%.1f mT" % (r0, rN, bc))
print("T over sweep: min %.4f max %.4f K (base ~0.034)" % (T.min(), T.max()))
print("leakage |I_tg|max[pA]=%.0f" % (itg.max()*1e12))
fig, ax = plt.subplots(figsize=(8,5))
ax.plot(Bs, Rs, ".-", ms=4)
ax.axhline(r0, color="g", ls=":", lw=1, label=f"Rxx(0)~{r0:.1f}")
ax.axhline(rN, color="r", ls=":", lw=1, label=f"normal~{rN:.0f}")
if np.isfinite(bc): ax.axvline(bc, color="b", ls="--", lw=1, label=f"B_c~{bc:.1f} mT")
ax.set_xlabel("B_perp (mT)"); ax.set_ylabel("4T Rxx (ohm)")
ax.set_title("data/10: field-kill at n=-0.55, D=-0.6 (zero DC bias)")
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.savefig("hera_scratch/fieldkill_step3.png", dpi=120)
print("saved")
