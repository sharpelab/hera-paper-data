#!/usr/bin/env python3
"""Step 3/4 refined — quality gating, thickness zoning (Si-520 + G
integral), re-split on trilayer-consistent pixels only, wall-sharpness
profile, strain screen on clean pixels, M-band / G* / ULF secondaries."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "tools"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from raman_io import load_wip
from map_tools import two_population_split, to_image, cluster_mean_spectrum
from metrics import metrics_2d

z = np.load(HERE / "map_metrics.npz")
dsets = load_wip(HERE / "inputs" / "vti-01.wip")
maps = {d["caption"]: d for d in dsets}
A = maps["73474_--Scan LA--003--Spec.Data 1"]
wn, ii = A["wn"], A["ii"]
cxA, cyA, nxA, nyA, stepA = z["A_geom"]
nxA, nyA = int(nxA), int(nyA)

fw = z["A_px_fwhm"]; cen = z["A_px_center"]; amp = z["A_px_amp"]
r2 = z["A_px_r2"]; si = z["A_si_amp"]; gfw = z["A_g_fwhm"]; gc = z["A_g_center"]


def g_integral(wn, ii):
    mL = (wn >= 1520) & (wn <= 1550); mR = (wn >= 1620) & (wn <= 1650)
    mG = (wn >= 1565) & (wn <= 1605)
    base = 0.5 * (ii[mL].mean(0) + ii[mR].mean(0))
    return np.clip(ii[mG] - base, 0, None).sum(0)


gint = g_integral(wn, ii)
ok = np.isfinite(fw)

# --- quality gate + interior erosion (kill boundary-straddling pixels) ---
img_ok = to_image(ok, nxA, nyA)
interior = ndimage.binary_erosion(img_ok, iterations=1).ravel()
q = ok & interior & (amp > 100) & (r2 > 0.9) & np.isfinite(si)
print(f"quality+interior pixels: {q.sum()} / {ok.sum()}")

# --- thickness zoning ---
# Si-amp histogram on quality px
h, edges = np.histogram(si[q], bins=40)
print("Si-amp histogram (quality px):")
for c, e in zip(h, edges):
    if c:
        print(f"  {e:6.0f}: {'#' * (c // 5)}{c}")
body_si = np.nanmedian(si[q])
thin = q & (si > body_si * 1.08)            # less attenuation -> thinner
thick = q & (si < body_si * 0.93)           # fold triangle / thicker
tri = q & ~thin & ~thick                    # trilayer-consistent
print(f"body Si median {body_si:.0f}; thin {thin.sum()} px, "
      f"thick {thick.sum()} px, trilayer-band {tri.sum()} px")
for name, m in (("thin", thin), ("thick", thick), ("tri", tri)):
    if m.sum():
        print(f"  {name}: FWHM {np.nanmean(fw[m]):.1f}±{np.nanstd(fw[m]):.1f} "
              f"Si {np.nanmean(si[m]):.0f} Gint {np.nanmean(gint[m]):.0f} "
              f"2Damp {np.nanmean(amp[m]):.0f} 2Dcen {np.nanmean(cen[m]):.1f}")

# --- split on trilayer-consistent pixels only ---
fw_tri = np.where(tri, fw, np.nan)
lab, cent = two_population_split(fw_tri)
n0, n1 = (lab == 0).sum(), (lab == 1).sum()
s0 = np.nanstd(fw[lab == 0]); s1 = np.nanstd(fw[lab == 1])
sep = cent[1] - cent[0]
print(f"\ntrilayer-only split: {n0} @ {cent[0]:.2f} (std {s0:.2f}) / "
      f"{n1} @ {cent[1]:.2f} (std {s1:.2f}); sep {sep:.2f}, "
      f"ratio {sep / max(s0, s1):.2f}")
for k in (0, 1):
    s = lab == k
    print(f"  cluster {k}: Si {np.nanmean(si[s]):.0f}±{np.nanstd(si[s]):.0f} "
          f"Gint {np.nanmean(gint[s]):.0f}±{np.nanstd(gint[s]):.0f} "
          f"2Damp {np.nanmean(amp[s]):.0f} 2Dcen {np.nanmean(cen[s]):.2f}"
          f"±{np.nanstd(cen[s]):.2f} Gcen {np.nanmean(gc[s]):.2f} "
          f"GFWHM {np.nanmean(gfw[s]):.2f} r2 {np.nanmean(r2[s]):.3f}")

# clean strain screen: corr on trilayer px
for a, b, nm in ((fw, cen, "FWHM,2Dcen"), (fw, si, "FWHM,Si"),
                 (fw, gint, "FWHM,Gint"), (fw, amp, "FWHM,2Damp"),
                 (gc, cen, "Gcen,2Dcen")):
    m = tri & np.isfinite(a) & np.isfinite(b)
    print(f"corr({nm}) on trilayer px = {np.corrcoef(a[m], b[m])[0, 1]:.2f}")

# --- morphology of the trilayer-only split ---
img_lab = to_image(lab, nxA, nyA)
for k, nm in ((0, "narrow"), (1, "broad")):
    cc, n = ndimage.label(img_lab == k)
    sizes = np.sort(np.bincount(cc.ravel())[1:])[::-1]
    print(f"{nm}: {n} components, sizes {sizes[:8]}")

# --- wall profile: vertical transects where a column crosses narrow->broad ---
img_fw = to_image(fw, nxA, nyA)
img_cen = to_image(cen, nxA, nyA)
profs_fw, profs_cen = [], []
for j in range(nxA):
    col = img_lab[:, j]
    rows_n = np.where(col == 0)[0]
    rows_b = np.where(col == 1)[0]
    if len(rows_n) < 3 or len(rows_b) < 3:
        continue
    # narrow band is at low row indices (top); find last narrow row block
    # transition: first broad row after a run of narrow rows
    t = None
    for r in range(1, nyA):
        if col[r] == 1 and (col[max(0, r - 3):r] == 0).sum() >= 2:
            t = r
            break
    if t is None or t < 4 or t > nyA - 4:
        continue
    w = img_fw[t - 4:t + 4, j]
    c = img_cen[t - 4:t + 4, j]
    if np.isfinite(w).all():
        profs_fw.append(w)
        profs_cen.append(c)
pf = np.array(profs_fw); pc = np.array(profs_cen)
print(f"\nwall transects: {len(pf)}")
if len(pf):
    mfw = np.nanmean(pf, 0); mcen = np.nanmean(pc, 0)
    print("mean FWHM profile (rows -4..+3 across wall):", mfw.round(1))
    print("mean 2Dcen profile:                          ", mcen.round(1))
    lo, hi = mfw[:3].mean(), mfw[-3:].mean()
    f10, f90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    x = np.arange(len(mfw))
    x10 = np.interp(f10, mfw, x); x90 = np.interp(f90, mfw, x)
    print(f"10-90% width: {abs(x90 - x10) * stepA:.1f} µm (step {stepA} µm)")

# --- secondaries on cluster mean spectra ---
ref_n = cluster_mean_spectrum(ii, lab, 0)
ref_b = cluster_mean_spectrum(ii, lab, 1)
mn = metrics_2d(wn, ref_n); mb = metrics_2d(wn, ref_b)
print(f"\ncluster means: narrow FWHM {mn['fwhm']:.1f} r2 {mn['r2']:.3f}; "
      f"broad FWHM {mb['fwhm']:.1f} r2 {mb['r2']:.3f}")

fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))
for lo, hi, ax, ttl in ((1640, 2200, axes[0], "M band region"),
                        (2350, 2550, axes[1], "G* region"),
                        (-150, 150, axes[2], "ULF / Rayleigh region")):
    m = (wn >= lo) & (wn <= hi)
    for spec, nm_, col in ((ref_n, "narrow (ABA-cand)", "C0"),
                           (ref_b, "broad (ABC-cand)", "C3")):
        ax.plot(wn[m], spec[m], col, lw=0.8, label=nm_)
    ax.set_title(ttl); ax.legend(fontsize=8)
    ax.set_xlabel("rel. cm$^{-1}$")
fig.tight_layout()
fig.savefig(HERE / "fig_secondaries.png", dpi=130)
print("wrote fig_secondaries.png")
mM = (wn >= 1650) & (wn <= 2250)
print("M-region counts: narrow max-min", ref_n[mM].max() - ref_n[mM].min(),
      "broad", ref_b[mM].max() - ref_b[mM].min())
print("baseline noise (1650-2250, med|diff|):",
      np.median(np.abs(np.diff(ref_n[mM]))).round(2),
      np.median(np.abs(np.diff(ref_b[mM]))).round(2))

# --- zone label raster for the final regions file ---
# 0 unassigned/no-graphene, 1 ABA-cand (narrow), 2 ABC-cand (broad),
# 3 fold/thick, 4 thin sliver, 5 graphene-but-unclassified (edge/junk)
zone = np.zeros(nxA * nyA, np.uint8)
zone[ok] = 5
zone[thin] = 4
zone[thick] = 3
zone[lab == 0] = 1
zone[lab == 1] = 2
np.savez(HERE / "zonesA.npz", zone=zone, lab=lab, tri=tri, thin=thin,
         thick=thick, fw=fw, cent=np.array(cent))

fig2, ax = plt.subplots(figsize=(9, 6.5))
from matplotlib.colors import ListedColormap
cmap = ListedColormap(["#f0f0f0", "#3b6fc9", "#c93b3b", "#7a2ea0",
                       "#7fd4c2", "#bdbdbd"])
ext = [cxA - nxA * stepA / 2, cxA + nxA * stepA / 2,
       cyA - nyA * stepA / 2, cyA + nyA * stepA / 2]
ax.imshow(to_image(zone, nxA, nyA), extent=ext, origin="upper", cmap=cmap,
          vmin=-0.5, vmax=5.5, interpolation="nearest")
ax.set_title("map A zones: blue=narrow(ABA-cand) red=broad(ABC-cand) "
             "purple=thick/fold teal=thin grey=unclassified")
ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
fig2.tight_layout()
fig2.savefig(HERE / "fig_zonesA.png", dpi=130)
print("wrote fig_zonesA.png, zonesA.npz")
