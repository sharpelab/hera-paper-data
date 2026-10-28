#!/usr/bin/env python3
"""Step 4 — cross-checks.
 (a) M-band region (1690–2150 cm⁻¹) per FWHM cluster — 532 nm = 2.33 eV is inside the
     2.1–2.4 eV dispersive-mode crossing, so this is recorded as uninformative by recipe.
 (b) G-band FWHM and position per cluster (supporting channel only).
 (c) Map 22 vs map 27 co-registration through the stage frame: do two independent
     acquisitions (12:57 pre-cut, 13:20 post-cut) agree on FWHM and label where they overlap?
 (d) Cut-edge effect in map 27: FWHM, G centre, 2D centre vs distance from the flake edge.
Writes figures/f4_mband.png, f4_coregistration.png, f4_edge.png; prints the numbers.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s4_crosschecks.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage, stats

from common import FIG, INT, load_map, to_img

sp = {k: dict(np.load(INT / f"split_{k}.npz")) for k in (22, 27)}
mt = {k: dict(np.load(INT / f"metrics_{k}.npz")) for k in (22, 27)}
mp = {k: load_map(k) for k in (22, 27)}

# (a) M band per cluster
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, k in zip(axes, (22, 27)):
    wn = sp[k]["wn"]
    for s, c, name in ((sp[k]["spec_narrow"], "C0", "narrow"), (sp[k]["spec_broad"], "C3", "broad")):
        sel = (wn > 1650) & (wn < 2200)
        b = np.median(s[(wn > 1650) & (wn < 1690)])
        ax.plot(wn[sel], (s - b)[sel], c, label=name)
        noise = np.std(np.diff(s[sel])) / np.sqrt(2)
        mm = (wn > 1690) & (wn < 2150)
        print(f"[{k}] {name}: M-region max {np.max((s-b)[mm]):.1f} counts above baseline, noise {noise:.1f} → "
              f"peak SNR {np.max((s-b)[mm])/noise:.1f} (cluster-mean of {(sp[k]['col_labels']==(0 if name=='narrow' else 1)).sum()} px)")
    ax.set_title(f"[{k}] M-band region per cluster (cluster-mean spectra, 2.33 eV — in the crossing zone)")
    ax.set_xlabel("Raman shift (cm⁻¹)"); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "f4_mband.png", dpi=120); plt.close(fig)

# (c) co-registration: map 27 pixel centres looked up in map 22 by nearest stage coordinate
m22, m27 = mp[22], mp[27]
fw22, fw27 = sp[22]["fwhm"], sp[27]["fwhm"]
lab22, lab27 = sp[22]["labels"], sp[27]["labels"]
e22, e27 = sp[22]["extent"], sp[27]["extent"]
# image pixel (iy, ix) -> stage coords (origin lower, 1 µm pitch)
def img_coords(extent, shape):
    ys = extent[2] + 0.5 + np.arange(shape[0]); xs = extent[0] + 0.5 + np.arange(shape[1])
    return np.meshgrid(xs, ys)
X27, Y27 = img_coords(e27, fw27.shape)
ix = np.round(X27 - (e22[0] + 0.5)).astype(int); iy = np.round(Y27 - (e22[2] + 0.5)).astype(int)
inside = (ix >= 0) & (ix < fw22.shape[1]) & (iy >= 0) & (iy < fw22.shape[0])
f22_on27 = np.full(fw27.shape, np.nan); l22_on27 = np.full(fw27.shape, -1)
f22_on27[inside] = fw22[iy[inside], ix[inside]]; l22_on27[inside] = lab22[iy[inside], ix[inside]]
both = np.isfinite(f22_on27) & np.isfinite(fw27)
r = stats.pearsonr(f22_on27[both], fw27[both])
agree = np.mean(l22_on27[both] == lab27[both])
print(f"co-registration (nearest stage pixel, no shift): {both.sum()} px in both maps' masked interiors; "
      f"FWHM corr r={r[0]:+.2f}; mean diff (27−22) {np.mean(fw27[both]-f22_on27[both]):+.2f} cm⁻¹; label agreement {agree:.2f}; "
      f"map-22 broad fraction inside the map-27 masked area {np.mean(l22_on27[both]==1):.2f} vs map-27 broad fraction {np.mean(lab27[both]==1):.2f}")
# best integer shift (stage reproducibility check)
best = None
for dx in range(-3, 4):
    for dy in range(-3, 4):
        jx, jy = ix + dx, iy + dy
        ok = (jx >= 0) & (jx < fw22.shape[1]) & (jy >= 0) & (jy < fw22.shape[0])
        f = np.full(fw27.shape, np.nan); f[ok] = fw22[jy[ok], jx[ok]]
        b = np.isfinite(f) & np.isfinite(fw27)
        if b.sum() < 50:
            continue
        rr = stats.pearsonr(f[b], fw27[b])[0]
        if best is None or rr > best[0]:
            best = (rr, dx, dy, b.sum())
print(f"best integer stage shift for map 22→27 FWHM agreement: dx={best[1]} dy={best[2]} µm, r={best[0]:+.2f} over {best[3]} px")
fig, axes = plt.subplots(1, 4, figsize=(22, 5.5))
im = axes[0].imshow(f22_on27, origin="lower", extent=e27, cmap="viridis", vmin=54, vmax=68); axes[0].set_title("map 22 FWHM resampled on map 27 grid (12:57, pre-cut)"); fig.colorbar(im, ax=axes[0], shrink=.8)
im = axes[1].imshow(fw27, origin="lower", extent=e27, cmap="viridis", vmin=54, vmax=68); axes[1].set_title("map 27 FWHM (13:20, post-cut)"); fig.colorbar(im, ax=axes[1], shrink=.8)
im = axes[2].imshow(np.where(both, fw27 - f22_on27, np.nan), origin="lower", extent=e27, cmap="coolwarm", vmin=-5, vmax=5); axes[2].set_title("difference 27 − 22"); fig.colorbar(im, ax=axes[2], shrink=.8)
axes[3].scatter(f22_on27[both], fw27[both], s=8, c=lab27[both], cmap="coolwarm"); axes[3].plot([54, 68], [54, 68], "k--", lw=.7); axes[3].set_xlabel("map 22 FWHM"); axes[3].set_ylabel("map 27 FWHM"); axes[3].set_title(f"r={r[0]:+.2f}")
for ax in axes[:3]:
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
fig.tight_layout(); fig.savefig(FIG / "f4_coregistration.png", dpi=120); plt.close(fig)

# (d) cut-edge effect in map 27: distance from the flake edge
pr27 = dict(np.load(INT / "proxies_27.npz"))
flake = to_img(pr27["flake"], m27)
dist = ndimage.distance_transform_edt(flake)
mask27 = sp[27]["mask"]
gc = np.where(mask27, to_img(mt[27]["g_center"], m27), np.nan)
cen = np.where(mask27, to_img(mt[27]["center"], m27), np.nan)
print("map 27 vs distance from flake edge (µm): d | n | FWHM | G centre | 2D centre | narrow fraction")
for d in (1, 2, 3, 4, 5):
    sel = mask27 & (np.round(dist) == d) if d < 5 else mask27 & (dist >= 5)
    print(f"  {d if d < 5 else '≥5'} | {sel.sum()} | {np.nanmean(fw27[sel]):.1f} | {np.nanmean(gc[sel]):.2f} | {np.nanmean(cen[sel]):.1f} | {np.mean(lab27[sel]==0):.2f}")
# same for map 22 (natural flake edge, uncut)
pr22 = dict(np.load(INT / "proxies_22.npz"))
dist22 = ndimage.distance_transform_edt(to_img(pr22["flake"], m22))
mask22 = sp[22]["mask"]; gc22 = np.where(mask22, to_img(mt[22]["g_center"], m22), np.nan)
print("map 22 (uncut edges) vs distance from flake edge: d | n | FWHM | G centre | narrow fraction")
for d in (1, 2, 3, 4, 5):
    sel = mask22 & (np.round(dist22) == d) if d < 5 else mask22 & (dist22 >= 5)
    print(f"  {d if d < 5 else '≥5'} | {sel.sum()} | {np.nanmean(fw22[sel]):.1f} | {np.nanmean(gc22[sel]):.2f} | {np.mean(lab22[sel]==0):.2f}")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, (v, name) in zip(axes, ((fw27, "2D FWHM"), (gc, "G centre"), (cen, "2D centre"))):
    ax.scatter(dist[mask27], v[mask27], s=8, c=lab27[mask27], cmap="coolwarm"); ax.set_xlabel("distance from flake edge (µm)"); ax.set_title(f"map 27: {name} vs edge distance")
fig.tight_layout(); fig.savefig(FIG / "f4_edge.png", dpi=120)
