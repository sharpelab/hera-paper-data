#!/usr/bin/env python3
"""
vti-01 Raman x transport fusion -- Step 2 registration artifact.

Frame bridges actually available:
  * in-file stage-registered video images (items 19/24/32 of vti-01.wip)
  * Raman region raster (inputs/regions.npz, WITec stage um frame)
  * device card contact map (topology only: T_SD/B_SD ends, L1-L4 left, R1-R2 right)
  * ana notebook geometry: gate-stack thicknesses only -- no Hall-bar dimensions
No GDS, no post-fab optical image, no build-step testimony.

Produces: registration.png, registration.json, registration.md
Run from the run dir:
  uv run --no-project --with numpy --with scipy --with matplotlib --with witio python registration.py
"""
import json
from pathlib import Path

import numpy as np
import witio
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle

RUN = Path(__file__).resolve().parent
WIP = Path("/data/sharpelab/hera-data/raman-vti-01/vti-01.wip")
Z = np.load(RUN / "inputs" / "regions.npz", allow_pickle=True)

LAB_A, LAB_B, LAB_MIX = 10, 11, 12
CLASSIFIED = (LAB_A, LAB_B, LAB_MIX)

xe, ye = Z["x_edges"], Z["y_edges"]
xc, yc = Z["x_centres"], Z["y_centres"]
rect = json.loads(str(Z["device_rect"]))
cuts = json.loads(str(Z["cut_footprints"]))
maps = json.loads(str(Z["map_footprints"]))
stage_stamps = json.loads(str(Z["stage_stamps"]))
labels = {
    "S0": Z["labels_S0_smooth"],
    "S1": Z["labels_S1_smooth"],
    "fused": Z["labels_fused_smooth"],
}
RX, RY = rect["x"], rect["y"]


# ---------------------------------------------------------------- helpers
def in_rect(x0, x1, y0, y1):
    """Boolean pixel mask of pixels whose centre lies in [x0,x1]x[y0,y1]."""
    mx = (xc >= x0) & (xc <= x1)
    my = (yc >= y0) & (yc <= y1)
    return my[:, None] & mx[None, :]


def composition(lab, mask):
    vals, cnt = np.unique(lab[mask], return_counts=True)
    d = {int(v): int(c) for v, c in zip(vals, cnt)}
    n_cls = sum(d.get(k, 0) for k in CLASSIFIED)
    out = {"n_px": int(mask.sum()), "counts": d, "n_classified": n_cls}
    for name, k in (("A", LAB_A), ("B", LAB_B), ("mixed", LAB_MIX)):
        out[f"share_{name}"] = (d.get(k, 0) / n_cls) if n_cls else float("nan")
    out["share_unclassified_of_all"] = 1 - n_cls / mask.sum() if mask.sum() else float("nan")
    return out


def window_sweep(lab, w, h, x0, x1, y0, y1, step=1.0):
    """Slide a w x h um window over all positions fully inside [x0,x1]x[y0,y1]."""
    res = []
    xs = np.arange(x0, x1 - w + 1e-9, step)
    ys = np.arange(y0, y1 - h + 1e-9, step)
    for ax in xs:
        for ay in ys:
            m = in_rect(ax, ax + w, ay, ay + h)
            c = composition(lab, m)
            if c["n_classified"] >= max(2, 0.5 * c["n_px"]):
                res.append((ax, ay, c["share_B"], c["share_A"], c["share_mixed"], c["n_classified"]))
    if not res:
        return None
    arr = np.array(res)
    return {
        "window_um": [w, h],
        "n_placements": int(len(arr)),
        "share_B_min": float(arr[:, 2].min()),
        "share_B_median": float(np.median(arr[:, 2])),
        "share_A_max": float(arr[:, 3].max()),
        "share_A_max_at": [float(arr[arr[:, 3].argmax(), 0]), float(arr[arr[:, 3].argmax(), 1])],
        "share_mixed_max": float(arr[:, 4].max()),
    }


def nearest_label_distance(lab, target, mask_from):
    """Min centre-to-centre distance (um) from any pixel in mask_from to any pixel == target."""
    tgt = lab == target
    if not tgt.any():
        return float("inf")
    yy, xx = np.meshgrid(yc, xc, indexing="ij")
    ty, tx = yy[tgt], xx[tgt]
    fy, fx = yy[mask_from], xx[mask_from]
    d = np.sqrt((fy[:, None] - ty[None, :]) ** 2 + (fx[:, None] - tx[None, :]) ** 2)
    return float(d.min())


