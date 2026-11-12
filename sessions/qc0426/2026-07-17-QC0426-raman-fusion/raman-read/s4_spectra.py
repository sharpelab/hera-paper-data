"""Population mean spectra, lineshape + M-band/G* cross-checks, decompose_mixed,
saturation screen, sub-region uniformity."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/.worktrees/raman_stacking_lit/hera/models/raman_stacking")
from raman_io import load_wip
from metrics import metrics_2d, fit_band, decompose_mixed, _lorentz

OUT = "/tmp/qc0426-raman-read"
ds = {d["caption"]: d for d in load_wip("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")}

d4 = ds["Scan LA--004--Spec.Data 1"]
wn, ii4 = d4["wn"], d4["ii"]
z4 = np.load(f"{OUT}/scan004_metrics.npz")
d2 = ds["Scan LA--002--Spec.Data 1"]
ii2 = d2["ii"]
z2 = np.load(f"{OUT}/scan002_metrics.npz")

lab4 = z4["labels"]; fw4 = z4["m_fwhm"]
main = lab4 == 1          # 521 px main population
low = lab4 == 0           # 22 px minority

# ---- saturation screen
for tag, ii, sel in [("scan004", ii4, np.isfinite(fw4)),
                     ("scan002", ii2, np.isfinite(z2["m_fwhm"]))]:
    sub = ii[:, sel]
    m = (wn > 1200)
    nsat = (sub[m] >= 65535).sum()
    print(f"{tag}: saturated samples above 1200 cm-1 in credible px: {nsat}")

# ---- r2 / skew / ratio stats for main population
for name, sel, z in [("scan004 main", main, z4), ("scan004 low", low, z4),
                     ("scan002 all-credible", np.isfinite(z2["m_fwhm"]), z2)]:
    r2 = z["m_r2"][sel]; sk = z["m_skew"][sel]; rt = z["m_ratio_lh"][sel]
    print(f"{name}: n={sel.sum()} r2 med {np.nanmedian(r2):.3f} "
          f"(5-95% {np.nanpercentile(r2,5):.3f}-{np.nanpercentile(r2,95):.3f})  "
          f"skew med {np.nanmedian(sk):+.3f}  ratio_lh med {np.nanmedian(rt):.3f}")

# ---- mean spectra
mean_main = ii4[:, main].mean(axis=1)
mean_low = ii4[:, low].mean(axis=1)
mean_002 = ii2[:, np.isfinite(z2["m_fwhm"])].mean(axis=1)
np.savez(f"{OUT}/mean_spectra.npz", wn=wn, mean_main=mean_main,
         mean_low=mean_low, mean_002=mean_002)

for name, sp in [("scan004 main mean", mean_main), ("scan004 low mean", mean_low),
                 ("scan002 mean", mean_002)]:
    m = metrics_2d(wn, sp)
    g = fit_band(wn, sp, (1500.0, 1650.0), fit_half=60.0)
    print(f"{name}: 2D " + (f"FWHM {m['fwhm']:.1f} center {m['center']:.1f} "
          f"r2 {m['r2']:.3f} skew {m['skew']:+.2f} ratio {m['ratio_lh']:.2f}" if m else "none")
          + (f" | G pos {g['center']:.1f} FWHM {g['fwhm']:.1f}" if g else " | no G"))

# ---- sub-region uniformity in scan004 (spatial blocks of the main population)
import itertools
X = np.asarray(np.load(f"{OUT}/scan004_grid.npz")["X"]) if False else None
# use position grid via witio-loaded ii ordering: index j -> a=j//51, b=j%51
import witio
p = witio.read("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")
gg = None
for it in p.data:
    if it.caption == "Scan LA--004--Spec.Data 1":
        g = it.position_grid
        gg = np.asarray(g() if callable(g) else g)
xs, ys = gg[0].ravel(), gg[1].ravel()
print("\nscan004 main-population FWHM by spatial block (3x3 blocks of the bbox):")
xe = np.linspace(xs[main].min(), xs[main].max(), 4)
ye = np.linspace(ys[main].min(), ys[main].max(), 4)
for iy in range(3):
    row = []
    for ix in range(3):
        sel = main & (xs >= xe[ix]) & (xs <= xe[ix+1]) & (ys >= ye[iy]) & (ys <= ye[iy+1])
        row.append(f"{np.nanmean(fw4[sel]):5.1f}±{np.nanstd(fw4[sel]):4.1f} (n={sel.sum():3d})"
                   if sel.sum() else "   --")
    print("  y[%5.1f,%5.1f]: " % (ye[iy], ye[iy+1]) + "  ".join(row))

# spine vs fingers: spine = -4.5 < y < 0 band along the channel
spine = main & (ys > -4.5) & (ys < 0.5)
arms_up = main & (ys >= 0.5)
arms_dn = main & (ys <= -4.5)
for nm, sel in [("spine", spine), ("upper arms", arms_up), ("lower arms", arms_dn)]:
    print(f"  {nm}: n={sel.sum()} FWHM {np.nanmean(fw4[sel]):.1f}±{np.nanstd(fw4[sel]):.1f} "
          f"2Dpos {np.nanmean(z4['m_center'][sel]):.1f}±{np.nanstd(z4['m_center'][sel]):.1f}")

# ---- decompose_mixed: intermediate/low pixels against main-mean and low-mean
res_alpha = []
inter = np.isfinite(fw4) & (fw4 < 61.5)   # below main population 5th pct
print(f"\ndecompose_mixed on {inter.sum()} scan004 px with FWHM<61.5 "
      f"(refs: main mean vs low-cluster mean):")
for j in np.where(inter)[0]:
    r = decompose_mixed(wn, ii4[:, j], mean_main, mean_low)
    if r:
        res_alpha.append((j, fw4[j], r["alpha"], r["r2"]))
for j, f, a, r2 in res_alpha:
    print(f"  px {j} (x={xs[j]:+.1f}, y={ys[j]:+.1f})  FWHM {f:.1f}  alpha(main) {a:.2f}  r2 {r2:.3f}")

# ---- figures: lineshape + windows
fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
ax = axs[0, 0]
m = metrics_2d(wn, mean_main)
w = (wn > 2550) & (wn < 2850)
ax.plot(wn[w], mean_main[w] - np.median(mean_main[(wn>2550)&(wn<2590)]), "k-", lw=1.2,
        label=f"scan004 main mean (FWHM {m['fwhm']:.1f}, r$^2$ {m['r2']:.3f})")
fitc = fit_band(wn, mean_main, (2550., 2850.))
ax.plot(wn[w], _lorentz(wn[w], fitc["amp"], fitc["center"], fitc["fwhm"], fitc["offset"])
        - np.median(mean_main[(wn>2550)&(wn<2590)]), "r--", lw=1,
        label="single Lorentzian fit")
ax.set_title("2D band, scan004 main population (532 nm)")
ax.set_xlabel("Raman shift (cm$^{-1}$)"); ax.legend(fontsize=8)

ax = axs[0, 1]
for sp, nm, c in [(mean_main, "scan004 main", "k"), (mean_low, "scan004 low-FWHM (edges)", "tab:blue"),
                  (mean_002, "scan002 (defocused) mean", "tab:green")]:
    mm = (wn > 2550) & (wn < 2850)
    y = sp[mm]
    b = np.median(y[:20]); pk = y.max() - b
    ax.plot(wn[mm], (y - b) / pk, c, lw=1, label=nm)
ax.set_title("2D band, normalized comparison")
ax.set_xlabel("Raman shift (cm$^{-1}$)"); ax.legend(fontsize=8)

ax = axs[1, 0]
mm = (wn > 1620) & (wn < 2200)
ax.plot(wn[mm], mean_main[mm], "k-", lw=1)
ax.set_title("M-band window, scan004 main mean (1690-2150; Cong Fig.2 @2.33 eV)")
ax.set_xlabel("Raman shift (cm$^{-1}$)")

ax = axs[1, 1]
mm = (wn > 2300) & (wn < 2550)
ax.plot(wn[mm], mean_main[mm], "k-", lw=1)
ax.set_title("G* window, scan004 main mean (2400-2450)")
ax.set_xlabel("Raman shift (cm$^{-1}$)")
fig.savefig(f"{OUT}/lineshape_panels.png", dpi=130)

# full-range mean spectrum
fig2, ax = plt.subplots(figsize=(13, 4), constrained_layout=True)
ax.plot(wn, mean_main, "k-", lw=0.8)
ax.set_yscale("log")
ax.set_xlabel("Raman shift (cm$^{-1}$)"); ax.set_title("scan004 main-population mean, full range (log)")
fig2.savefig(f"{OUT}/mean_full_range.png", dpi=130)
print("figures written")
