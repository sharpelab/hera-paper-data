import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, summarize_run, fan_grids, resistance_grids, GateCalibration

run = open_run("data/2"); print(summarize_run(run)); print("interrupted:", run.interrupted)
f = fan_grids("data/2"); rg = resistance_grids(f)

VT = f.grid("k_tg_volt")           # (105,83)
VB = f.grid("k_bg_volt")
Rxx = np.abs(rg.R["sr830_3"])      # 4T longitudinal (30-31)
R2t = np.abs(rg.R["sr830_2"])      # 2T (5-4)
Icur = rg.current

# --- leakage (gatemap Verify) ---
ci = {c:i for i,c in enumerate(f.cols)}
itg = f.data[:, ci["k_tg_curr"]]; ibg = f.data[:, ci["k_bg_curr"]]
print(f"\nleakage: |I_tg|max={np.abs(itg).max():.2e} A  |I_bg|max={np.abs(ibg).max():.2e} A  (ceiling 1 nA)")
print(f"current: med={np.median(Icur)*1e9:.3f} nA  min={Icur.min()*1e9:.3f} nA (current-bias holds if min~1nA)")
print(f"Rxx(4T): min={Rxx.min():.1f}  median={np.median(Rxx):.1f}  max={Rxx.max()/1e3:.1f}k Ohm")

# --- cap-ratio refinement: CNP ridge per TG row from 2T (clear, large peak) ---
tg = f.slow                         # (105,)
bg1d = VB[0]                        # fast axis values (assume same per row)
cnp_bg = np.full(len(tg), np.nan); edge = np.zeros(len(tg), bool)
for i in range(len(tg)):
    prof = gaussian_filter1d(R2t[i], 1.5)
    k = int(np.argmax(prof)); cnp_bg[i] = VB[i, k]
    if k <= 1 or k >= R2t.shape[1]-2: edge[i] = True
good = ~edge & np.isfinite(cnp_bg)
slope, b0 = np.polyfit(tg[good], cnp_bg[good], 1)
resid = cnp_bg[good] - (slope*tg[good]+b0)
cbg_ctg = -1.0/slope
print(f"\nCNP fit (n={good.sum()}/{len(tg)} rows, {edge.sum()} edge-excluded):")
print(f"  Vbg = {slope:+.4f} Vtg {b0:+.4f}   resid rms={np.std(resid):.4f} V  max|resid|={np.abs(resid).max():.4f} V")
print(f"  c_bg/c_tg = -1/slope = {cbg_ctg:.4f}   (prior 1.18; recon preview 1.176)")

# --- (n,D) reprojection ---
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
N = cal.density(VT, VB)/1e15        # 1e11 cm^-2
D = cal.displacement_field(VT, VB)/1e9   # V/nm

# --- candidate hunt: hole side, D<0, near the proximity-SC window ---
win = (D <= -0.35) & (D >= -0.65) & (N <= -3.0) & (N >= -8.0)
print(f"\ncandidate window (D in[-0.65,-0.35], n in[-8,-3]e11): {win.sum()} grid pts")
if win.sum():
    rw = Rxx[win]
    print(f"  Rxx in window: min={rw.min():.1f}  med={np.median(rw):.1f}  max={rw.max():.1f} Ohm")
    # location of the window minimum
    idx = np.where(win); j = np.argmin(Rxx[win])
    iy, ix = idx[0][j], idx[1][j]
    print(f"  window Rxx min at Vtg={VT[iy,ix]:+.2f} Vbg={VB[iy,ix]:+.2f} -> n={N[iy,ix]:+.2f}e11 D={D[iy,ix]:+.3f}: Rxx={Rxx[iy,ix]:.1f} Ohm")
# global low-Rxx (below metallic background) hunt on hole side
holes = (N < -1.0) & (Rxx < 8.0)
print(f"  hole-side pts with Rxx<8 Ohm (sub-metallic): {holes.sum()}")
if holes.sum():
    print(f"    their (n,D) span: n[{N[holes].min():+.1f},{N[holes].max():+.1f}]  D[{D[holes].min():+.2f},{D[holes].max():+.2f}]")

# === plots ===
fig, axs = plt.subplots(2, 2, figsize=(14,10))
# (a) raw Rxx vs gates, log
ax=axs[0,0]
pc=ax.pcolormesh(VT, VB, np.clip(Rxx,1,None), norm=LogNorm(1,5e3), shading="nearest", cmap="viridis")
ax.plot(tg[good], cnp_bg[good], "r.", ms=2, label="CNP (2T)")
ax.plot(tg, slope*tg+b0, "w-", lw=0.8)
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)"); ax.set_title("Run 2: 4T Rxx(V_tg,V_bg) [Ω, log]"); ax.legend(loc="upper right")
fig.colorbar(pc, ax=ax)
# (b) (n,D) map
ax=axs[0,1]
pc=ax.pcolormesh(N, D, np.clip(Rxx,1,None), norm=LogNorm(1,5e3), shading="nearest", cmap="viridis")
ax.axhline(-0.5, color="w", ls=":", lw=0.7); ax.axvline(-5, color="w", ls=":", lw=0.7)
ax.set_xlabel("n (1e11 cm⁻²)"); ax.set_ylabel("D (V/nm)"); ax.set_title("4T Rxx(n,D) [Ω, log]  (white: candidate target)")
fig.colorbar(pc, ax=ax)
# (c) CNP fit
ax=axs[1,0]
ax.plot(tg[good], cnp_bg[good], "o", ms=3); ax.plot(tg, slope*tg+b0, "-", label=f"c_bg/c_tg={cbg_ctg:.3f}")
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg at CNP"); ax.set_title(f"CNP line ({good.sum()} rows, rms {np.std(resid):.3f} V)"); ax.legend()
# (d) candidate-region zoom (n,D)
ax=axs[1,1]
m = (D<=-0.2)&(D>=-0.78)&(N<=0)&(N>=-12)
sc=ax.scatter(N[m], D[m], c=np.clip(Rxx[m],1,500), norm=LogNorm(1,500), s=14, cmap="viridis")
ax.set_xlabel("n (1e11 cm⁻²)"); ax.set_ylabel("D (V/nm)"); ax.set_title("Hole-side D<0 zoom — Rxx [Ω, log]")
fig.colorbar(sc, ax=ax)
fig.tight_layout(); fig.savefig("hera_scratch/survey_run2.png", dpi=110)
print("\nsaved hera_scratch/survey_run2.png")
