#!/usr/bin/env python3
"""Step 3 — two-population read on map A (+ map B), with the mandatory
screens: thickness proxies (Si-520 amp, 2D amp, G integral), strain
(2D-center co-variation), morphology (coherent domains vs gradients),
and cross-map consistency A vs B."""
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
from metrics import metrics_2d, decompose_mixed

z = np.load(HERE / "map_metrics.npz")
dsets = load_wip(HERE / "inputs" / "vti-01.wip")
maps = {d["caption"]: d for d in dsets}
A = maps["73474_--Scan LA--003--Spec.Data 1"]
B = maps["73474_--Scan LA--005--Spec.Data 1"]


def geom(tag):
    cx, cy, nx, ny, step = z[f"{tag}_geom"]
    return cx, cy, int(nx), int(ny), step


def world_grids(tag):
    cx, cy, nx, ny, step = geom(tag)
    ix = np.arange(nx); iy = np.arange(ny)
    xs = cx + (ix - (nx - 1) / 2.0) * step
    ys = cy - (iy - (ny - 1) / 2.0) * step   # row 0 = +y (Scale y = -1)
    return xs, ys


def g_integral(wn, ii):
    """Integrated G intensity 1565-1605 minus linear baseline from
    1520-1550 / 1620-1650 — robust thickness proxy."""
    def win(lo, hi):
        m = (wn >= lo) & (wn <= hi)
        return m
    mL, mR, mG = win(1520, 1550), win(1620, 1650), win(1565, 1605)
    base = 0.5 * (ii[mL].mean(0) + ii[mR].mean(0))
    return np.clip(ii[mG] - base, 0, None).sum(0)


# ---------- map A ----------
cxA, cyA, nxA, nyA, stepA = geom("A")
fw = z["A_px_fwhm"]; cen = z["A_px_center"]; amp = z["A_px_amp"]
r2 = z["A_px_r2"]; si = z["A_si_amp"]; gfw = z["A_g_fwhm"]; gc = z["A_g_center"]
gint = g_integral(A["wn"], A["ii"])
ok = np.isfinite(fw)
print(f"map A: {ok.sum()} graphene px")

# thickness proxies on flake pixels
print("Si amp on-flake: p5..p95 =", np.nanpercentile(si[ok], [5, 50, 95]).round(0))
print("2D amp on-flake: p5..p95 =", np.nanpercentile(amp[ok], [5, 50, 95]).round(0))
print("G integral on-flake: p5..p95 =", np.nanpercentile(gint[ok], [5, 50, 95]).round(0))

# FWHM split on all flake pixels (first pass)
lab, cent = two_population_split(fw)
print(f"first-pass split: {(lab==0).sum()} @ {cent[0]:.1f} / "
      f"{(lab==1).sum()} @ {cent[1]:.1f} cm^-1")
for k in (0, 1):
    s = lab == k
    print(f"  cluster {k}: FWHM {np.nanmean(fw[s]):.1f}±{np.nanstd(fw[s]):.1f}, "
          f"2D center {np.nanmean(cen[s]):.1f}±{np.nanstd(cen[s]):.1f}, "
          f"2D amp {np.nanmean(amp[s]):.0f}±{np.nanstd(amp[s]):.0f}, "
          f"Si amp {np.nanmean(si[s]):.0f}±{np.nanstd(si[s]):.0f}, "
          f"G int {np.nanmean(gint[s]):.0f}±{np.nanstd(gint[s]):.0f}, "
          f"G FWHM {np.nanmean(gfw[s]):.1f}±{np.nanstd(gfw[s]):.1f}, "
          f"G center {np.nanmean(gc[s]):.2f}±{np.nanstd(gc[s]):.2f}")
sep = cent[1] - cent[0]
w0, w1 = np.nanstd(fw[lab == 0]), np.nanstd(fw[lab == 1])
print(f"separation {sep:.1f} vs within-cluster spread {w0:.1f}/{w1:.1f} "
      f"-> ratio {sep / max(w0, w1):.1f}")

# fold detection: Si amp far below median (thicker), or 2D amp outlier
si_med = np.nanmedian(si[ok])
fold = ok & (si < 0.8 * si_med)
print(f"fold/thick candidate px (Si amp < 0.8*median): {fold.sum()}")
print(f"  their FWHM {np.nanmean(fw[fold]):.1f}, 2D amp {np.nanmean(amp[fold]):.0f}, "
      f"G int {np.nanmean(gint[fold]):.0f}")

