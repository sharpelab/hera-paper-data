#!/usr/bin/env python3
"""s5_stacking.py — 2D-band lineshape clustering (the stacking discriminator).

K-means on area-normalized, baseline-subtracted 2D lineshapes (2570-2830 1/cm)
over graphene pixels of maps 003+005; cluster label maps in the stage frame;
cluster mean lineshapes + full-range mean spectra + per-cluster metric stats.

Run: uv run --with numpy --with scipy --with scikit-learn --with matplotlib python s5_stacking.py
Outputs: clusters_k{2,3,4}.png, cluster_shapes.png, cluster_stats.txt
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
KEYS = ["003", "005"]
G_THRESH = 2000  # from bimodal G_area histogram (substrate ~0, sheet ~4400-5000)

shape_x = m["shape_x"]
shapes = m["shapes"].astype(float)
meta_k = m["meta_k"]; meta_j = m["meta_j"]; meta_i = m["meta_i"]

# graphene selection + exclude pixels whose G is huge (thick graphite) handled later
sel = np.zeros(len(shapes), bool)
garea = np.full(len(shapes), np.nan)
for k in KEYS:
    G = m[f"{k}_G_area"]
    idx = meta_k == k
    garea[idx] = G[meta_j[idx], meta_i[idx]]
sel = garea > G_THRESH
print("selected graphene px:", sel.sum())

dx = np.abs(np.gradient(shape_x))
norm = (shapes * dx).sum(1, keepdims=True)
S = shapes[sel] / norm[sel]
pca = PCA(n_components=8).fit(S)
print("PCA explained variance:", np.round(pca.explained_variance_ratio_[:6], 4))
P = pca.transform(S)

stats_lines = []
for K in (2, 3, 4):
    km = KMeans(n_clusters=K, n_init=20, random_state=0).fit(P[:, :5])
    lab = km.labels_
    # order clusters by mean 2D centroid for stable naming
    cent = []
    for c in range(K):
        mean_shape = S[lab == c].mean(0)
        cent.append(np.sum(shape_x * mean_shape * dx) / np.sum(mean_shape * dx))
    order = np.argsort(cent)
    relab = np.zeros_like(lab)
    for newc, oldc in enumerate(order):
        relab[lab == oldc] = newc
    lab = relab

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    cmap = plt.get_cmap("tab10")
    for ax, k in zip(axes[:2], KEYS):
        wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
        img = np.full(wx.shape, np.nan)
        idx = (meta_k == k) & sel
        img[meta_j[idx], meta_i[idx]] = lab[np.searchsorted(
            np.flatnonzero(sel), np.flatnonzero(idx))]
        im = ax.pcolormesh(wx, wy, img, shading="nearest", cmap="tab10",
                           vmin=-0.5, vmax=9.5)
        ax.set_aspect("equal"); ax.set_title(f"map {k}, K={K}")
    for c in range(K):
        ms = S[lab == c].mean(0)
        axes[2].plot(shape_x, ms, color=cmap(c), label=f"cluster {c} (n={(lab==c).sum()})")
    axes[2].legend(); axes[2].set_xlabel("Raman shift (1/cm)")
    axes[2].set_title("normalized mean 2D lineshapes")
    fig.savefig(f"clusters_k{K}.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    stats_lines.append(f"== K={K} ==")
    for c in range(K):
        idx_c = np.flatnonzero(sel)[lab == c]
        row = {}
        for met in ["G_area", "Si_area", "TD_center", "TD_fwhm", "TD_skew",
                    "G_center", "G_fwhm", "D_area", "TD_area"]:
            vals = []
            for k in KEYS:
                kk = idx_c[meta_k[idx_c] == k]
                if len(kk):
                    vals.append(m[f"{k}_{met}"][meta_j[kk], meta_i[kk]])
            v = np.concatenate(vals)
            row[met] = (np.nanmedian(v), np.nanstd(v))
        n003 = (meta_k[idx_c] == "003").sum(); n005 = (meta_k[idx_c] == "005").sum()
        stats_lines.append(
            f"cluster {c}: n={len(idx_c)} (003:{n003}, 005:{n005}) " +
            " ".join(f"{met}={mu:.1f}±{sd:.1f}" for met, (mu, sd) in row.items()))

open("cluster_stats.txt", "w").write("\n".join(stats_lines) + "\n")
print("\n".join(stats_lines))

# save K=2 and K=3 labels for later region building
for K in (2, 3, 4):
    km = KMeans(n_clusters=K, n_init=20, random_state=0).fit(P[:, :5])
    lab = km.labels_
    cent = []
    for c in range(K):
        mean_shape = S[lab == c].mean(0)
        cent.append(np.sum(shape_x * mean_shape * dx) / np.sum(mean_shape * dx))
    order = np.argsort(cent)
    relab = np.zeros_like(lab)
    for newc, oldc in enumerate(order):
        relab[lab == oldc] = newc
    np.save(f"labels_k{K}.npy", relab)
np.save("labels_sel.npy", sel)