# ------------------------------------------------------------ numbers
out = {"frame": str(Z["frame"]), "device_rect": rect, "cut_footprints": cuts,
       "map_footprints": maps, "stage_stamps": stage_stamps}

rect_mask = in_rect(RX[0], RX[1], RY[0], RY[1])
out["rect_composition"] = {k: composition(v, rect_mask) for k, v in labels.items()}

# final piece = rectangle after the 13:27 pass (y>=1288 removed) and 13:30 pass (y<=1274 removed);
# the rectangle as defined already excludes both; the S1 map includes the slanted top strip above it.
strip_mask = in_rect(-12047.5, -12037.5, 1288.0, 1296.0)
out["top_strip_S1_composition"] = composition(labels["S1"], strip_mask)

# temporal differencing S0 vs S1 inside the rectangle, like-conditioned (both bare flake)
both = rect_mask & np.isin(labels["S0"], CLASSIFIED) & np.isin(labels["S1"], CLASSIFIED)
agree = (labels["S0"][both] == labels["S1"][both]).mean() if both.any() else float("nan")
b2a = int(((labels["S0"] == LAB_B) & (labels["S1"] == LAB_A) & rect_mask).sum())
a2b = int(((labels["S0"] == LAB_A) & (labels["S1"] == LAB_B) & rect_mask).sum())
out["S0_vs_S1_in_rect"] = {"n_both_classified": int(both.sum()), "label_agreement": float(agree),
                           "B_to_A_px": b2a, "A_to_B_px": a2b,
                           "fwhm_S0_mean": float(np.nanmean(Z["fwhm_S0"][rect_mask])),
                           "fwhm_S1_mean": float(np.nanmean(Z["fwhm_S1"][rect_mask]))}

# shift stress: rectangle translated by (dx, dy) in um, -3..3
shifts = np.arange(-3, 3.01, 1.0)
grid_B = np.full((len(shifts), len(shifts)), np.nan)
grid_A = np.full_like(grid_B, np.nan)
worst = None
for i, dy in enumerate(shifts):
    for j, dx in enumerate(shifts):
        c = composition(labels["S1"], in_rect(RX[0] + dx, RX[1] + dx, RY[0] + dy, RY[1] + dy))
        grid_B[i, j], grid_A[i, j] = c["share_B"], c["share_A"]
        if worst is None or c["share_B"] < worst[2]:
            worst = (float(dx), float(dy), c["share_B"], c["share_A"], c["share_mixed"])
out["shift_stress_S1"] = {"shifts_um": shifts.tolist(), "share_B_grid": np.round(grid_B, 3).tolist(),
                          "share_A_grid": np.round(grid_A, 3).tolist(),
                          "worst_dx_dy_shareB_shareA_shareMix": worst,
                          "share_B_min_within_1um": float(np.nanmin(grid_B[2:5, 2:5])),
                          "share_B_min_within_2um": float(np.nanmin(grid_B[1:6, 1:6])),
                          "share_B_min_within_3um": float(np.nanmin(grid_B))}

# channel-footprint sweep: every placement of a w x h window inside rect (+-1 um wall tolerance)
sweeps = []
for (w, h) in [(2, 2), (3, 3), (2, 6), (4, 4), (6, 2), (4, 8), (6, 6), (8, 4), (6, 10), (10, 6), (11, 13)]:
    for tol, lab_name in ((0.0, "S1"), (1.0, "S1"), (0.0, "S0")):
        r = window_sweep(labels[lab_name], w, h, RX[0] - tol, RX[1] + tol, RY[0] - tol, RY[1] + tol)
        if r:
            r.update({"stage": lab_name, "rect_tolerance_um": tol})
            sweeps.append(r)
out["window_sweep"] = sweeps

# nearest region-A pixel to the rectangle, S1 and after the 13:27 cut (y < 1288 only)
lab_final = labels["S1"].copy()
lab_final[yc[:, None].repeat(len(xc), 1) >= 1288.0] = 0
out["nearest_A_um"] = {"S1_any": nearest_label_distance(labels["S1"], LAB_A, rect_mask),
                       "S1_below_cut30": nearest_label_distance(lab_final, LAB_A, rect_mask),
                       "S0_any": nearest_label_distance(labels["S0"], LAB_A, rect_mask)}