# morphology: connected components of the broad cluster (excluding fold)
img_lab = to_image(lab, nxA, nyA).astype(float)
img_fold = to_image(fold, nxA, nyA)
broad = (img_lab == 1) & ~img_fold
narrow = (img_lab == 0) & ~img_fold
for name, m in (("broad", broad), ("narrow", narrow)):
    cc, n = ndimage.label(m)
    sizes = np.sort(np.bincount(cc.ravel())[1:])[::-1]
    print(f"{name}: {n} components, sizes {sizes[:6]}")

# wall sharpness: FWHM profile along rows crossing the main boundary
img_fw = to_image(fw, nxA, nyA)
img_cen = to_image(cen, nxA, nyA)

# strain screen: correlation of FWHM with 2D center among flake px (no fold)
sel = ok & ~fold
cc_fc = np.corrcoef(fw[sel], cen[sel])[0, 1]
cc_fsi = np.corrcoef(fw[sel], si[sel])[0, 1]
cc_famp = np.corrcoef(fw[sel], amp[sel])[0, 1]
cc_fg = np.corrcoef(fw[sel & np.isfinite(gint)], gint[sel & np.isfinite(gint)])[0, 1]
print(f"corr(FWHM, 2D center) = {cc_fc:.2f}")
print(f"corr(FWHM, Si amp)    = {cc_fsi:.2f}")
print(f"corr(FWHM, 2D amp)    = {cc_famp:.2f}")
print(f"corr(FWHM, G int)     = {cc_fg:.2f}")
# per-cluster thickness deltas (excluding fold)
for k in (0, 1):
    s = (lab == k) & ~fold
    print(f"  cluster {k} (no fold): n={s.sum()} Si {np.nanmean(si[s]):.0f} "
          f"2Damp {np.nanmean(amp[s]):.0f} Gint {np.nanmean(gint[s]):.0f} "
          f"2Dcen {np.nanmean(cen[s]):.2f} FWHM {np.nanmean(fw[s]):.2f}")

# G center vs 2D center (strain/doping axis), directional only
s2 = sel & np.isfinite(gc)
print(f"corr(G center, 2D center) = {np.corrcoef(gc[s2], cen[s2])[0,1]:.2f}")

# mixed-spectrum decomposition against A's own cluster means
ref_n = cluster_mean_spectrum(A["ii"], np.where(~fold, lab, -1), 0)
ref_b = cluster_mean_spectrum(A["ii"], np.where(~fold, lab, -1), 1)
mn = metrics_2d(A["wn"], ref_n); mb = metrics_2d(A["wn"], ref_b)
print(f"cluster-mean spectra: narrow FWHM {mn['fwhm']:.1f} r2 {mn['r2']:.3f} "
      f"skew {mn['skew']:.2f} ratio {mn['ratio_lh']:.2f}; "
      f"broad FWHM {mb['fwhm']:.1f} r2 {mb['r2']:.3f} skew {mb['skew']:.2f} "
      f"ratio {mb['ratio_lh']:.2f}")
lo_c, hi_c = cent
inter = np.where(ok & (fw > lo_c + 1.5) & (fw < hi_c - 1.5) & ~fold)[0]
alphas = []
for j in inter:
    d = decompose_mixed(A["wn"], A["ii"][:, j], ref_n, ref_b)
    if d:
        alphas.append((j, d["alpha"], d["r2"]))
al = np.array([a for _, a, _ in alphas])
print(f"intermediate-FWHM px: {len(inter)}; mid-α (0.2-0.8): "
      f"{(np.sum((al > 0.2) & (al < 0.8)) if len(al) else 0)}")

# ---------- map B ----------
cxB, cyB, nxB, nyB, stepB = geom("B")
fwB = z["B_px_fwhm"]; cenB = z["B_px_center"]; ampB = z["B_px_amp"]
siB = z["B_si_amp"]; gfwB = z["B_g_fwhm"]
okB = np.isfinite(fwB)
labB, centB = two_population_split(fwB)
sepB = centB[1] - centB[0]
sB0, sB1 = np.nanstd(fwB[labB == 0]), np.nanstd(fwB[labB == 1])
print(f"\nmap B: {okB.sum()} graphene px; FWHM {np.nanmean(fwB[okB]):.1f}"
      f"±{np.nanstd(fwB[okB]):.1f}; forced split {centB[0]:.1f}/{centB[1]:.1f} "
      f"sep {sepB:.1f} vs spread {sB0:.1f}/{sB1:.1f} -> ratio "
      f"{sepB / max(sB0, sB1):.1f}")
