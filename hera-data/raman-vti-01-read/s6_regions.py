#!/usr/bin/env python3
"""Step 6 — region-label raster in the stage µm frame (regions.npz + regions.png).

Grid: 1 µm pitch, pixel centres at integer+0.5 offsets matching the WITec scan
grids (both maps were acquired at 1 µm pitch on the same stage), covering the
union of the two Raman-map footprints. Two stage rasters share the grid:
  labels_S0  — map 22 (2026-05-28 12:57, whole flake, pre-cut)
  labels_S1  — map 27 (2026-05-28 13:20, after the first cut); NaN→0 outside its footprint
  labels_fused — S1 where S1 was mapped, else S0; `stage` says which (0/1)
  *_smooth — 3×3 majority-filtered versions of the 10/11 labels (for region reading;
             per-pixel versions are primary)
Label key (uint8):
   0 unmapped (outside the map footprint)
   1 substrate — no graphene 2D band
   2 graphene, other thickness population (thicker: folded wedge / opaque graphite chunk)
   3 graphene, other thickness population (thinner strip)
   5 graphene, unclassified (edge ring — partial spot —, low r² or low 2D amplitude)
  10 region A — main thickness, NARROW 2D population (ABA-consistent)
  11 region B — main thickness, BROAD 2D population (ABC candidate)
  12 mixed / boundary — wall-adjacent pixel with α ∈ (0.2, 0.8)
Verdict strings per label are in `key` (JSON) inside the npz; result.md is authoritative.
Also stored: device_rect (inferred channel rectangle, stage µm), cut_footprints
(1064 nm passes), map footprints, per-region statistics (JSON).
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s6_regions.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from common import FIG, HERE, INT, load_map, to_img

G_MODE = {22: (3000, 4700), 27: (3300, 4900)}
maps = {k: load_map(k) for k in (22, 27)}
ext = {k: np.array(maps[k]["extent"]) for k in (22, 27)}
x0 = min(ext[22][0], ext[27][0]); x1 = max(ext[22][1], ext[27][1])
y0 = min(ext[22][2], ext[27][2]); y1 = max(ext[22][3], ext[27][3])
nx, ny = int(round(x1 - x0)), int(round(y1 - y0))
x_edges = x0 + np.arange(nx + 1); y_edges = y0 + np.arange(ny + 1)
xc = x_edges[:-1] + 0.5; yc = y_edges[:-1] + 0.5


def labels_for(k):
    m = maps[k]
    pr = dict(np.load(INT / f"proxies_{k}.npz")); sp = dict(np.load(INT / f"split_{k}.npz")); al = dict(np.load(INT / f"alpha_{k}.npz"))
    flake = to_img(pr["flake"], m); g = to_img(pr["g"], m)
    lo, hi = G_MODE[k]
    si = to_img(pr["si"], m); si_sub = np.median(si[~flake])
    interior = ndimage.binary_erosion(flake, iterations=1)
    lab = np.ones(flake.shape, np.uint8)                        # substrate
    lab[flake] = 5                                              # edge ring / unclassified by default
    lab[interior & (g >= hi)] = 2
    lab[interior & (g <= lo)] = 3
    lab[flake & (si < 0.5 * si_sub)] = 2                        # opaque bulk graphite (Si line extinguished)
    lab[sp["mask"] & (sp["labels"] == 0)] = 10
    lab[sp["mask"] & (sp["labels"] == 1)] = 11
    lab[sp["mask"] & al["wall"] & al["mixed"]] = 12
    # smooth: 3×3 majority among {10, 11} within the masked interior
    is10 = (lab == 10).astype(float); is11 = (lab == 11).astype(float)
    n10 = ndimage.uniform_filter(is10, 3, mode="constant") * 9; n11 = ndimage.uniform_filter(is11, 3, mode="constant") * 9
    sm = lab.copy()
    sel = sp["mask"]
    sm[sel & (n11 > n10)] = 11; sm[sel & (n10 > n11)] = 10
    sm[sp["mask"] & al["wall"] & al["mixed"]] = 12
    # place on the common grid
    full = np.zeros((ny, nx), np.uint8); full_s = np.zeros((ny, nx), np.uint8)
    ix = int(round(ext[k][0] - x0)); iy = int(round(ext[k][2] - y0))
    full[iy:iy + lab.shape[0], ix:ix + lab.shape[1]] = lab
    full_s[iy:iy + lab.shape[0], ix:ix + lab.shape[1]] = sm
    fw = np.full((ny, nx), np.nan); fw[iy:iy + lab.shape[0], ix:ix + lab.shape[1]] = sp["fwhm"]
    return full, full_s, fw, sp


L0, L0s, F0, sp22 = labels_for(22)
L1, L1s, F1, sp27 = labels_for(27)
stage = np.zeros((ny, nx), np.uint8); stage[L1 > 0] = 1
fused = np.where(L1 > 0, L1, L0); fused_s = np.where(L1 > 0, L1s, L0s)

device_rect = dict(x=[-12045.5, -12034.0], y=[1274.0, 1287.0],
                   note="inferred from video images 004/007 + 1064 nm pass footprints; not testimony")
cut = {30: dict(x=[-12051.6, -12023.6], y=[1288.0, 1301.0], time="13:27"), 35: dict(x=[-12046.5, -12028.5], y=[1266.0, 1274.0], time="13:30")}

# per-region statistics (per-pixel labels)
stats = {}
for name, L, F, k in (("S0_map22", L0, F0, 22), ("S1_map27", L1, F1, 27)):
    m = maps[k]; mt = dict(np.load(INT / f"metrics_{k}.npz"))
    cen = np.full((ny, nx), np.nan); gc = cen.copy(); gf = cen.copy()
    ix = int(round(ext[k][0] - x0)); iy = int(round(ext[k][2] - y0))
    for arr, key in ((cen, "center"), (gc, "g_center"), (gf, "g_fwhm")):
        arr[iy:iy + m["ny"], ix:ix + m["nx"]] = to_img(mt[key], m)
    st = {}
    for lab_id, nm in ((10, "A_narrow"), (11, "B_broad"), (12, "mixed")):
        sel = L == lab_id
        if not sel.any():
            continue
        yy, xx = np.nonzero(sel)
        comp, ncomp = ndimage.label(sel)
        sizes = np.bincount(comp.ravel())[1:]
        st[nm] = dict(n_px=int(sel.sum()), area_um2=float(sel.sum()), fwhm_mean=float(np.nanmean(F[sel])), fwhm_sd=float(np.nanstd(F[sel])),
                      center_2d=float(np.nanmean(cen[sel])), g_center=float(np.nanmean(gc[sel])), g_fwhm=float(np.nanmean(gf[sel])),
                      centroid_um=[float(xc[xx].mean()), float(yc[yy].mean())],
                      bbox_um=[float(xc[xx].min() - .5), float(xc[xx].max() + .5), float(yc[yy].min() - .5), float(yc[yy].max() + .5)],
                      n_components=int(ncomp), largest_component_px=int(sizes.max()))
    # inside the inferred device rectangle
    rx = (xc >= device_rect["x"][0]) & (xc <= device_rect["x"][1]); ry = (yc >= device_rect["y"][0]) & (yc <= device_rect["y"][1])
    R = np.outer(ry, rx)
    inside = {int(v): int(((L == v) & R).sum()) for v in np.unique(L[R])}
    st["device_rect_label_counts"] = inside
    st["device_rect_fwhm"] = dict(mean=float(np.nanmean(F[R & (L >= 10)])), sd=float(np.nanstd(F[R & (L >= 10)])), n=int(np.isfinite(F[R & (L >= 10)]).sum()))
    stats[name] = st
print(json.dumps(stats, indent=1))

key = {0: "unmapped", 1: "substrate (no graphene)", 2: "graphene, other thickness (thicker: folded wedge, bulk graphite)", 3: "graphene, other thickness (thinner strip, interior pixels only)",
       5: "graphene, main thickness, unclassified (edge/low-quality fit)",
       10: "region A: main thickness, narrow 2D population — ABA-consistent (see result.md for strength + stage)",
       11: "region B: main thickness, broad 2D population — ABC candidate (see result.md for strength + stage)",
       12: "mixed/boundary: wall-adjacent, α in (0.2, 0.8) — not a third stacking"}
np.savez_compressed(HERE / "regions.npz", labels_S0=L0, labels_S1=L1, labels_fused=fused, labels_S0_smooth=L0s, labels_S1_smooth=L1s,
                    labels_fused_smooth=fused_s, stage=stage, fwhm_S0=F0, fwhm_S1=F1, x_edges=x_edges, y_edges=y_edges, x_centres=xc, y_centres=yc,
                    frame="WITec stage µm, vti-01.wip (sample 73474_), 2026-05-28; pixel pitch 1 µm",
                    key=json.dumps(key), stats=json.dumps(stats), device_rect=json.dumps(device_rect), cut_footprints=json.dumps(cut),
                    map_footprints=json.dumps({k: ext[k].tolist() for k in (22, 27)}),
                    stage_stamps=json.dumps({"S0": "2026-05-28 12:57 local, map 22, flake stage pre-cut, pre-transfer (imagery-inferred)",
                                             "S1": "2026-05-28 13:20 local, map 27, after first laser cut, pre-transfer (imagery-inferred)"}))

# figure
cmap = matplotlib.colors.ListedColormap(["white", "#d9d9d9", "#6a3d9a", "#b2df8a", "#bdbdbd", "#1f78b4", "#e31a1c", "#ff7f00"])
bounds = [-.5, .5, 1.5, 2.5, 3.5, 5.5, 10.5, 11.5, 12.5]
norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
vid = np.load(INT / "video_19.npz"); rgb, vext = vid["rgb"], vid["extent"]
fig, axes = plt.subplots(1, 3, figsize=(22, 7))
for ax, (L, title) in zip(axes, ((L0s, "S0 — map 22, 12:57 pre-cut (3×3-majority labels)"), (L1s, "S1 — map 27, 13:20 post-cut"), (fused_s, "fused: S1 where mapped, else S0"))):
    ax.imshow(rgb, extent=[vext[0], vext[1], min(vext[2], vext[3]), max(vext[2], vext[3])], origin="upper" if vext[2] > vext[3] else "lower", alpha=.55)
    ax.imshow(np.ma.masked_equal(L, 0), origin="lower", extent=[x0, x1, y0, y1], cmap=cmap, norm=norm, interpolation="nearest", alpha=.9)
    ax.add_patch(mpatches.Rectangle((device_rect["x"][0], device_rect["y"][0]), np.diff(device_rect["x"])[0], np.diff(device_rect["y"])[0], fill=False, ec="k", lw=2, ls="--"))
    for c in cut.values():
        ax.add_patch(mpatches.Rectangle((c["x"][0], c["y"][0]), np.diff(c["x"])[0], np.diff(c["y"])[0], fill=False, ec="yellow", lw=1, ls=":"))
    ax.set_xlim(x0 - 2, x1 + 2); ax.set_ylim(y0 - 2, y1 + 2); ax.set_title(title); ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
handles = [mpatches.Patch(color=cmap(norm(v)), label=f"{v}: {key[v].split(' — ')[0].split(' (see')[0]}") for v in (1, 2, 3, 5, 10, 11, 12)]
handles += [mpatches.Patch(fill=False, ec="k", ls="--", label="inferred device rectangle"), mpatches.Patch(fill=False, ec="yellow", ls=":", label="1064 nm cut passes")]
axes[2].legend(handles=handles, fontsize=7, loc="lower left")
fig.suptitle("vti-01 Raman stacking read — region labels, stage µm frame (regions.npz)"); fig.tight_layout(); fig.savefig(HERE / "regions.png", dpi=130)
