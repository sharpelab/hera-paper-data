#!/usr/bin/env python3
"""Step 1 — in-map layer-count proxies (no external thickness map supplied).

Per pixel, for maps 22 and 27: integrated areas of Si 520, G, 2D, D bands above
a linear baseline; G/Si and 2D/G ratios. Histograms of G area and Si area over
flake pixels expose thickness populations (a terrace = a step in G and an
opposite step in Si). Flake mask = G area above the substrate mode.

Writes intermediates/proxies_<k>.npz, figures/f1_proxies_<k>.png, f1_histograms.png.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s1_layer_proxies.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import FIG, INT, band_area, load_map, show

WINDOWS = dict(si=(503, 538), d=(1320, 1385), g=(1545, 1625), twod=(2580, 2810), si2=(930, 1010))

fig_h, axh = plt.subplots(2, 3, figsize=(16, 8))
for row, k in enumerate((22, 27)):
    m = load_map(k)
    wn, ii = m["wn"], m["ii"]
    areas = {n: band_area(wn, ii, *w) for n, w in WINDOWS.items()}
    g_si = areas["g"] / areas["si"]
    td_g = areas["twod"] / np.where(areas["g"] > 0, areas["g"], np.nan)
    # substrate vs flake: G area histogram, threshold at the valley after the substrate mode
    g = areas["g"]
    hist, edges = np.histogram(g, bins=80)
    ctr = 0.5 * (edges[1:] + edges[:-1])
    sub_mode = ctr[np.argmax(hist)]
    # valley search beyond the substrate mode
    after = ctr > sub_mode
    i_val = np.argmin(hist[after][: max(3, int(after.sum() * 0.5))])
    thr = ctr[after][i_val]
    flake = g > thr
    np.savez_compressed(INT / f"proxies_{k}.npz", **areas, g_si=g_si, td_g=td_g, flake=flake, g_thr=thr)
    print(f"[{k}] substrate G-area mode {sub_mode:.0f}, flake threshold {thr:.0f}, "
          f"flake px {flake.sum()}/{flake.size}")
    fg = g[flake]; fsi = areas["si"][flake]; ftd = td_g[flake]
    print(f"     flake G area: p5/p50/p95 = {np.percentile(fg,[5,50,95]).round(0)}; "
          f"Si area p5/p50/p95 = {np.percentile(fsi,[5,50,95]).round(0)}; substrate Si p50 {np.median(areas['si'][~flake]):.0f}")
    print(f"     flake 2D/G area ratio p5/p50/p95 = {np.nanpercentile(ftd,[5,50,95]).round(2)}")

    fig, axes = plt.subplots(2, 3, figsize=(17, 9 if k == 22 else 12))
    for ax, (name, vec, cm) in zip(axes.ravel(), (
            ("G area (counts·cm⁻¹)", areas["g"], "magma"), ("Si 520 area", areas["si"], "viridis"),
            ("2D area", areas["twod"], "magma"), ("2D/G area ratio", np.where(flake, td_g, np.nan), "cividis"),
            ("G/Si", g_si, "magma"), ("D area", areas["d"], "magma"))):
        lo, hi = np.nanpercentile(vec, [1, 99])
        im = show(ax, vec, m, cmap=cm, vmin=lo, vmax=hi)
        ax.set_title(name); fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    fig.suptitle(f"[{k}] {m['caption']} — layer-count proxies (stage frame)")
    fig.tight_layout(); fig.savefig(FIG / f"f1_proxies_{k}.png", dpi=120); plt.close(fig)

    axh[row, 0].hist(g, bins=80, color="C0"); axh[row, 0].axvline(thr, color="k", ls="--")
    axh[row, 0].set_title(f"[{k}] G area, all px (thr {thr:.0f})"); axh[row, 0].set_yscale("log")
    axh[row, 1].hist(fg, bins=60, color="C1"); axh[row, 1].set_title(f"[{k}] G area, flake px")
    axh[row, 2].hist(fsi, bins=60, color="C2"); axh[row, 2].axvline(np.median(areas["si"][~flake]), color="k", ls="--")
    axh[row, 2].set_title(f"[{k}] Si area, flake px (dashed: substrate median)")
fig_h.tight_layout(); fig_h.savefig(FIG / "f1_histograms.png", dpi=120)