# A pixels inside the rectangle, listed
for k in ("S0", "S1"):
    yy, xx = np.where((labels[k] == LAB_A) & rect_mask)
    out[f"A_px_in_rect_{k}"] = [[float(xc[j]), float(yc[i])] for i, j in zip(yy, xx)]

# Raman map coverage of the rectangle
for m, fp in maps.items():
    cov = (RX[0] >= fp[0]) and (RX[1] <= fp[1]) and (RY[0] >= fp[2]) and (RY[1] <= fp[3])
    out[f"map{m}_covers_rect"] = bool(cov)

# registration uncertainty budget (um)
out["uncertainty_budget_um"] = {
    "raman_pixel_pitch": 1.0,
    "wall_position": 1.0,
    "video_to_scan_stage_registration": 0.5,   # 0.5 deg scan rotation over ~55 um, approximated axis-aligned
    "rect_edge_read_from_video": 0.5,
    "within_rect_channel_placement": "unbounded -- no GDS/optical bridge; treated by the full window sweep",
    "piece_identity": "binary -- vti-01 = this rectangle (inferred, only Hall-bar-shaped remnant) vs not from this file",
}

(RUN / "registration.json").write_text(json.dumps(out, indent=1, default=float))

# ------------------------------------------------------------- figure
proj = witio.read(str(WIP))
vid = {}
for idx, tag in ((19, "002 (12:55, pre-cut)"), (24, "004 (13:19, after cut 1)"), (32, "007 (13:29, after 1064 nm pass 30)")):
    d = proj.data[idx]
    arr = np.asarray(d.array())            # (x_px, y_px, 3)
    gx, gy = [np.asarray(g) for g in d.position_grid()]
    img = arr.transpose(1, 0, 2)           # (y_px, x_px, 3); row 0 = top (largest y)
    extent = [gx.min(), gx.max(), gy.min(), gy.max()]
    vid[tag] = (img, extent)

colors = {0: (0, 0, 0, 0), 1: "#e8e8e8", 2: "#6a3d9a", 3: "#b2df8a", 5: "#bdbdbd",
          10: "#1f78b4", 11: "#e31a1c", 12: "#ff7f00"}
bounds = [-0.5, 0.5, 1.5, 2.5, 4, 7.5, 10.5, 11.5, 12.5]
cmap = ListedColormap([colors[k] for k in (0, 1, 2, 3, 5, 10, 11, 12)])
norm = BoundaryNorm(bounds, cmap.N)
ext_lab = [xe[0], xe[-1], ye[0], ye[-1]]

fig = plt.figure(figsize=(22, 13))
gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1])
CROP = (-12082, -12020, 1262, 1306)


def base_panel(ax, tag, lab, alpha=0.55, title=""):
    img, ext = vid[tag]
    ax.imshow(img, extent=ext, origin="upper", interpolation="bilinear")
    if lab is not None:
        ax.imshow(lab, extent=ext_lab, origin="lower", cmap=cmap, norm=norm, alpha=alpha, interpolation="nearest")
    ax.add_patch(Rectangle((RX[0], RY[0]), RX[1] - RX[0], RY[1] - RY[0], fill=False, ec="k", lw=2, ls="--"))
    for k, c in cuts.items():
        ax.add_patch(Rectangle((c["x"][0], c["y"][0]), c["x"][1] - c["x"][0], c["y"][1] - c["y"][0],
                               fill=False, ec="yellow", lw=1.2, ls=":"))
    for k, fp in maps.items():
        ax.add_patch(Rectangle((fp[0], fp[2]), fp[1] - fp[0], fp[3] - fp[2], fill=False, ec="white", lw=0.8, ls="-."))
        ax.text(fp[0] + 0.3, fp[3] - 1.2, f"map {k}", color="white", fontsize=8)
    ax.set_xlim(CROP[0], CROP[1]); ax.set_ylim(CROP[2], CROP[3])
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    ax.set_title(title, fontsize=10)


ax = fig.add_subplot(gs[0, 0]); base_panel(ax, "002 (12:55, pre-cut)", labels["S0"], title="S0 — video 002 + map-22 labels (12:57)")
ax = fig.add_subplot(gs[0, 1]); base_panel(ax, "004 (13:19, after cut 1)", labels["S1"], title="S1 — video 004 + map-27 labels (13:20)")
ax = fig.add_subplot(gs[0, 2]); base_panel(ax, "007 (13:29, after 1064 nm pass 30)", None, title="video 007 (13:29): after pass 30; pass 35 (13:30) trims the bottom\n(dashed = inferred device rectangle; yellow = 1064 nm passes)")

