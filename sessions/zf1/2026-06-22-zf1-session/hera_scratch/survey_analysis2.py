import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import fan_grids, resistance_grids, GateCalibration

f = fan_grids("data/2"); rg = resistance_grids(f)
VT = f.grid("k_tg_volt"); VB = f.grid("k_bg_volt")
Rxx = np.abs(rg.R["sr830_3"]); tg = f.slow

# --- CNP from 4T, searched around recon prior, in-window rows only ---
pred = lambda vt: -0.850*vt + 0.133            # recon CNP line
cnp_bg = np.full(len(tg), np.nan)
for i in range(len(tg)):
    p = pred(tg[i])
    if not (-3.7 <= p <= 3.9):                  # CNP must be inside BG window w/ margin
        continue
    bg = VB[i]; sel = np.abs(bg - p) <= 1.3
    if sel.sum() < 5: continue
    prof = gaussian_filter1d(Rxx[i][sel], 1.0)
    cnp_bg[i] = bg[sel][int(np.argmax(prof))]
good = np.isfinite(cnp_bg)
slope, b0 = np.polyfit(tg[good], cnp_bg[good], 1)
resid = cnp_bg[good] - (slope*tg[good]+b0)
print(f"CNP fit (4T, {good.sum()} in-window rows): Vbg={slope:+.4f} Vtg{b0:+.4f}")
print(f"  resid rms={np.std(resid):.4f} V  max|resid|={np.abs(resid).max():.4f} V")
print(f"  dVbg/dVtg={slope:+.4f} -> c_bg/c_tg=-1/slope={-1/slope:.4f}  (prior 1.18, recon 1.176)")

# --- (n,D) + low-Rxx suppression hunt ---
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
N = cal.density(VT, VB)/1e15; D = cal.displacement_field(VT, VB)/1e9
# distance from CNP (in n) to mask out the insulating ridge
metal = np.abs(N) > 1.0                         # away from CNP
print(f"\nmetallic-region (|n|>1e11) Rxx: min={Rxx[metal].min():.1f}  p1={np.percentile(Rxx[metal],1):.1f}  median={np.median(Rxx[metal]):.1f} Ohm")
# any genuinely suppressed pocket (Rxx well below background) on hole side, D<0?
for thr in (10,8,6,5):
    sub = metal & (Rxx < thr) & (N < 0)
    if sub.sum():
        print(f"  hole-side Rxx<{thr}Ω: {sub.sum()} pts; (n,D) span n[{N[sub].min():+.1f},{N[sub].max():+.1f}] D[{D[sub].min():+.2f},{D[sub].max():+.2f}]")
    else:
        print(f"  hole-side Rxx<{thr}Ω: none")

# proximity-SC window stats
win = (D<=-0.35)&(D>=-0.65)&(N<=-3.0)&(N>=-8.0)
print(f"\nproximity-SC window Rxx: min={Rxx[win].min():.1f} med={np.median(Rxx[win]):.1f} max={Rxx[win].max():.1f} Ω  (metallic background ~{np.median(Rxx[metal]):.0f}Ω => {'NO suppression' if Rxx[win].min()>0.7*np.median(Rxx[metal]) else 'possible dip'})")

# === low-R focused maps (linear, clipped) ===
fig, axs = plt.subplots(1, 2, figsize=(15,6))
ax=axs[0]
pc=ax.pcolormesh(VT, VB, np.clip(Rxx,0,40), vmin=0, vmax=40, shading="nearest", cmap="inferno")
ax.plot(tg[good], cnp_bg[good], "c.", ms=3); ax.plot(tg, slope*tg+b0, "w-", lw=0.8)
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)"); ax.set_title("4T Rxx (linear 0–40 Ω) — suppression hunt"); fig.colorbar(pc,ax=ax)
ax=axs[1]
sc=ax.scatter(N.ravel(), D.ravel(), c=np.clip(Rxx.ravel(),0,40), vmin=0, vmax=40, s=10, cmap="inferno")
ax.axhline(-0.5,color="c",ls=":",lw=0.7); ax.axvline(-5,color="c",ls=":",lw=0.7)
ax.set_xlim(-15,5); ax.set_xlabel("n (1e11 cm⁻²)"); ax.set_ylabel("D (V/nm)")
ax.set_title("Rxx(n,D) linear 0–40 Ω (cyan: candidate target)"); fig.colorbar(sc,ax=ax)
fig.tight_layout(); fig.savefig("hera_scratch/survey_run2_lowR.png", dpi=120)
print("\nsaved hera_scratch/survey_run2_lowR.png")
