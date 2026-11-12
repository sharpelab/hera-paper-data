#!/usr/bin/env python3
"""Step 3 — map read: thickness mask → two-population FWHM split → bimodality,
morphology, strain screen, terrace screen, cluster mean spectra. Maps 22 and 27.

Thickness mask: pixels in the main G-area mode (the device's thickness population),
eroded by one pixel from the flake edge, 2D fit r² ≥ 0.9, 2D amp ≥ 80 counts.
Bimodality: 2-means on FWHM; Ashman's D = |μ1−μ2| / sqrt((σ1²+σ2²)/2); the same on
3×3-binned spectra (noise-reduced FWHM) as a cross-check.
Morphology: connected components of each cluster (4-connectivity), wall-profile
transition widths along x through the largest wall.
Strain screen: FWHM vs 2D-centre correlation, G-centre vs 2D-centre slope.
Terrace screen: G area and Si 520 area (unsaturated) per cluster.

Writes intermediates/split_<k>.npz, figures/f3_split_<k>.png, f3_spectra_<k>.png.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s3_split.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage, stats

from common import FIG, INT, load_map, show, to_img
from map_tools import cluster_mean_spectrum, two_population_split
from metrics import metrics_2d

G_MODE = {22: (3000, 4700), 27: (3300, 4900)}   # main G-area mode, from f1_histograms.png


def binned_fwhm(m, mask_img, n=3):
    """FWHM of the mean spectrum over n×n blocks of masked pixels (≥ n*n-3 px present)."""
    ny, nx = mask_img.shape
    out = np.full((ny // n, nx // n), np.nan)
    cube = to_img(np.arange(m["ii"].shape[1]), m)      # column index per image pixel
    for by in range(ny // n):
        for bx in range(nx // n):
            blk = cube[by * n:(by + 1) * n, bx * n:(bx + 1) * n]
            mk = mask_img[by * n:(by + 1) * n, bx * n:(bx + 1) * n]
            if mk.sum() < n * n - 3:
                continue
            spec = m["ii"][:, blk[mk]].mean(axis=1)
            mm = metrics_2d(m["wn"], spec)
            if mm:
                out[by, bx] = mm["fwhm"]
    return out


for k in (22, 27):
    m = load_map(k)
    px = dict(np.load(INT / f"metrics_{k}.npz"))
    pr = dict(np.load(INT / f"proxies_{k}.npz"))
    flake_img = to_img(pr["flake"], m)
    interior = ndimage.binary_erosion(flake_img, iterations=1)
    lo, hi = G_MODE[k]
    mask = (to_img(pr["g"], m) > lo) & (to_img(pr["g"], m) < hi) & interior \
        & (to_img(px["r2"], m) >= 0.9) & (to_img(px["amp"], m) >= 80) & np.isfinite(to_img(px["fwhm"], m))
    fw = np.where(mask, to_img(px["fwhm"], m), np.nan)
    cen = np.where(mask, to_img(px["center"], m), np.nan)
    gc = np.where(mask, to_img(px["g_center"], m), np.nan)
    gfw = np.where(mask, to_img(px["g_fwhm"], m), np.nan)
    garea = np.where(mask, to_img(pr["g"], m), np.nan)
    siarea = np.where(mask, to_img(pr["si"], m), np.nan)
    tdg = np.where(mask, to_img(pr["td_g"], m), np.nan)
    print(f"\n=== map {k}: {mask.sum()} px in thickness-masked interior (of {flake_img.sum()} flake px)")

    labels, centers = two_population_split(fw.ravel())
    lab = labels.reshape(fw.shape)
    v0, v1 = fw[lab == 0], fw[lab == 1]
    D = abs(v1.mean() - v0.mean()) / np.sqrt((v0.std() ** 2 + v1.std() ** 2) / 2)
    print(f"2-means FWHM: {centers[0]:.1f} (σ {v0.std():.1f}, n {v0.size}) / {centers[1]:.1f} (σ {v1.std():.1f}, n {v1.size}); "
          f"split {centers[1]-centers[0]:.1f} cm⁻¹; Ashman D {D:.2f}")
    # per-pixel noise of FWHM: RMS of half the difference between horizontal neighbours inside a cluster
    d = fw[:, 1:] - fw[:, :-1]
    same = (lab[:, 1:] == lab[:, :-1]) & np.isfinite(d)
    noise = np.sqrt(np.mean(d[same] ** 2) / 2)
    print(f"per-pixel FWHM noise (same-cluster neighbour RMS/√2): {noise:.2f} cm⁻¹")
    # histogram dip test: counts at midpoint vs peaks
    h, e = np.histogram(fw[mask], bins=np.arange(48, 72, 1.0))
    c = 0.5 * (e[1:] + e[:-1])
    print("FWHM histogram (1 cm⁻¹ bins):", " ".join(f"{int(cc)}:{hh}" for cc, hh in zip(c, h) if hh))

    # binned cross-check
    bf = binned_fwhm(m, mask)
    bl, bc = two_population_split(bf.ravel())
    b0, b1 = bf[bl.reshape(bf.shape) == 0], bf[bl.reshape(bf.shape) == 1]
    Db = abs(b1.mean() - b0.mean()) / np.sqrt((b0.std() ** 2 + b1.std() ** 2) / 2) if b0.size > 1 and b1.size > 1 else np.nan
    print(f"3×3-binned FWHM: {bc[0]:.1f} (σ {b0.std():.1f}, n {b0.size}) / {bc[1]:.1f} (σ {b1.std():.1f}, n {b1.size}); Ashman D {Db:.2f}; "
          f"binned p5/p50/p95 {np.nanpercentile(bf,[5,50,95]).round(1)}")

    # morphology: connected components per cluster
    comps = {}
    for kk in (0, 1):
        cl, n = ndimage.label(lab == kk)
        sizes = np.bincount(cl.ravel())[1:]
        comps[kk] = (cl, sizes)
        print(f"cluster {kk} ({'narrow' if kk == 0 else 'broad'}): {n} components; largest {sorted(sizes)[-5:]} px "
              f"(of {sizes.sum()}); fraction in components ≥ 9 px: {sizes[sizes >= 9].sum() / sizes.sum():.2f}")
    # majority-filtered label map (3×3) to show coherent domains vs speckle
    lab_f = np.where(mask, lab, -1)
    maj = ndimage.generic_filter(np.where(mask, lab, np.nan).astype(float), lambda w: np.nanmean(w) if np.isfinite(w).sum() >= 5 else np.nan, size=3, mode="constant", cval=np.nan)
    agree = np.nanmean((maj[mask] > 0.5) == (lab[mask] == 1))
    print(f"pixel label agrees with 3×3 majority: {agree:.2f} (0.5 = speckle, 1 = perfectly coherent)")

    # strain screen
    ok = mask & np.isfinite(cen) & np.isfinite(gc)
    r_fc = stats.pearsonr(fw[ok], cen[ok])
    r_gc = stats.pearsonr(gc[ok], cen[ok])
    slope = np.polyfit(gc[ok], cen[ok], 1)[0]
    print(f"strain screen: corr(FWHM, 2D centre) r={r_fc[0]:+.2f}; corr(G centre, 2D centre) r={r_gc[0]:+.2f}, slope d2D/dG={slope:.2f}; "
          f"2D centre by cluster {np.nanmean(cen[lab==0]):.1f} / {np.nanmean(cen[lab==1]):.1f}; G centre by cluster {np.nanmean(gc[lab==0]):.2f} / {np.nanmean(gc[lab==1]):.2f}; "
          f"G FWHM by cluster {np.nanmean(gfw[lab==0]):.2f} / {np.nanmean(gfw[lab==1]):.2f}")
    # spatial gradient smoothness: fraction of FWHM variance explained by a 2-D quadratic surface (smooth field) vs by the cluster labels
    yy, xx = np.indices(fw.shape)
    A = np.c_[np.ones(ok.sum()), xx[ok], yy[ok], xx[ok] ** 2, yy[ok] ** 2, xx[ok] * yy[ok]]
    coef, *_ = np.linalg.lstsq(A, fw[ok], rcond=None)
    r2_surf = 1 - np.var(fw[ok] - A @ coef) / np.var(fw[ok])
    r2_lab = 1 - (np.var(v0) * v0.size + np.var(v1) * v1.size) / (np.var(fw[mask]) * mask.sum())
    print(f"FWHM variance explained: quadratic surface {r2_surf:.2f} vs 2-cluster labels {r2_lab:.2f}")
    # terrace screen
    print(f"terrace screen: G area by cluster {np.nanmean(garea[lab==0]):.0f}±{np.nanstd(garea[lab==0]):.0f} / {np.nanmean(garea[lab==1]):.0f}±{np.nanstd(garea[lab==1]):.0f}; "
          f"Si area {np.nanmean(siarea[lab==0]):.0f}±{np.nanstd(siarea[lab==0]):.0f} / {np.nanmean(siarea[lab==1]):.0f}±{np.nanstd(siarea[lab==1]):.0f}; "
          f"2D/G {np.nanmean(tdg[lab==0]):.2f} / {np.nanmean(tdg[lab==1]):.2f}; 2D amp {np.nanmean(np.where(mask,to_img(px['amp'],m),np.nan)[lab==0]):.0f} / {np.nanmean(np.where(mask,to_img(px['amp'],m),np.nan)[lab==1]):.0f}")

    # cluster mean spectra
    col_lab = np.full(m["ii"].shape[1], -1)
    idx_img = to_img(np.arange(m["ii"].shape[1]), m)
    col_lab[idx_img[lab == 0]] = 0
    col_lab[idx_img[lab == 1]] = 1
    s0 = cluster_mean_spectrum(m["ii"], col_lab, 0)
    s1 = cluster_mean_spectrum(m["ii"], col_lab, 1)
    m0, m1 = metrics_2d(m["wn"], s0), metrics_2d(m["wn"], s1)
    print(f"cluster-mean spectra: narrow FWHM {m0['fwhm']:.1f} centre {m0['center']:.1f} skew {m0['skew']:+.3f} r_lh {m0['ratio_lh']:.3f} r² {m0['r2']:.3f} | "
          f"broad FWHM {m1['fwhm']:.1f} centre {m1['center']:.1f} skew {m1['skew']:+.3f} r_lh {m1['ratio_lh']:.3f} r² {m1['r2']:.3f}")
    np.savez_compressed(INT / f"split_{k}.npz", mask=mask, labels=lab, fwhm=fw, centers=np.array(centers),
                        binned_fwhm=bf, col_labels=col_lab, spec_narrow=s0, spec_broad=s1, wn=m["wn"],
                        extent=np.array(m["extent"]), ashman_D=D, noise=noise)

    # figures
    fig, axes = plt.subplots(2, 4, figsize=(22, 10 if k == 22 else 13))
    im = axes[0, 0].imshow(fw, origin="lower", extent=m["extent"], cmap="viridis", vmin=54, vmax=68); axes[0, 0].set_title("2D FWHM, thickness-masked interior"); fig.colorbar(im, ax=axes[0, 0], shrink=.8)
    im = axes[0, 1].imshow(np.where(mask, lab, np.nan), origin="lower", extent=m["extent"], cmap="coolwarm", vmin=0, vmax=1); axes[0, 1].set_title(f"2-means labels (red = broad {centers[1]:.1f}, blue = narrow {centers[0]:.1f})")
    im = axes[0, 2].imshow(maj, origin="lower", extent=m["extent"], cmap="coolwarm", vmin=0, vmax=1); axes[0, 2].set_title("3×3 majority of labels (coherence)"); fig.colorbar(im, ax=axes[0, 2], shrink=.8)
    bext = [m["extent"][0], m["extent"][0] + bf.shape[1] * 3, m["extent"][2], m["extent"][2] + bf.shape[0] * 3]
    im = axes[0, 3].imshow(bf, origin="lower", extent=bext, cmap="viridis", vmin=54, vmax=68); axes[0, 3].set_title("FWHM of 3×3-binned spectra"); fig.colorbar(im, ax=axes[0, 3], shrink=.8)
    axes[1, 0].hist(fw[mask], bins=np.arange(48, 72, 0.5), color="gray", label="per-pixel"); axes[1, 0].hist(v0, bins=np.arange(48, 72, 0.5), color="C0", alpha=.6); axes[1, 0].hist(v1, bins=np.arange(48, 72, 0.5), color="C3", alpha=.6)
    axes[1, 0].set_title(f"FWHM histogram; Ashman D {D:.2f}, px noise {noise:.1f}"); axes[1, 0].set_xlabel("cm⁻¹")
    axes[1, 1].hist(bf[np.isfinite(bf)], bins=np.arange(48, 72, 0.5), color="C2"); axes[1, 1].set_title(f"3×3-binned FWHM; Ashman D {Db:.2f}"); axes[1, 1].set_xlabel("cm⁻¹")
    axes[1, 2].scatter(cen[ok], fw[ok], c=lab[ok], cmap="coolwarm", s=8); axes[1, 2].set_xlabel("2D centre"); axes[1, 2].set_ylabel("2D FWHM"); axes[1, 2].set_title(f"strain screen: r={r_fc[0]:+.2f}")
    axes[1, 3].scatter(gc[ok], cen[ok], c=lab[ok], cmap="coolwarm", s=8); axes[1, 3].set_xlabel("G centre"); axes[1, 3].set_ylabel("2D centre"); axes[1, 3].set_title(f"G–2D position: r={r_gc[0]:+.2f}, slope {slope:.2f}")
    for ax in axes[0]:
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    fig.suptitle(f"[{k}] {m['caption']} — two-population split"); fig.tight_layout(); fig.savefig(FIG / f"f3_split_{k}.png", dpi=120); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    wn = m["wn"]
    for ax, (lo_, hi_) in zip(axes[:2], ((2550, 2850), (1450, 2200))):
        sel = (wn > lo_) & (wn < hi_)
        for s, c, name in ((s0, "C0", f"narrow {m0['fwhm']:.1f}"), (s1, "C3", f"broad {m1['fwhm']:.1f}")):
            b = np.median(s[(wn > lo_) & (wn < lo_ + 30)])
            y = s - b
            ax.plot(wn[sel], y[sel] / (y[(wn > 2550) & (wn < 2850)].max() if lo_ > 2000 else y[(wn > 1560) & (wn < 1600)].max()), c, label=name)
        ax.set_xlabel("Raman shift (cm⁻¹)"); ax.legend()
    axes[0].set_title("cluster-mean 2D band (peak-normalised)"); axes[1].set_title("G + M-band region (G-normalised)")
    sel = (wn > 2550) & (wn < 2850)
    y0 = s0 - np.median(s0[(wn > 2550) & (wn < 2580)]); y1 = s1 - np.median(s1[(wn > 2550) & (wn < 2580)])
    axes[2].plot(wn[sel], (y1 / y1[sel].max() - y0 / y0[sel].max())[sel], "k"); axes[2].axhline(0, color="gray", lw=.5)
    axes[2].set_title("broad − narrow (peak-normalised)"); axes[2].set_xlabel("Raman shift (cm⁻¹)")
    fig.suptitle(f"[{k}] cluster-mean spectra"); fig.tight_layout(); fig.savefig(FIG / f"f3_spectra_{k}.png", dpi=120); plt.close(fig)
