#!/usr/bin/env python3
"""Step 5 / Verify — mixed-spectrum decomposition. Every thickness-masked pixel is fit
as α·narrow + (1−α)·broad against the map's own cluster-mean spectra
(`metrics.decompose_mixed`); intermediate-FWHM pixels (60.5–62.5 cm⁻¹) are the
straddling candidates. α ∈ (0.2, 0.8) → mixed/boundary, not a third category.
Writes intermediates/alpha_<k>.npz, figures/f5_mixed.png.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s5_mixed.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from common import FIG, INT, load_map, to_img
from metrics import decompose_mixed

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for row, k in enumerate((22, 27)):
    m = load_map(k)
    sp = dict(np.load(INT / f"split_{k}.npz"))
    wn, ii = m["wn"], m["ii"]
    a_ref, b_ref = sp["spec_narrow"], sp["spec_broad"]
    alpha = np.full(ii.shape[1], np.nan); r2 = np.full(ii.shape[1], np.nan)
    idx_img = to_img(np.arange(ii.shape[1]), m)
    cols = idx_img[sp["mask"]]
    for j in cols:
        d = decompose_mixed(wn, ii[:, j], a_ref, b_ref)
        if d:
            alpha[j], r2[j] = d["alpha"], d["r2"]
    A = np.where(sp["mask"], to_img(alpha, m), np.nan); R = np.where(sp["mask"], to_img(r2, m), np.nan)
    fw, lab = sp["fwhm"], sp["labels"]
    inter = sp["mask"] & (fw > 60.5) & (fw < 62.5)
    mid = (A > 0.2) & (A < 0.8)
    # wall pixels: masked pixels with a neighbour of the other label
    other = np.zeros_like(lab, bool)
    for kk in (0, 1):
        dil = ndimage.binary_dilation(lab == kk, structure=np.ones((3, 3)))
        other |= (lab == 1 - kk) & dil
    wall = other & sp["mask"]
    print(f"[{k}] α fit r² median {np.nanmedian(R):.3f}; α median narrow-cluster {np.nanmedian(A[lab==0]):.2f}, broad-cluster {np.nanmedian(A[lab==1]):.2f}")
    print(f"     intermediate-FWHM px (60.5–62.5): {inter.sum()} of {sp['mask'].sum()}; of these α∈(0.2,0.8): {np.mean(mid[inter]):.2f}; "
          f"of these adjacent to the other label: {np.mean(wall[inter]):.2f}")
    print(f"     all masked px with α∈(0.2,0.8): {mid[sp['mask']].sum()} ({np.mean(mid[sp['mask']]):.2f}); wall-adjacent px: {wall.sum()}, of which mid-α {np.mean(mid[wall]):.2f}; "
          f"interior (non-wall) px mid-α {np.mean(mid[sp['mask'] & ~wall]):.2f}")
    np.savez_compressed(INT / f"alpha_{k}.npz", alpha=A, r2=R, mixed=mid & sp["mask"], wall=wall, intermediate=inter)
    im = axes[row, 0].imshow(A, origin="lower", extent=sp["extent"], cmap="coolwarm_r", vmin=0, vmax=1); axes[row, 0].set_title(f"[{k}] α (1 = narrow ref, 0 = broad ref)"); fig.colorbar(im, ax=axes[row, 0], shrink=.8)
    im = axes[row, 1].imshow(np.where(sp["mask"], mid.astype(float), np.nan), origin="lower", extent=sp["extent"], cmap="gray_r", vmin=0, vmax=1); axes[row, 1].set_title(f"[{k}] α ∈ (0.2, 0.8) — mixed/boundary candidates")
    axes[row, 2].hist(A[sp["mask"]], bins=40, color="gray"); axes[row, 2].hist(A[inter], bins=40, color="C1", alpha=.7, label="intermediate FWHM"); axes[row, 2].hist(A[wall], bins=40, color="C2", alpha=.5, label="wall-adjacent"); axes[row, 2].legend(); axes[row, 2].set_xlabel("α"); axes[row, 2].set_title(f"[{k}] α distribution")
    for ax in axes[row, :2]:
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
fig.tight_layout(); fig.savefig(FIG / "f5_mixed.png", dpi=120)