# zoom: rectangle with labels + Hall-bar topology in two candidate orientations
ax = fig.add_subplot(gs[1, 0])
ax.imshow(labels["S1"], extent=ext_lab, origin="lower", cmap=cmap, norm=norm, interpolation="nearest")
ax.add_patch(Rectangle((RX[0], RY[0]), RX[1] - RX[0], RY[1] - RY[0], fill=False, ec="k", lw=2, ls="--"))
for gxl in np.arange(np.floor(RX[0]) - 2, RX[1] + 3): ax.axvline(gxl + 0.5 - 0.0739, color="w", lw=0.3, alpha=0.5)
# orientation 1: bar axis along y (13 um), probes L1..L4 down the left, R1,R2 right, T_SD top, B_SD bottom
cx, cy = np.mean(RX), np.mean(RY)
bw = 4.0
ax.add_patch(Rectangle((cx - bw / 2, RY[0] + 0.5), bw, RY[1] - RY[0] - 1.0, fill=False, ec="cyan", lw=1.5))
ax.text(cx, RY[1] - 0.2, "T_SD", color="cyan", ha="center", va="bottom", fontsize=8)
ax.text(cx, RY[0] + 0.2, "B_SD", color="cyan", ha="center", va="top", fontsize=8)
for i, name in enumerate(["L_1", "L_2", "L_3", "L_4"]):
    yy = RY[1] - 2.5 - i * 2.7
    ax.plot([cx - bw / 2 - 1.2, cx - bw / 2], [yy, yy], color="cyan", lw=1.5)
    ax.text(cx - bw / 2 - 1.4, yy, name, color="cyan", ha="right", va="center", fontsize=7)
for i, name in enumerate(["R_1", "R_2"]):
    yy = RY[1] - 4 - i * 4
    ax.plot([cx + bw / 2, cx + bw / 2 + 1.2], [yy, yy], color="cyan", lw=1.5, ls=":")
    ax.text(cx + bw / 2 + 1.4, yy, name + " (dead)", color="cyan", ha="left", va="center", fontsize=7)
ax.set_xlim(RX[0] - 3.5, RX[1] + 3.5); ax.set_ylim(RY[0] - 2, RY[1] + 2)
ax.set_title("Rectangle zoom (S1 labels) + card Hall-bar topology\n(schematic: orientation, bar width, probe pitch UNKNOWN — no GDS/optical bridge)", fontsize=9)
ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")

# shift stress heat map
ax = fig.add_subplot(gs[1, 1])
im = ax.imshow(grid_B, origin="lower", extent=[shifts[0] - 0.5, shifts[-1] + 0.5] * 2, vmin=0.5, vmax=1.0, cmap="viridis")
for i, dy in enumerate(shifts):
    for j, dx in enumerate(shifts):
        ax.text(dx, dy, f"{grid_B[i, j]:.2f}", ha="center", va="center", fontsize=7, color="w" if grid_B[i, j] < 0.85 else "k")
ax.set_xlabel("rectangle shift dx (µm)"); ax.set_ylabel("rectangle shift dy (µm)")
ax.set_title("Registration stress — region-B share of classified px\ninside the shifted rectangle (S1 labels)", fontsize=9)
plt.colorbar(im, ax=ax, fraction=0.046)

# window sweep
ax = fig.add_subplot(gs[1, 2])
sw = [s for s in sweeps if s["stage"] == "S1"]
for tol, mk in ((0.0, "o"), (1.0, "s")):
    ss = [s for s in sw if s["rect_tolerance_um"] == tol]
    area = [s["window_um"][0] * s["window_um"][1] for s in ss]
    ax.scatter(area, [s["share_B_min"] for s in ss], marker=mk, label=f"min B-share over placements (rect ±{tol:.0f} µm)")
    ax.scatter(area, [s["share_A_max"] for s in ss], marker=mk, facecolors="none", edgecolors="C3", label=f"max A-share over placements (rect ±{tol:.0f} µm)")
ax.set_xscale("log"); ax.set_xlabel("channel-footprint window area (µm²)"); ax.set_ylabel("share of classified px")
ax.set_ylim(-0.02, 1.02); ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="center right")
ax.set_title("Any channel footprint inside the rectangle (S1):\nworst-case B share / best-case A share", fontsize=9)