print(f"  2D center {np.nanmean(cenB[okB]):.1f}±{np.nanstd(cenB[okB]):.1f}, "
      f"G FWHM {np.nanmean(gfwB[okB]):.1f}")

# A pixels inside B footprint, for cross-map consistency
xsA, ysA = world_grids("A")
XX, YY = np.meshgrid(xsA, ysA)
inB = (XX > cxB - nxB * stepB / 2) & (XX < cxB + nxB * stepB / 2) & \
      (YY > cyB - nyB * stepB / 2) & (YY < cyB + nyB * stepB / 2)
fwA_inB = img_fw[inB]
print(f"A px inside B footprint: {np.isfinite(fwA_inB).sum()}, "
      f"FWHM {np.nanmean(fwA_inB):.1f}±{np.nanstd(fwA_inB):.1f}")

# ---------- figures ----------
xsB, ysB = world_grids("B")
extA = [xsA[0] - stepA/2, xsA[-1] + stepA/2, ysA[-1] - stepA/2, ysA[0] + stepA/2]
extB = [xsB[0] - stepB/2, xsB[-1] + stepB/2, ysB[-1] - stepB/2, ysB[0] + stepB/2]

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
lab_img = to_image(np.where(fold, 2.0, lab.astype(float)), nxA, nyA)
lab_img[to_image(lab, nxA, nyA) == -1] = np.nan
im = axes[0, 0].imshow(lab_img, extent=extA, origin="upper", cmap="coolwarm",
                       vmin=0, vmax=2)
axes[0, 0].set_title("A: split (blue=narrow, red=broad, dark red=fold/thick)")
im = axes[0, 1].imshow(img_fw, extent=extA, origin="upper", cmap="viridis",
                       vmin=54, vmax=68)
fig.colorbar(im, ax=axes[0, 1], shrink=0.8)
axes[0, 1].set_title("A: 2D FWHM (clipped 54-68)")
im = axes[0, 2].imshow(img_cen, extent=extA, origin="upper", cmap="coolwarm",
                       vmin=2690, vmax=2704)
fig.colorbar(im, ax=axes[0, 2], shrink=0.8)
axes[0, 2].set_title("A: 2D center")
axes[1, 0].scatter(fw[sel], cen[sel], s=4, alpha=0.4,
                   c=np.where(lab[sel] == 1, "C3", "C0"))
axes[1, 0].set_xlabel("2D FWHM"); axes[1, 0].set_ylabel("2D center")
axes[1, 0].set_title(f"A: FWHM vs center (r={cc_fc:.2f})")
axes[1, 1].scatter(fw[sel], si[sel], s=4, alpha=0.4,
                   c=np.where(lab[sel] == 1, "C3", "C0"))
axes[1, 1].set_xlabel("2D FWHM"); axes[1, 1].set_ylabel("Si-520 amp")
axes[1, 1].set_title(f"A: FWHM vs Si amp (r={cc_fsi:.2f})")
wnw = (A["wn"] > 2550) & (A["wn"] < 2850)
for spec, lab_, col in ((ref_n, f"narrow mean {mn['fwhm']:.1f}", "C0"),
                        (ref_b, f"broad mean {mb['fwhm']:.1f}", "C3")):
    s_ = spec[wnw] - np.median(spec[(A["wn"] > 2500) & (A["wn"] < 2550)])
    axes[1, 2].plot(A["wn"][wnw], s_ / s_.max(), col, label=lab_)
axes[1, 2].legend(); axes[1, 2].set_title("A: cluster mean 2D lineshapes")
axes[1, 2].set_xlabel("rel. cm$^{-1}$")
fig.tight_layout()
fig.savefig(HERE / "fig_split.png", dpi=130)
print("wrote fig_split.png")

fig2, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(to_image(fwB, nxB, nyB), extent=extB, origin="upper",
               cmap="viridis", vmin=54, vmax=68)
fig2.colorbar(im, ax=ax, shrink=0.8)
ax.set_title("B: 2D FWHM (clipped 54-68)")
fig2.tight_layout()
fig2.savefig(HERE / "fig_mapB_fwhm.png", dpi=130)
print("wrote fig_mapB_fwhm.png")

np.savez(HERE / "split_results.npz", A_labels=lab, A_centers=np.array(cent),
         A_fold=fold, B_labels=labB, B_centers=np.array(centB),
         A_ref_narrow=ref_n, A_ref_broad=ref_b, wn=A["wn"],
         inter_idx=np.array([j for j, _, _ in alphas]),
         inter_alpha=np.array([a for _, a, _ in alphas]),
         inter_r2=np.array([r for _, _, r in alphas]))
print("wrote split_results.npz")
