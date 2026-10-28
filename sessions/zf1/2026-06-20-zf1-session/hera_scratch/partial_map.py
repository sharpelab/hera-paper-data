import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run

g = open_run("data/2")
mc = g.meta["measurement_config"]; Ibias = mc["bias_voltage_1"]/mc["bias_resistor"]
NF = 101  # TG fast points per row
nfull = (g.rows // NF)
N = nfull * NF
print(f"complete BG rows: {nfull} (of 61); using {N} pts")

vtg = g.col_at(g.col_indices("k_tg_volt")[-1])[:N].reshape(nfull, NF)
vbg = g.col_at(g.col_indices("k_bg_volt")[-1])[:N].reshape(nfull, NF)
R3 = ((g.col("sr830_3_X")/mc["sr3_gain"])/Ibias)[:N].reshape(nfull, NF)   # 4T Rxx
R2 = ((g.col("sr830_2_X")/mc["sr2_gain"])/Ibias)[:N].reshape(nfull, NF)   # 2T
tg_axis = vtg[0]                 # TG fast axis (same each row)
bg_axis = vbg[:, 0]             # BG slow axis
print(f"TG: {tg_axis.min():.2f}..{tg_axis.max():.2f}  BG: {bg_axis.min():.2f}..{bg_axis.max():.2f}")

# --- CNP ridge: per BG row, argmax of smoothed 4T Rxx along TG ---
tg_cnp = np.array([tg_axis[np.argmax(gaussian_filter1d(R3[i], 2))] for i in range(nfull)])
# fit over rows where the ridge is inside the TG window (not edge-clipped)
inside = (tg_cnp > tg_axis.min()+0.3) & (tg_cnp < tg_axis.max()-0.3)
slope, intercept = np.polyfit(bg_axis[inside], tg_cnp[inside], 1)
resid = np.std(tg_cnp[inside] - (slope*bg_axis[inside]+intercept))
print(f"\nCNP fit (4T): Vtg_cnp = {slope:.3f}*Vbg + {intercept:.3f}  ({inside.sum()}/{nfull} rows, resid {resid:.3f} V)")
print(f"  cap ratio c_bg/c_tg = -slope = {-slope:.3f}  (geometry prior 23.6/20 = {23.6/20:.3f})")
print(f"  CNP at Vbg=0: Vtg = {intercept:.3f} V")

# --- candidate scan: contiguous low-Rxx well below the metal floor ---
metal = np.median(R3[(np.abs(R3) < 60)])  # rough metal scale
print(f"\nmetal Rxx scale ~{metal:.1f} Ω; noise floor ~2.6 Ω (run1)")
for thr in (8, 5, 3):
    mask = R3 < thr
    print(f"  pts with 4T Rxx < {thr} Ω: {mask.sum()} ({100*mask.sum()/R3.size:.2f}%)")
# location of the lowest-Rxx contiguous-ish spots (exclude single-pixel noise via 2D smoothing)
from scipy.ndimage import uniform_filter
R3s = uniform_filter(R3, size=3)   # 3x3 smooth kills isolated noise dips
imin = np.unravel_index(np.argmin(R3s), R3s.shape)
print(f"  lowest 3x3-smoothed 4T Rxx = {R3s[imin]:.1f} Ω at (Vtg={vtg[imin]:.2f}, Vbg={vbg[imin]:.2f})")
print(f"  (compare metal ~{metal:.0f} Ω — a real SC candidate would sit well below this, contiguous)")

# --- render ---
fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle(f"Run 2 partial gatemap ({nfull}/61 BG rows, BG −4→+2) — B~0, 0.5 nA, 34 mK")
im0 = ax[0].pcolormesh(tg_axis, bg_axis, np.clip(R3, -5, 80), cmap="viridis", shading="nearest")
ax[0].plot(slope*bg_axis[inside]+intercept, bg_axis[inside], "r-", lw=1, label=f"CNP fit (slope {slope:.2f})")
ax[0].set(xlabel="k_tg (V)", ylabel="k_bg (V)", title="4T Rxx sr3 (Ω, clip 0–80)"); ax[0].legend(fontsize=8)
plt.colorbar(im0, ax=ax[0], label="Rxx (Ω)")
im1 = ax[1].pcolormesh(tg_axis, bg_axis, np.clip(R3, -3, 15), cmap="inferno", shading="nearest")
ax[1].set(xlabel="k_tg (V)", ylabel="k_bg (V)", title="4T Rxx zoomed (0–15 Ω) — candidate hunt")
plt.colorbar(im1, ax=ax[1], label="Rxx (Ω)")
plt.tight_layout(); plt.savefig("hera_scratch/partial_map.png", dpi=115)
print("\nsaved hera_scratch/partial_map.png")
