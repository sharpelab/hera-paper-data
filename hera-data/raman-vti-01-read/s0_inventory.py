#!/usr/bin/env python3
"""Step 0 — inventory the vti-01 WITec project from in-file metadata only.

Writes (all under this directory):
  intermediates/inventory.json        every project item: class, caption, shape, metadata
  intermediates/map_<k>.npz           each spectral map: wn, cube[nx,ny,nsp], X,Y stage-µm grids, meta
  intermediates/video_<k>.npz         each video image: rgb[ny,nx,3] + stage-µm extent
  figures/f0_video_<k>.png            video images in the stage µm frame
  figures/f0_overview.png             all video images with every scan footprint outlined
  intermediates/inventory.md          the Step 0 table skeleton (numbers only; prose in provenance.md)

Run: uv run --no-project --with numpy --with scipy --with matplotlib --with witio python3 s0_inventory.py
"""
import datetime as dt
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import witio

HERE = Path(__file__).resolve().parent
WIP = Path("/data/sharpelab/hera-data/raman-vti-01/vti-01.wip")
INT = HERE / "intermediates"
FIG = HERE / "figures"
INT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)


def jsonable(v):
    if isinstance(v, dt.datetime):
        return v.isoformat()
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    return v


proj = witio.read(str(WIP))
inv = dict(file=str(WIP), witio_version=getattr(witio, "__version__", "?"),
           project_version=proj.version, magic=proj.magic.decode(errors="replace"),
           system_metadata=proj.system_metadata, items=[])
maps, videos = [], []
for k, d in enumerate(proj.data):
    item = dict(index=k, class_name=d.class_name, caption=d.caption)
    try:
        arr = np.asarray(d.array())
        item["shape"] = list(arr.shape)
        item["dtype"] = str(arr.dtype)
    except Exception:
        arr = None
    meta = d.measurement_metadata
    meta = meta() if callable(meta) else meta
    meta = {kk: jsonable(vv) for kk, vv in (meta or {}).items()}
    item["meta"] = meta
    inv["items"].append(item)
    if arr is None:
        continue
    if d.class_name == "TDGraph" and arr.ndim == 3:
        X, Y = d.position_grid()           # (SizeX, SizeY) stage µm
        wn, unit = d.x_axis()
        wn = np.asarray(wn, float)
        item["spectral_axis"] = dict(unit=unit, n=int(wn.size), min=float(wn.min()),
                                     max=float(wn.max()),
                                     step_median=float(np.median(np.abs(np.diff(wn)))))
        item["stage_extent_um"] = dict(xmin=float(X.min()), xmax=float(X.max()),
                                       ymin=float(Y.min()), ymax=float(Y.max()))
        item["pixel_pitch_um"] = dict(x=float(np.median(np.abs(np.diff(X, axis=0)))) if X.shape[0] > 1 else None,
                                      y=float(np.median(np.abs(np.diff(Y, axis=1)))) if Y.shape[1] > 1 else None)
        item["cube_stats"] = dict(min=int(arr.min()), max=int(arr.max()),
                                  n_saturated_65535=int((arr >= 65535).sum()))
        np.savez_compressed(INT / f"map_{k}.npz", wn=wn, cube=arr, X=X, Y=Y,
                            meta=json.dumps(meta), caption=d.caption)
        maps.append((k, d.caption, X, Y, meta))
    elif d.class_name == "TDBitmap" and arr.ndim == 3:
        X, Y = d.position_grid()
        rgb = arr.transpose(1, 0, 2)       # (ny, nx, 3)
        ext = [float(X[0, 0]), float(X[-1, 0]), float(Y[0, 0]), float(Y[0, -1])]
        item["stage_extent_um"] = dict(x0=ext[0], x1=ext[1], y0=ext[2], y1=ext[3])
        item["um_per_px"] = dict(x=float((ext[1] - ext[0]) / (X.shape[0] - 1)),
                                 y=float((ext[3] - ext[2]) / (X.shape[1] - 1)))
        np.savez_compressed(INT / f"video_{k}.npz", rgb=rgb, extent=np.array(ext),
                            meta=json.dumps(meta), caption=d.caption)
        videos.append((k, d.caption, rgb, ext, meta))
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.imshow(rgb, extent=[ext[0], ext[1], ext[2], ext[3]] if ext[2] < ext[3]
                  else [ext[0], ext[1], ext[3], ext[2]], origin="lower" if ext[2] < ext[3] else "upper")
        ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
        ax.set_title(f"[{k}] {d.caption}  {meta.get('trace_creation_time_local','')}")
        fig.tight_layout(); fig.savefig(FIG / f"f0_video_{k}.png", dpi=130); plt.close(fig)

