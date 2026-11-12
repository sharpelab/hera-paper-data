"""Per-pixel metrics + segmentation on both scans + Spot1. Saves npz.
Local per-pixel loop = map_tools.per_pixel_metrics gates + finite-pixel screen
(Scan002 is a partial map with all-NaN unacquired columns)."""
import sys
import numpy as np
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/.worktrees/raman_stacking_lit/hera/models/raman_stacking")
from raman_io import load_wip
from metrics import metrics_2d, metrics_g, fit_band
from map_tools import two_population_split, METRIC_KEYS

WIP = "/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip"
OUT = "/tmp/qc0426-raman-read"

ds = {d["caption"]: d for d in load_wip(WIP)}

# ---- Spot1
sp = ds["Spot1--Spec.Data 1"]
wn, y = sp["wn"], sp["ii"][:, 0]
m2 = metrics_2d(wn, y)
mg = metrics_g(wn, y)
print("Spot1 2D:", {k: round(v, 3) for k, v in m2.items()} if m2 else "NO 2D BAND")
print("Spot1 G :", {k: round(v, 3) for k, v in mg.items()} if mg else "NO G BAND")
np.savez(f"{OUT}/spot1.npz", wn=wn, ii=y)

# ---- Maps
for cap, tag in [("Scan LA--002--Spec.Data 1", "scan002"),
                 ("Scan LA--004--Spec.Data 1", "scan004")]:
    d = ds[cap]
    wn, ii, nx, ny = d["wn"], d["ii"], d["nx"], d["ny"]
    n = nx * ny
    acquired = np.isfinite(ii).all(axis=0)
    mm = {k: np.full(n, np.nan) for k in METRIC_KEYS}
    for j in range(n):
        if not acquired[j]:
            continue
        yj = ii[:, j]
        noise = np.median(np.abs(np.diff(yj))) + 1e-12
        m = metrics_2d(wn, yj)
        if m is None or m["amp"] < 8.0 * noise:
            continue
        if not (15.0 < m["fwhm"] < 200.0) or m["r2"] < 0.4:
            continue
        for k in METRIC_KEYS:
            mm[k][j] = m[k]
    n_ok = np.isfinite(mm["fwhm"]).sum()
    print(f"\n{tag}: {nx}x{ny}, acquired {acquired.sum()}, credible 2D band {n_ok}")
    labels, centers = two_population_split(mm["fwhm"])
    n0, n1 = (labels == 0).sum(), (labels == 1).sum()
    print(f"  FWHM 2-pop split: {centers[0]:.1f} ({n0} px) / {centers[1]:.1f} ({n1} px), delta {centers[1]-centers[0]:.1f}")
    v = mm["fwhm"][np.isfinite(mm["fwhm"])]
    print(f"  FWHM percentiles 5/25/50/75/95: " +
          " ".join(f"{np.percentile(v,p):.1f}" for p in (5, 25, 50, 75, 95)))
    c = mm["center"][np.isfinite(mm["center"])]
    print(f"  2D center percentiles 5/50/95: " +
          " ".join(f"{np.percentile(c,p):.1f}" for p in (5, 50, 95)))
    # G-band per pixel
    gpos = np.full(n, np.nan); gfw = np.full(n, np.nan)
    gamp = np.full(n, np.nan); gr2 = np.full(n, np.nan)
    for j in range(n):
        if not acquired[j]:
            continue
        g = fit_band(wn, ii[:, j], (1500.0, 1650.0), fit_half=60.0)
        if g is None:
            continue
        noise = np.median(np.abs(np.diff(ii[:, j]))) + 1e-12
        if g["amp"] < 8.0 * noise or not (5 < g["fwhm"] < 80) or g["r2"] < 0.4:
            continue
        gpos[j], gfw[j], gamp[j], gr2[j] = g["center"], g["fwhm"], g["amp"], g["r2"]
    print(f"  G-band pixels: {np.isfinite(gfw).sum()}; "
          f"pos med {np.nanmedian(gpos):.1f}, FWHM med {np.nanmedian(gfw):.1f}")
    np.savez(f"{OUT}/{tag}_metrics.npz", nx=nx, ny=ny, labels=labels,
             centers=np.array(centers), acquired=acquired,
             g_pos=gpos, g_fwhm=gfw, g_amp=gamp, g_r2=gr2,
             **{f"m_{k}": v for k, v in mm.items()})
print("\ndone")
