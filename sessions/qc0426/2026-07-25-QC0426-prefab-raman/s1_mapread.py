import sys
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/hera/models/raman_stacking")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from raman_io import load_wip
from map_tools import per_pixel_metrics, two_population_split, to_image
import witio

OUT = "."  # figures land in cwd
ROOT = "/data/sharpelab/hera-data/raman-qc0426"

for tag, fname, mapname in (("04", "04_3LGr.wip", "Scan LA--009--Spec.Data 1"),
                            ("05", "05_3LGr-stack.wip", "Scan LA--007--Spec.Data 1")):
    ds = {d["caption"]: d for d in load_wip(f"{ROOT}/{fname}")}
    d = ds[mapname]
    wn, ii, nx, ny = d["wn"], d["ii"], d["nx"], d["ny"]
    pm = per_pixel_metrics(wn, ii)
    fw = pm["fwhm"]; ok = np.isfinite(fw)
    # restrict to thick (trilayer-candidate) population: drop thin-region pixels
    thick = ok & (fw > 45)
    labels, centers = two_population_split(np.where(thick, fw, np.nan))
    n0, n1 = (labels==0).sum(), (labels==1).sum()
    print(f"{tag} thick-only split: lo {centers[0]:.1f} (n={n0}) hi {centers[1]:.1f} (n={n1}) sep {centers[1]-centers[0]:.1f}")
    for k in (0,1):
        sel = labels==k
        print(f"   c{k}: fwhm {np.nanmean(fw[sel]):.1f}±{np.nanstd(fw[sel]):.1f} center {np.nanmean(pm['center'][sel]):.1f}±{np.nanstd(pm['center'][sel]):.1f} skew {np.nanmean(pm['skew'][sel]):.2f} ratio {np.nanmean(pm['ratio_lh'][sel]):.2f}")
    fig, ax = plt.subplots(1, 3, figsize=(17,4.5))
    img = to_image(np.where(thick, fw, np.nan), nx, ny)
    im = ax[0].imshow(img, origin="lower", cmap="viridis", vmin=45, vmax=max(75, np.nanpercentile(img,99)))
    plt.colorbar(im, ax=ax[0], shrink=0.8); ax[0].set_title(f"{tag}: 2D FWHM, thick region")
    imgl = to_image(labels.astype(float), nx, ny); imgl[imgl<0]=np.nan
    ax[1].imshow(imgl, origin="lower", cmap="coolwarm"); ax[1].set_title(f"{tag}: split hi=red")
    ax[2].hist(fw[thick], bins=50); ax[2].axvline(centers[0], color='b'); ax[2].axvline(centers[1], color='r')
    ax[2].set_title("thick-region FWHM hist")
    fig.savefig(f"{OUT}/map_{tag}_thick.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    # video image: exact caption
    p = witio.read(f"{ROOT}/{fname}")
    for it in p.data:
        if it.caption == "Video Image--000":
            arr = np.asarray(it.array())
            plt.figure(figsize=(9,7)); plt.imshow(arr); plt.title(f"{tag}: Video Image--000")
            plt.savefig(f"{OUT}/video_{tag}.png", dpi=110, bbox_inches="tight"); plt.close()
    # spot 2D lineshape overlay (04 only has spot pairs at both stages)
    fig, ax = plt.subplots(figsize=(7,4.5))
    for cap in ds:
        if d is None: pass
    caps = [c for c in ds if "2D" in c and ds[c]["nx"]==1]
    for cap in caps:
        s = ds[cap]; sel = (s["wn"]>2550)&(s["wn"]<2850)
        y = s["ii"][sel,0]; y = (y-y.min())/(y.max()-y.min()+1e-9)
        ax.plot(s["wn"][sel], y, label=cap.split("--")[0])
    ax.legend(); ax.set_xlabel("Raman shift (cm-1)"); ax.set_title(f"{tag}: normalized 2D lineshapes")
    fig.savefig(f"{OUT}/spots_{tag}_2d.png", dpi=110, bbox_inches="tight"); plt.close(fig)
print("done")
