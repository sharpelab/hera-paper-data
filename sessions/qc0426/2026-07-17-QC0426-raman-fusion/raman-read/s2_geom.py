"""Exact stage coords per pixel; morphology; overlap cross-check; figures."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import witio

OUT = "/tmp/qc0426-raman-read"
WIP = "/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip"

p = witio.read(WIP)
pg = {}
for d in p.data:
    if d.caption in ("Scan LA--002--Spec.Data 1", "Scan LA--004--Spec.Data 1"):
        g = d.position_grid
        g = g() if callable(g) else g
        pg[d.caption] = np.asarray(g)

def load(tag, cap, n):
    z = np.load(f"{OUT}/{tag}_metrics.npz")
    g = pg[cap]                       # (2, n, n): x = g[0,a,b], y = g[1,a,b]
    X, Y = g[0], g[1]
    def im(vec):                      # vec[j], j = a*n + b -> arr[a, b]
        return np.asarray(vec).reshape(n, n)
    return z, X, Y, im

z2, X2, Y2, im2 = load("scan002", "Scan LA--002--Spec.Data 1", 61)
z4, X4, Y4, im4 = load("scan004", "Scan LA--004--Spec.Data 1", 51)

for tag, z, X, Y in [("scan002", z2, X2, Y2), ("scan004", z4, X4, Y4)]:
    print(f"{tag}: x range {X.min():.2f}..{X.max():.2f}, y range {Y.min():.2f}..{Y.max():.2f}")

# ---- ASCII morphology: FWHM cluster labels in (a,b) frame with coords noted
for tag, z, X, Y, n in [("scan002", z2, X2, Y2, 61), ("scan004", z4, X4, Y4, 51)]:
    lab = z["labels"].reshape(n, n)
    fw = z["m_fwhm"].reshape(n, n)
    print(f"\n==== {tag} label map (rows=a: x {X[0,0]:.1f}->{X[-1,0]:.1f}; "
          f"cols=b: y {Y[0,0]:.1f}->{Y[0,-1]:.1f}), .=no2D, 0=low 1=high")
    for a in range(n):
        print("".join(".01"[int(v)+1] if v >= -1 else "?" for v in lab[a]))

# ---- overlap cross-check: nearest scan004 pixel for each credible scan002 pixel
from scipy.spatial import cKDTree
ok2 = np.isfinite(z2["m_fwhm"])
ok4 = np.isfinite(z4["m_fwhm"])
pts4 = np.c_[X4.ravel()[ok4], Y4.ravel()[ok4]]
tree = cKDTree(pts4)
pts2 = np.c_[X2.ravel()[ok2], Y2.ravel()[ok2]]
dd, jj = tree.query(pts2)
near = dd < 0.45
f2 = z2["m_fwhm"][ok2][near]
f4 = z4["m_fwhm"][ok4][jj[near]]
print(f"\noverlap pairs (<0.45 um): {near.sum()}")
if near.sum() > 5:
    print(f"  FWHM scan002 med {np.median(f2):.1f}  scan004 med {np.median(f4):.1f}  "
          f"median diff {np.median(f4-f2):+.1f}  corr r {np.corrcoef(f2, f4)[0,1]:.2f}")
    c2 = z2["m_center"][ok2][near]; c4 = z4["m_center"][ok4][jj[near]]
    print(f"  2Dpos scan002 med {np.median(c2):.1f}  scan004 med {np.median(c4):.1f}  "
          f"median diff {np.median(c4-c2):+.1f}")

# ---- strain screen numbers: FWHM vs 2D center correlation within each map
for tag, z in [("scan002", z2), ("scan004", z4)]:
    ok = np.isfinite(z["m_fwhm"])
    fw, ce = z["m_fwhm"][ok], z["m_center"][ok]
    r = np.corrcoef(fw, ce)[0, 1]
    print(f"{tag}: corr(FWHM, 2Dcenter) = {r:+.2f} over {ok.sum()} px; "
          f"center std {ce.std():.2f} cm-1")
    # G-band cross-tabs by cluster
    lab = z["labels"]
    for k in (0, 1):
        sel = (lab == k)
        gf = z["g_fwhm"][sel]; gp = z["g_pos"][sel]
        ga = z["g_amp"][sel]; a2 = z["m_amp"][sel]
        print(f"   cluster {k}: n={sel.sum()}  G-FWHM med {np.nanmedian(gf):.1f}  "
              f"G-pos med {np.nanmedian(gp):.1f}  G-amp med {np.nanmedian(ga):.0f}  "
              f"2D-amp med {np.nanmedian(a2):.0f}  2Dpos med {np.nanmedian(z['m_center'][sel]):.1f}")

# ---- figures: metric maps in stage frame
def stagemaps(tag, z, X, Y, n):
    fig, axs = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    panels = [("m_fwhm", "2D FWHM (cm$^{-1}$)", (52, 72), "viridis"),
              ("m_center", "2D center (cm$^{-1}$)", (2698, 2710), "coolwarm"),
              ("m_amp", "2D amplitude (cts)", None, "magma"),
              ("g_fwhm", "G FWHM (cm$^{-1}$)", (8, 25), "viridis"),
              ("g_pos", "G position (cm$^{-1}$)", (1574, 1584), "coolwarm"),
              ("g_amp", "G amplitude (cts)", None, "magma")]
    for ax, (k, ttl, clim, cmap) in zip(axs.ravel(), panels):
        M = z[k].reshape(n, n)
        pc = ax.pcolormesh(X, Y, M, shading="nearest", cmap=cmap)
        if clim: pc.set_clim(*clim)
        fig.colorbar(pc, ax=ax, shrink=0.8)
        ax.set_title(ttl); ax.set_aspect("equal")
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    fig.suptitle(f"QC0426 {tag} — 532.34 nm, stage frame")
    fig.savefig(f"{OUT}/{tag}_metric_maps.png", dpi=130)
    plt.close(fig)

stagemaps("scan002", z2, X2, Y2, 61)
stagemaps("scan004", z4, X4, Y4, 51)

# ---- FWHM histograms
fig, axs = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
for ax, (tag, z) in zip(axs, [("scan002", z2), ("scan004", z4)]):
    v = z["m_fwhm"][np.isfinite(z["m_fwhm"])]
    ax.hist(v, bins=np.arange(48, 80, 0.75), color="#46688e")
    for c in z["centers"]:
        ax.axvline(c, color="crimson", ls="--")
    ax.set_title(f"{tag}  (2-means: {z['centers'][0]:.1f} / {z['centers'][1]:.1f})")
    ax.set_xlabel("2D FWHM (cm$^{-1}$)"); ax.set_ylabel("pixels")
fig.savefig(f"{OUT}/fwhm_histograms.png", dpi=130)
plt.close(fig)

# segmentation maps
fig, axs = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
for ax, (tag, z, X, Y, n) in zip(axs, [("scan002", z2, X2, Y2, 61),
                                       ("scan004", z4, X4, Y4, 51)]):
    lab = z["labels"].astype(float).copy()
    lab[lab < 0] = np.nan
    pc = ax.pcolormesh(X, Y, lab.reshape(n, n), shading="nearest",
                       cmap="coolwarm", vmin=0, vmax=1)
    ax.set_title(f"{tag} FWHM 2-means (0=low blue, 1=high red)")
    ax.set_aspect("equal"); ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
fig.savefig(f"{OUT}/segmentation_maps.png", dpi=130)
plt.close(fig)
print("\nfigures written")
