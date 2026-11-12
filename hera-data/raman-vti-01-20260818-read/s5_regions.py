#!/usr/bin/env python3
"""Step 6 support — final region-label raster (stage µm frame) + region
stats + refined mixed-pixel decomposition. Writes regions.npz, regions.png."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "tools"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from scipy import ndimage

from raman_io import load_wip
from map_tools import to_image, cluster_mean_spectrum
from metrics import decompose_mixed, metrics_2d

z = np.load(HERE / "map_metrics.npz")
zz = np.load(HERE / "zonesA.npz")
zone = zz["zone"]; lab = zz["lab"]; fw = zz["fw"]
cxA, cyA, nxA, nyA, stepA = z["A_geom"]; nxA, nyA = int(nxA), int(nyA)

dsets = load_wip(HERE / "inputs" / "vti-01.wip")
A = {d["caption"]: d for d in dsets}["73474_--Scan LA--003--Spec.Data 1"]
wn, ii = A["wn"], A["ii"]

# pixel-center world coordinates (rotation 0.5 deg neglected, noted)
ix = np.arange(nxA); iy = np.arange(nyA)
xs = cxA + (ix - (nxA - 1) / 2.0) * stepA
ys = cyA - (iy - (nyA - 1) / 2.0) * stepA

# refined refs + mixed decomposition on intermediate/wall pixels
ref_n = cluster_mean_spectrum(ii, lab, 0)
ref_b = cluster_mean_spectrum(ii, lab, 1)
mn, mb = metrics_2d(wn, ref_n), metrics_2d(wn, ref_b)
print(f"refs: narrow {mn['fwhm']:.1f} broad {mb['fwhm']:.1f}")
inter = np.where(np.isfinite(fw) & (fw > 59.5) & (fw < 62.5) & (zone != 3)
                 & (zone != 4))[0]
res = [decompose_mixed(wn, ii[:, j], ref_n, ref_b) for j in inter]
al = np.array([r["alpha"] for r in res if r])
r2m = np.array([r["r2"] for r in res if r])
mid = (al > 0.2) & (al < 0.8)
print(f"intermediate 59.5-62.5 px: {len(inter)}; decomposed {len(al)}; "
      f"mid-alpha {mid.sum()} ({100*mid.mean():.0f}%); "
      f"decomp r2 median {np.median(r2m):.3f}")

# region components
img = to_image(zone, nxA, nyA)
regions = np.zeros_like(img, dtype=np.uint8)
# 1 = ABA domain(s), 2 = ABC main domain, 3 = ABC/ABA mixed top band,
# 4 = fold/thick (uninformative), 5 = thin sliver, 6 = graphene unclassified
cc_b, nb = ndimage.label(img == 2)
sizes = np.bincount(cc_b.ravel()); sizes[0] = 0
main_b = np.argmax(sizes)
print("broad components:", sorted(sizes[1:], reverse=True)[:6])
regions[(img == 2) & (cc_b == main_b)] = 2
regions[(img == 2) & (cc_b != main_b)] = 3   # other broad = top-band texture
regions[img == 1] = 1
regions[img == 3] = 4
regions[img == 4] = 5
regions[img == 5] = 6
# ABA pixels inside the top mixed band (y > 1289.5, x < -12045) -> label 3?
# keep class-faithful: ABA stays 1; region 3 is the disjoint ABC texture.

for r, nm in ((1, "ABA domains"), (2, "ABC main domain"),
              (3, "ABC top-band texture"), (4, "fold/thick"),
              (5, "thin"), (6, "unclassified graphene")):
    m = regions == r
    if m.sum():
        yy, xx = np.where(m)
        print(f"region {r} ({nm}): {m.sum()} px, centroid "
              f"({xs[xx].mean():.1f}, {ys[yy].mean():.1f}), "
              f"x {xs[xx].min():.0f}..{xs[xx].max():.0f}, "
              f"y {ys[yy].min():.0f}..{ys[yy].max():.0f}")
        if r in (1, 2, 3):
            v = to_image(fw, nxA, nyA)[m]
            print(f"    FWHM {np.nanmean(v):.1f}±{np.nanstd(v):.1f}")

key = [
    "0: no graphene / not mapped",
    "1: ABA domain (narrow 2D pop. 58.4 cm-1) -- verdict ABA (strong), stage S0",
    "2: ABC main domain (broad 2D pop. 63.4 cm-1) -- verdict ABC (strong), stage S0",
    "3: top-band ABC/ABA mixed texture (broad pop. px interleaved with ABA px & walls)"
    " -- verdict mixed ABA+ABC domains (strong as mixture), stage S0",
    "4: fold/thicker zone (Si-520 -16%, G x1.5, twisted t(3+3) fork) -- uninformative",
    "5: thin (non-trilayer) sliver -- uninformative for trilayer stacking",
    "6: graphene, quality/edge-rejected (flake rim, wall-straddling) -- unclassified",
]
np.savez(HERE / "regions.npz", labels=regions, x_um=xs, y_um=ys,
         key=np.array(key), stage=np.array([
             "S0 = intact exfoliated flake on SiO2/Si (imagery-inferred), "
             "map A 2026-05-28 19:57 UTC, 532.34 nm",
             "S1 = after first pickup (~20:10-20:19 UTC): leftover rectangle "
             "x -12047..-12035, y 1266..1289 re-confirmed broad/ABC by map B "
             "20:20 UTC (63.0 cm-1)"]))
print("wrote regions.npz")

fig, ax = plt.subplots(figsize=(10, 7))
cmap = ListedColormap(["#f2f2f2", "#3b6fc9", "#c93b3b", "#e8935a",
                       "#7a2ea0", "#7fd4c2", "#bdbdbd"])
ext = [xs[0] - stepA / 2, xs[-1] + stepA / 2,
       ys[-1] - stepA / 2, ys[0] + stepA / 2]
ax.imshow(regions, extent=ext, origin="upper", cmap=cmap, vmin=-0.5,
          vmax=6.5, interpolation="nearest")
ax.add_patch(plt.Rectangle((-12047, 1266), 12, 23, fill=False, ec="k",
                           lw=1.5, ls="--"))
ax.annotate("leftover piece,\nre-confirmed ABC at S1 (map B)",
            (-12047, 1265.2), fontsize=8, va="top")
ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
ax.set_title("vti-01 flake 73474 — region labels, stage frame, map A "
             "(2026-05-28 19:57 UTC, 532 nm)\n"
             "blue=ABA(strong) red=ABC main(strong) orange=mixed top band "
             "purple=fold teal=thin grey=unclassified")
fig.tight_layout()
fig.savefig(HERE / "regions.png", dpi=140)
print("wrote regions.png")