(INT / "inventory.json").write_text(json.dumps(inv, indent=1, default=str))

# overview: each video image with all scan footprints
fig, axes = plt.subplots(1, len(videos), figsize=(7 * len(videos), 6.5))
axes = np.atleast_1d(axes)
colors = ["C1", "C3", "C2", "C4", "C5"]
for ax, (k, cap, rgb, ext, meta) in zip(axes, videos):
    flip = ext[2] > ext[3]
    ax.imshow(rgb, extent=[ext[0], ext[1], min(ext[2], ext[3]), max(ext[2], ext[3])],
              origin="upper" if flip else "lower")
    for c, (km, capm, X, Y, mm) in zip(colors, maps):
        xs = [X.min(), X.max(), X.max(), X.min(), X.min()]
        ys = [Y.min(), Y.min(), Y.max(), Y.max(), Y.min()]
        ax.plot(xs, ys, c, lw=1.3, label=f"[{km}] {capm.split('--')[1]} {mm.get('laser_wavelength_nm', 0):.0f} nm")
    ax.set_title(f"[{k}] {cap} {meta.get('trace_creation_time_local','')[11:16]}", fontsize=9)
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    ax.legend(fontsize=7, loc="lower right")
fig.tight_layout(); fig.savefig(FIG / "f0_overview.png", dpi=120); plt.close(fig)

# Step 0 table skeleton
lines = ["| item | caption | px | span µm | pitch µm | λ nm | P_fiber mW | t_int s | grating | axis cm⁻¹ (n, step) | local time | stage centre µm |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for it in inv["items"]:
    if it["class_name"] != "TDGraph":
        continue
    m, sa = it["meta"], it["spectral_axis"]
    lines.append(f"| {it['index']} | {it['caption']} | {m['scan_size_x_px']}×{m['scan_size_y_px']} | "
                 f"{m['scan_span_x_um']:.1f}×{m['scan_span_y_um']:.1f} | "
                 f"{it['pixel_pitch_um']['x']:.3f}×{it['pixel_pitch_um']['y']:.3f} | "
                 f"{m['laser_wavelength_nm']:.1f} | {m.get('laser_power_in_fiber_mw', float('nan')):.2f} | "
                 f"{m['integration_time_s']:.3f} | {m['grating']} | "
                 f"{sa['min']:.0f}…{sa['max']:.0f} ({sa['n']}, {sa['step_median']:.2f}) | "
                 f"{m['trace_creation_time_local']} | ({m['scan_center_x_um']:.1f}, {m['scan_center_y_um']:.1f}) |")
lines.append("")
lines.append("| item | caption | px | span µm | stage extent µm (x0,x1,y0,y1) | local time |")
lines.append("|---|---|---|---|---|---|")
for it in inv["items"]:
    if it["class_name"] != "TDBitmap":
        continue
    m, e = it["meta"], it["stage_extent_um"]
    lines.append(f"| {it['index']} | {it['caption']} | {m['scan_size_x_px']}×{m['scan_size_y_px']} | "
                 f"{m['scan_span_x_um']:.1f}×{m['scan_span_y_um']:.1f} | "
                 f"({e['x0']:.1f}, {e['x1']:.1f}, {e['y0']:.1f}, {e['y1']:.1f}) | {m['trace_creation_time_local']} |")
lines.append("")
lines.append("Transformation-only items (no data payload): " + ", ".join(
    it["caption"] for it in inv["items"] if it["class_name"] == "TDSpaceTransformation"))
(INT / "inventory.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
for it in inv["items"]:
    if "cube_stats" in it:
        print(it["index"], it["cube_stats"], it["spectral_axis"])
