#!/usr/bin/env python3
"""Step 2 — per-pixel 2D-band metrics with the tool (`map_tools.per_pixel_metrics`:
single-Lorentzian FWHM, centre, amp, r², skew, low/high ratio, with its junk-fit
rejection) plus G-band position/FWHM (`metrics.metrics_g`) for maps 22 and 27.

Writes intermediates/metrics_<k>.npz and figures/f2_metrics_<k>.png.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s2_metrics.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import FIG, INT, load_map, show
from map_tools import METRIC_KEYS, per_pixel_metrics
from metrics import metrics_g

for k in (22, 27):
    m = load_map(k)
    wn, ii = m["wn"], m["ii"]
    px = per_pixel_metrics(wn, ii)
    g_pos = np.full(ii.shape[1], np.nan); g_fw = np.full(ii.shape[1], np.nan); g_r2 = np.full(ii.shape[1], np.nan)
    for j in range(ii.shape[1]):
        if not np.isfinite(px["fwhm"][j]):
            continue
        gg = metrics_g(wn, ii[:, j])
        if gg and 5 < gg["fwhm"] < 60:
            g_pos[j], g_fw[j], g_r2[j] = gg["center"], gg["fwhm"], gg["r2"]
    np.savez_compressed(INT / f"metrics_{k}.npz", **px, g_center=g_pos, g_fwhm=g_fw, g_r2=g_r2)
    ok = np.isfinite(px["fwhm"])
    print(f"[{k}] {ok.sum()}/{ok.size} px with a credible 2D band; "
          f"FWHM p5/p50/p95 = {np.percentile(px['fwhm'][ok],[5,50,95]).round(1)}; "
          f"centre p50 {np.median(px['center'][ok]):.1f}; r2 p50 {np.median(px['r2'][ok]):.3f}; "
          f"amp p50 {np.median(px['amp'][ok]):.0f}; G FWHM p50 {np.nanmedian(g_fw):.1f}; G pos p50 {np.nanmedian(g_pos):.1f}")
    fig, axes = plt.subplots(2, 4, figsize=(21, 9 if k == 22 else 12))
    panels = (("2D FWHM (cm⁻¹)", px["fwhm"], "viridis"), ("2D centre (cm⁻¹)", px["center"], "coolwarm"),
              ("2D fit r²", px["r2"], "magma"), ("2D amplitude (counts)", px["amp"], "magma"),
              ("2D skew", px["skew"], "coolwarm"), ("2D low/high ratio", px["ratio_lh"], "coolwarm"),
              ("G FWHM (cm⁻¹)", g_fw, "viridis"), ("G centre (cm⁻¹)", g_pos, "coolwarm"))
    for ax, (name, vec, cm) in zip(axes.ravel(), panels):
        lo, hi = np.nanpercentile(vec, [2, 98])
        im = show(ax, vec, m, cmap=cm, vmin=lo, vmax=hi)
        ax.set_title(name); fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    fig.suptitle(f"[{k}] {m['caption']} — per-pixel 2D/G metrics (stage frame)")
    fig.tight_layout(); fig.savefig(FIG / f"f2_metrics_{k}.png", dpi=120); plt.close(fig)
