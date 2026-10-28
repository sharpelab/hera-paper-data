import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sweep import raster
from sharpelab_nb.gates import calculate_gate_voltages, calculate_n_D

DTG, DBG, EP = 23.6, 20.0, 3.0
def to_gates(n, D): return calculate_gate_voltages(n, D, dtg=DTG, dbg=DBG, ep=EP)
# verify round-trip at the dip
vt, vb = to_gates(-0.4654, -0.6501)
print(f"dip round-trip: Vtg={vt:.3f} Vbg={vb:.3f} (meas -5.445, 4.053)")

# (n,D) box around the dip (n in e12 cm^-2, D in V/nm)
N_LO, N_HI = -0.63, -0.28
D_LO, D_HI = -0.67, -0.50
NX, NY = 71, 35              # ~0.005 e12 x ~0.005 V/nm
verts = np.array([[N_LO, D_LO], [N_HI, D_LO], [N_HI, D_HI], [N_LO, D_HI], [N_LO, D_LO]])
ns, Ds = raster.rasterize(verts, NX, NY, 0)
vtg = np.array([to_gates(n, D)[0] for n, D in zip(ns, Ds)])
vbg = np.array([to_gates(n, D)[1] for n, D in zip(ns, Ds)])
print(f"rasterized points: {len(ns)}")

# sanitize against validators
TGL, TGH, BGL, BGH = -7.0, 6.0, -4.0, 4.2
ok = (vtg > TGL) & (vtg < TGH) & (vbg > BGL) & (vbg < BGH)
print(f"in-validator: {ok.sum()}/{len(ok)} ({100*ok.mean():.1f}%) ; clipped {100*(~ok).mean():.1f}%")
print(f"gate extent (in-range): Vtg {vtg[ok].min():.3f}..{vtg[ok].max():.3f} ; Vbg {vbg[ok].min():.3f}..{vbg[ok].max():.3f}")
print(f"est time @1.3 s/pt: {len(ns[ok])*1.3/60:.0f} min")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].scatter(vtg[ok], vbg[ok], s=6, c="C0", label="in-range")
ax[0].scatter(vtg[~ok], vbg[~ok], s=6, c="C3", label="clipped (Vbg>4.2)")
ax[0].axhline(4.2, color="k", ls=":"); ax[0].set(xlabel="Vtg", ylabel="Vbg", title="rasterized box -> gates")
ax[0].legend(fontsize=8)
ax[1].scatter(ns[ok], Ds[ok], s=6, c="C0"); ax[1].scatter(ns[~ok], Ds[~ok], s=6, c="C3")
ax[1].plot(-0.4654, -0.6501, "y*", ms=16, label="dip"); ax[1].legend(fontsize=8)
ax[1].set(xlabel="n (e12 cm^-2)", ylabel="D (V/nm)", title="(n,D) coverage")
plt.tight_layout(); plt.savefig("hera_scratch/nd_design.png", dpi=110); print("saved nd_design.png")