fig.suptitle("vti-01 — Step 2 registration: Raman frame (WITec stage µm, 2026-05-28) vs transport channels (device card topology only)", fontsize=12)
fig.tight_layout()
fig.savefig(RUN / "registration.png", dpi=130)

# ---------------------------------------------------------------- markdown
L = []
L.append("# vti-01 — Step 2 registration artifact\n")
L.append(f"Frame: {out['frame']}. Generated by `registration.py` → `registration.png`, `registration.json`.\n")
L.append("## Inferred device rectangle (stage µm)\n")
L.append(f"x {RX[0]}…{RX[1]}, y {RY[0]}…{RY[1]} ({RX[1]-RX[0]:.1f} × {RY[1]-RY[0]:.1f} µm) — {rect['note']}.\n")
L.append(f"Map 22 covers rectangle: {out['map22_covers_rect']}; map 27 covers rectangle: {out['map27_covers_rect']}.\n")
L.append("## Composition inside the rectangle (pixel centres; shares of classified px A/B/mixed)\n")
L.append("| stage | px | classified | A | B | mixed | share A | share B | share mixed |\n|---|---|---|---|---|---|---|---|---|")
for k, c in out["rect_composition"].items():
    d = c["counts"]
    L.append(f"| {k} | {c['n_px']} | {c['n_classified']} | {d.get(10,0)} | {d.get(11,0)} | {d.get(12,0)} | {c['share_A']:.3f} | {c['share_B']:.3f} | {c['share_mixed']:.3f} |")
s = out["S0_vs_S1_in_rect"]
L.append(f"\nS0→S1 differencing inside the rectangle (like-conditioned, both bare flake): {s['n_both_classified']} px classified in both, label agreement {s['label_agreement']:.3f}, B→A {s['B_to_A_px']} px, A→B {s['A_to_B_px']} px; mean FWHM {s['fwhm_S0_mean']:.2f} → {s['fwhm_S1_mean']:.2f} cm⁻¹.\n")
L.append(f"Region-A pixels inside the rectangle: S0 {out['A_px_in_rect_S0']}; S1 {out['A_px_in_rect_S1']}.\n")
na = out["nearest_A_um"]
L.append(f"Nearest region-A pixel to the rectangle: S0 {na['S0_any']:.1f} µm; S1 {na['S1_any']:.1f} µm (the slanted-top strip, removed by pass 30 at 13:27); S1 excluding y ≥ 1288 (final piece): {na['S1_below_cut30'] if na['S1_below_cut30'] != float('inf') else 'none'} µm.\n")
ts = out["top_strip_S1_composition"]
L.append(f"Slanted-top strip (x −12047.5…−12037.5, y 1288…1296) at S1: A {ts['counts'].get(10,0)} / B {ts['counts'].get(11,0)} / mixed {ts['counts'].get(12,0)} px — inside pass-30 footprint, not part of the final piece.\n")
st = out["shift_stress_S1"]
L.append("## Shift stress (S1 labels, rectangle translated rigidly)\n")
L.append(f"min B share: within ±1 µm {st['share_B_min_within_1um']:.3f}; ±2 µm {st['share_B_min_within_2um']:.3f}; ±3 µm {st['share_B_min_within_3um']:.3f}; worst (dx, dy, B, A, mixed) = {tuple(round(v,3) for v in st['worst_dx_dy_shareB_shareA_shareMix'])}.\n")
L.append("## Channel-footprint sweep (every placement of a w×h window inside the rectangle)\n")
L.append("| stage | rect tol (µm) | window (µm) | placements | min B share | median B share | max A share | at (x,y) | max mixed share |\n|---|---|---|---|---|---|---|---|---|")
for r in sweeps:
    L.append(f"| {r['stage']} | {r['rect_tolerance_um']:.0f} | {r['window_um'][0]}×{r['window_um'][1]} | {r['n_placements']} | {r['share_B_min']:.2f} | {r['share_B_median']:.2f} | {r['share_A_max']:.2f} | ({r['share_A_max_at'][0]:.1f}, {r['share_A_max_at'][1]:.1f}) | {r['share_mixed_max']:.2f} |")
L.append("\n## Uncertainty budget\n")
for k, v in out["uncertainty_budget_um"].items():
    L.append(f"- {k}: {v}")
(RUN / "registration.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
