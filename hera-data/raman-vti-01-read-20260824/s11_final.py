#!/usr/bin/env python3
"""s11_final.py — final stacking analysis + region products.

1. K=2 k-means on area-normalized 2D lineshapes, restricted to the uniform
   sheet population (G_area 3000-6500, excludes thick wedge/graphite/edges),
   joint over maps 003+005 (calibration verified identical, s10).
2. Cluster mean lineshapes + 3-Lorentzian decompositions (evidence values).
3. Region label rasters in the stage µm frame, two layers:
      labels_pre  — state of map 003 (before the 20:10-20:19 pickup)
      labels_post — state of map 005 (after pickup)
   Label key: 0 bg/unmapped, 1 sheet ABC-like, 2 sheet ABA-like,
   3 thick multilayer wedge, 4 graphite, 5 remnant ABC-like,
   6 remnant ABA-like, 7 graphene edge/unassigned.
4. regions.npz + regions.png + final_lineshapes.png + final_stats.txt

Run: uv run --with numpy --with scipy --with scikit-learn --with matplotlib python s11_final.py
"""
import numpy as np
from scipy.optimize import least_squares
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
EXC = float(d["exc_nm"])
KEYS = ["003", "005"]

shape_x = m["shape_x"]; dx = np.abs(np.gradient(shape_x))
shapes = m["shapes"].astype(float)
meta_k = m["meta_k"]; meta_j = m["meta_j"]; meta_i = m["meta_i"]

def px_metric(name):
    out = np.full(len(shapes), np.nan)
    for k in KEYS:
        idx = meta_k == k
        out[idx] = m[f"{k}_{name}"][meta_j[idx], meta_i[idx]]
    return out

G = px_metric("G_area"); SI = px_metric("Si_area")
sheet = (G > 3000) & (G < 6500) & (SI > 12000)      # uniform-thickness sheet
wedge = (G >= 6500)                                  # thick multilayer wedge
graphite = (G > 500) & (SI < 6000)                   # graphite chunk/sliver
edge = (G > 500) & ~sheet & ~wedge & ~graphite       # weak/edge graphene

norm = (shapes * dx).sum(1, keepdims=True)
S = shapes[sheet] / norm[sheet]
P = PCA(n_components=5).fit_transform(S)
km = KMeans(n_clusters=2, n_init=30, random_state=0).fit(P)
lab = km.labels_
# name clusters: 0 = lower 2D centroid (ABC-like), 1 = higher (ABA-like)
cents = [float(np.sum(shape_x * S[lab == c].mean(0) * dx) /
               np.sum(S[lab == c].mean(0) * dx)) for c in (0, 1)]
if cents[0] > cents[1]:
    lab = 1 - lab
stats = []

def lorN(x, p, n):
    y = np.zeros_like(x)
    for q in range(n):
        a, x0, w = p[3 * q:3 * q + 3]
        y += a / (1 + ((x - x0) / (w / 2)) ** 2)
    return y + p[-1]

def fit_lorN(x, y, guesses):
    n = len(guesses)
    p0 = []
    for x0 in guesses:
        p0 += [y.max() * 0.6, x0, 35.0]
    p0.append(0.0)
    lo = [0, x.min(), 8] * n + [-np.inf]
    hi = [np.inf, x.max(), 120] * n + [np.inf]
    r = least_squares(lambda p: lorN(x, p, n) - y, p0, bounds=(lo, hi))
    return r.x, np.sqrt(np.mean(r.fun ** 2))

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
colors = {0: "tab:blue", 1: "tab:orange"}
mean_shapes = {}
for c in (0, 1):
    ms = S[lab == c].mean(0)
    mean_shapes[c] = ms
    n003 = ((meta_k[sheet] == "003") & (lab == c)).sum()
    n005 = ((meta_k[sheet] == "005") & (lab == c)).sum()
    axes[0].plot(shape_x, ms, color=colors[c],
                 label=f"cluster {c} ({'ABC-like' if c==0 else 'ABA-like'}) "
                       f"n={(lab==c).sum()} (003:{n003}, 005:{n005})")
    p, resid = fit_lorN(shape_x, ms, [2650, 2685, 2705])
    comps = sorted([(p[3*q+1], p[3*q+2], p[3*q]) for q in range(3)])
    stats.append(f"cluster {c} 3-Lorentzian components (center, fwhm, amp): " +
                 "; ".join(f"({x0:.1f}, {w:.1f}, {a:.5f})" for x0, w, a in comps) +
                 f"  rms={resid:.6f}")
    for x0, w, a in comps:
        axes[0].plot(shape_x, a / (1 + ((shape_x - x0) / (w / 2)) ** 2),
                     color=colors[c], alpha=0.35, lw=0.8)
axes[0].legend(fontsize=8); axes[0].set_xlabel("Raman shift (1/cm)")
axes[0].set_title("mean 2D lineshapes (area-normalized) + components")
axes[1].plot(shape_x, mean_shapes[0] - mean_shapes[1], "k")
axes[1].axhline(0, color="gray", lw=0.5)
axes[1].set_title("difference: cluster0 - cluster1")
axes[1].set_xlabel("Raman shift (1/cm)")
fig.savefig("final_lineshapes.png", dpi=140, bbox_inches="tight")
plt.close(fig)

# per-cluster metric medians (verified same-calibration)
for c in (0, 1):
    sel_c = np.zeros(len(shapes), bool); sel_c[np.flatnonzero(sheet)[lab == c]] = True
    row = []
    for met in ["TD_center", "TD_fwhm", "TD_area", "G_center", "G_fwhm",
                "G_area", "Si_area", "TD_skew"]:
        row.append(f"{met}={np.nanmedian(px_metric(met)[sel_c]):.2f}")
    stats.append(f"cluster {c} medians: " + " ".join(row))
    for k in KEYS:
        idx = sel_c & (meta_k == k)
        if idx.sum() > 5:
            stats.append(f"  [{k} only, n={idx.sum()}] TD_center="
                         f"{np.nanmedian(px_metric('TD_center')[idx]):.2f} "
                         f"TD_fwhm={np.nanmedian(px_metric('TD_fwhm')[idx]):.2f} "
                         f"G_center={np.nanmedian(px_metric('G_center')[idx]):.2f}")

