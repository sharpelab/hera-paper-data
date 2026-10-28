#!/usr/bin/env python3
"""Step 2/3 — per-pixel metrics for maps A (Scan 003) and B (Scan 005):
2D metrics (tool), G metrics, Si-520 amplitude (terrace proxy), raw-count
ceiling (saturation check). Saves map_metrics.npz + overview figures."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "tools"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from raman_io import load_wip
from metrics import fit_band, metrics_g
from map_tools import per_pixel_metrics, to_image, METRIC_KEYS

dsets = load_wip(HERE / "inputs" / "vti-01.wip")
maps = {d["caption"]: d for d in dsets}
A = maps["73474_--Scan LA--003--Spec.Data 1"]
B = maps["73474_--Scan LA--005--Spec.Data 1"]

out = {}
for tag, d in (("A", A), ("B", B)):
    wn, ii, nx, ny = d["wn"], d["ii"], d["nx"], d["ny"]
    meta = d["meta"]
    print(f"map {tag}: {nx}x{ny}, center ({meta['scan_center_x_um']:.1f}, "
          f"{meta['scan_center_y_um']:.1f}), span {meta['scan_span_x_um']}x"
          f"{meta['scan_span_y_um']} µm")
    px = per_pixel_metrics(wn, ii)
    n = ii.shape[1]
    g_center = np.full(n, np.nan); g_fwhm = np.full(n, np.nan)
    g_amp = np.full(n, np.nan); si_amp = np.full(n, np.nan)
    raw_max = np.full(n, np.nan)
    for j in range(n):
        y = ii[:, j]
        raw_max[j] = np.nanmax(y)
        g = metrics_g(wn, y)
        if g is not None:
            g_center[j], g_fwhm[j] = g["center"], g["fwhm"]
        gf = fit_band(wn, y, (1500.0, 1650.0), fit_half=60.0)
        if gf is not None:
            g_amp[j] = gf["amp"]
        sf = fit_band(wn, y, (490.0, 550.0), fit_half=40.0)
        if sf is not None and 500 < sf["center"] < 540:
            si_amp[j] = sf["amp"]
    out[tag] = dict(px=px, g_center=g_center, g_fwhm=g_fwhm, g_amp=g_amp,
                    si_amp=si_amp, raw_max=raw_max, nx=nx, ny=ny,
                    cx=meta["scan_center_x_um"], cy=meta["scan_center_y_um"],
                    step=meta["scan_span_x_um"] / nx)
    print(f"  graphene px (2D ok): {np.isfinite(px['fwhm']).sum()}/{n}")
    print(f"  raw counts max over map: {np.nanmax(raw_max):.0f} "
          f"(16-bit ceiling 65535); Si amp range "
          f"{np.nanmin(si_amp):.0f}..{np.nanmax(si_amp):.0f}")

np.savez(HERE / "map_metrics.npz",
         **{f"{t}_{k}": v[k] if False else v[k]
            for t, v in out.items() for k in
            ("g_center", "g_fwhm", "g_amp", "si_amp", "raw_max")},
         **{f"{t}_px_{k}": out[t]["px"][k] for t in out for k in METRIC_KEYS},
         A_geom=np.array([out["A"]["cx"], out["A"]["cy"], out["A"]["nx"],
                          out["A"]["ny"], out["A"]["step"]]),
         B_geom=np.array([out["B"]["cx"], out["B"]["cy"], out["B"]["nx"],
                          out["B"]["ny"], out["B"]["step"]]))
print("wrote map_metrics.npz")


def extent(v):
    hx = v["nx"] * v["step"] / 2; hy = v["ny"] * v["step"] / 2
    return [v["cx"] - hx, v["cx"] + hx, v["cy"] - hy, v["cy"] + hy]


for tag, v in out.items():
    nx, ny = v["nx"], v["ny"]
    ext = extent(v)
    fig, axes = plt.subplots(2, 4, figsize=(20, 8))
    panels = [("2D FWHM", v["px"]["fwhm"], "viridis"),
              ("2D center", v["px"]["center"], "coolwarm"),
              ("2D amp", v["px"]["amp"], "magma"),
              ("2D fit r2", v["px"]["r2"], "cividis"),
              ("G center", v["g_center"], "coolwarm"),
              ("G FWHM", v["g_fwhm"], "viridis"),
              ("G amp", v["g_amp"], "magma"),
              ("Si-520 amp", v["si_amp"], "gray")]
    for ax, (title, vec, cmap) in zip(axes.ravel(), panels):
        img = to_image(vec, nx, ny)
        im = ax.imshow(img, extent=ext, origin="upper", cmap=cmap)
        ax.set_title(f"{tag}: {title}")
        fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(HERE / f"fig_map{tag}_metrics.png", dpi=120)
    print(f"wrote fig_map{tag}_metrics.png")

# histograms of 2D FWHM
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, (tag, v) in zip(axes, out.items()):
    f = v["px"]["fwhm"]
    ax.hist(f[np.isfinite(f)], bins=60)
    ax.set_title(f"map {tag}: 2D FWHM histogram")
    ax.set_xlabel("FWHM (cm$^{-1}$)")
fig.tight_layout()
fig.savefig(HERE / "fig_fwhm_hist.png", dpi=120)
print("wrote fig_fwhm_hist.png")