# tombstone-footprint composition pre vs post pickup
TB = dict(x0=-12047.5, x1=-12033, y0=1264, y1=1296.5)
WX = px_metric_x = np.full(len(shapes), np.nan); WY = np.full(len(shapes), np.nan)
for k in KEYS:
    idx = meta_k == k
    WX[idx] = d[f"wx_{k}"][meta_j[idx], meta_i[idx]]
    WY[idx] = d[f"wy_{k}"][meta_j[idx], meta_i[idx]]
in_tb = (WX > TB["x0"]) & (WX < TB["x1"]) & (WY > TB["y0"]) & (WY < TB["y1"])
for k in KEYS:
    idx = np.flatnonzero(sheet)
    kk = (meta_k[sheet] == k) & in_tb[sheet]
    if kk.sum():
        f0 = (lab[kk] == 0).mean()
        stats.append(f"tombstone footprint, map {k}: n={kk.sum()} sheet px, "
                     f"ABC-like fraction {f0:.2f}")

open("final_stats.txt", "w").write("\n".join(stats) + "\n")
print("\n".join(stats))

# ---------- region rasters ----------
STEP = 0.5
xg = np.arange(-12080, -12020 + STEP, STEP)
yg = np.arange(1262, 1306 + STEP, STEP)
XX, YY = np.meshgrid(xg, yg)

def rasterize(k, values):
    """Nearest-pixel raster of per-pixel integer labels of map k onto grid."""
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    out = np.zeros(XX.shape, np.uint8)
    # map grid points into pixel indices via inverse of the affine transform
    # (approximate: use nearest data pixel within step tolerance)
    from scipy.spatial import cKDTree
    tree = cKDTree(np.stack([wx.ravel(), wy.ravel()], 1))
    dist, idx = tree.query(np.stack([XX.ravel(), YY.ravel()], 1))
    ok = dist < 0.75  # within one map pixel
    out.ravel()[ok] = values.ravel()[idx[ok]]
    return out

labels = {}
for k in KEYS:
    v = np.zeros(d[f"wx_{k}"].shape, np.uint8)
    idx = meta_k == k
    kj, ki = meta_j[idx], meta_i[idx]
    v[kj[sheet[idx]], ki[sheet[idx]]] = 0  # placeholder
    # per-pixel classes
    cls = np.zeros(idx.sum(), np.uint8)
    cls[sheet[idx]] = 10  # sheet, cluster set below
    sheet_pos = np.flatnonzero(sheet)
    for c in (0, 1):
        sel_c = np.zeros(len(shapes), bool); sel_c[sheet_pos[lab == c]] = True
        cls[sel_c[idx]] = (1 if c == 0 else 2) if k == "003" else (5 if c == 0 else 6)
    cls[wedge[idx]] = 3
    cls[graphite[idx]] = 4
    cls[edge[idx]] = 7
    v[kj, ki] = cls
    labels[k] = rasterize(k, v)

key = {0: "background/unmapped", 1: "sheet ABC-like (pre-pickup)",
       2: "sheet ABA-like (pre-pickup)", 3: "thick multilayer wedge",
       4: "graphite", 5: "remnant ABC-like (post-pickup)",
       6: "remnant ABA-like (post-pickup)", 7: "graphene edge/unassigned"}
verdicts = {0: "n/a", 1: "ABC (strong)", 2: "ABA (strong)",
            3: "multilayer >3L, Bernal-like (consistent-with)",
            4: "graphite (decisive, not device-relevant)",
            5: "ABC (strong)", 6: "ABA (weak)",
            7: "uninformative (edge mixing)"}
np.savez_compressed(
    "regions.npz",
    x_um=xg, y_um=yg,
    labels_pre=labels["003"], labels_post=labels["005"],
    label_key=np.array([f"{i}: {key[i]} -> {verdicts[i]}" for i in key]),
    note=np.array(
        "Stage µm frame (WITec WorldOrigin coords). labels_pre = state during "
        "map 003 (2026-05-28 19:57 UTC, before pickup); labels_post = state "
        "during map 005 (20:20 UTC, after ~20:10-20:19 pickup removed most of "
        "the sheet). Scan-axis rotation vs stage (~0.5 deg) is included via "
        "per-pixel world coords."))

from matplotlib.colors import ListedColormap
cmap = ListedColormap(["#f0f0f0", "#1f77b4", "#ff7f0e", "#2ca02c",
                       "#000000", "#17becf", "#ffbb78", "#c7c7c7"])
fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), sharex=True, sharey=True)
for ax, (nm, L) in zip(axes, [("pre-pickup (map 003 state)", labels["003"]),
                              ("post-pickup (map 005 state)", labels["005"])]):
    ax.pcolormesh(XX, YY, L, cmap=cmap, vmin=-0.5, vmax=7.5, shading="nearest")
    ax.set_aspect("equal"); ax.set_title(nm)
    ax.set_xlabel("stage x (µm)")
axes[0].set_ylabel("stage y (µm)")
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color=cmap(i), label=f"{i}: {key[i]}") for i in key]
axes[1].legend(handles=handles, fontsize=7, loc="center left",
               bbox_to_anchor=(1.02, 0.5))
fig.savefig("regions.png", dpi=140, bbox_inches="tight")
print("wrote regions.npz / regions.png")
