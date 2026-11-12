"""hera-overlay CLI: render an annotated gate-map image from a sidecar JSON.

Reads a sidecar produced by `hera-classify`, loads the source image referenced
by `provenance.image_path`, and renders the findings' `region_gate` shapes
on top — colored boxes / points / line segments / bands.

Coordinate strategy:
- imshow the source PNG full-bleed (preserves baked-in axes labels and colorbar)
- overlay a transparent matplotlib Axes positioned at the data-area's fractional
  bbox, with `extent=scan_limits`
- draw findings in data coords on the overlay
- caption with finding titles + confidences below

Default bbox is tuned for matplotlib's gatemap-with-colorbar layout. If the
overlay is visibly offset, tune via --bbox L,B,R,T (fractional figure coords).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from hera.models import Sidecar

DEFAULT_BBOX: Tuple[float, float, float, float] = (0.10, 0.11, 0.78, 0.92)
"""Fractional (left, bottom, right, top) of the data area within the source PNG.

Used as fallback if `detect_data_bbox()` can't find clean axis spines. Tuned
for matplotlib's default `subplots()` + `colorbar()` layout.
"""


def _longest_run(mask_1d: np.ndarray) -> int:
    if not mask_1d.any():
        return 0
    diffs = np.diff(np.concatenate([[0], mask_1d.astype(int), [0]]))
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]
    return int((ends - starts).max()) if len(starts) else 0


def _cluster(positions: np.ndarray, max_gap: int = 4) -> list[Tuple[int, int]]:
    """Group sorted positions where consecutive entries differ by ≤ max_gap.

    Returns list of (cluster_start, cluster_end) inclusive pairs.
    """
    if len(positions) == 0:
        return []
    out = []
    cstart = cend = int(positions[0])
    for p in positions[1:]:
        p = int(p)
        if p - cend <= max_gap:
            cend = p
        else:
            out.append((cstart, cend))
            cstart = cend = p
    out.append((cstart, cend))
    return out


def _data_axis_pair(clusters: list[Tuple[int, int]], extent: int) -> Optional[Tuple[int, int]]:
    """Pick the data-area's two spine clusters from a list, ignoring colorbar.

    Heuristic: the leftmost (or topmost) two spine clusters are the data area's
    L/R (or top/bot) spines. Later clusters belong to a colorbar or other
    decoration and are ignored.

    Works for: bare axes (2 clusters), axes + colorbar on the relevant side
    (4 clusters: data L/R + cbar L/R), and axes + colorbar on the orthogonal
    side (still 2 clusters on this axis).
    """
    del extent  # unused in this heuristic
    if len(clusters) < 2:
        return None
    return (clusters[0][0], clusters[1][-1])


def detect_data_bbox(img: np.ndarray, dark_threshold: float = 0.15) -> Optional[Tuple[float, float, float, float]]:
    """Find the data-area pixel-rectangle by scanning for matplotlib's axis spines.

    Returns fractional (left, bottom, right, top) in figure coords (matplotlib
    convention: y increases upward), or None if detection fails.

    Strategy: matplotlib draws axes spines as thin dark lines around the data
    area. Threshold to find dark pixels, identify rows/cols with long contiguous
    dark runs (= candidate spines), cluster adjacent candidates, then pick the
    data-area pair (ignoring colorbar via largest-gap split).
    """
    if img.ndim == 3:
        gray = img[..., :3].mean(axis=-1)
    else:
        gray = img
    if gray.max() > 1.5:  # uint8-shaped → normalize to [0,1]
        gray = gray / 255.0
    dark = gray < dark_threshold

    h, w = dark.shape
    row_runs = np.array([_longest_run(dark[r]) for r in range(h)])
    col_runs = np.array([_longest_run(dark[:, c]) for c in range(w)])

    spine_rows = np.where(row_runs > 0.5 * w)[0]
    spine_cols = np.where(col_runs > 0.5 * h)[0]

    row_clusters = _cluster(spine_rows)
    col_clusters = _cluster(spine_cols)

    rows_pair = _data_axis_pair(row_clusters, h)
    cols_pair = _data_axis_pair(col_clusters, w)
    if rows_pair is None or cols_pair is None:
        return None

    top_px, bot_px = rows_pair
    left_px, right_px = cols_pair

    # Pixel coords (origin top-left) → matplotlib figure coords (origin bottom-left).
    return (left_px / w, 1.0 - bot_px / h, right_px / w, 1.0 - top_px / h)

PALETTE = ("red", "yellow", "magenta", "cyan", "lime", "orange", "white")


def _pick_color(idx: int) -> str:
    return PALETTE[idx % len(PALETTE)]


def _label(idx: int, finding) -> str:
    return finding.id or f"F{idx + 1}"


def _draw_finding(ax, idx: int, finding, scan_limits) -> None:
    rg = finding.region_gate
    if rg is None:
        return
    color = _pick_color(idx)
    label = _label(idx, finding)
    label_kwargs = dict(color=color, fontsize=9, fontweight="bold")

    if rg.kind == "box" and rg.vbg_range and rg.vtg_range:
        x0, x1 = sorted(rg.vbg_range)
        y0, y1 = sorted(rg.vtg_range)
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=color, linewidth=2))
        ax.text(x0, y1, f" {label}", verticalalignment="bottom", **label_kwargs)

    elif rg.kind == "point" and rg.vbg is not None and rg.vtg is not None:
        ax.plot(rg.vbg, rg.vtg, marker="o", color=color, markersize=12,
                markerfacecolor="none", markeredgewidth=2)
        ax.text(rg.vbg, rg.vtg, f"  {label}", verticalalignment="center", **label_kwargs)

    elif rg.kind == "line_segment" and None not in (rg.vbg_start, rg.vtg_start, rg.vbg_end, rg.vtg_end):
        ax.plot([rg.vbg_start, rg.vbg_end], [rg.vtg_start, rg.vtg_end],
                color=color, linewidth=2)
        midx = (rg.vbg_start + rg.vbg_end) / 2
        midy = (rg.vtg_start + rg.vtg_end) / 2
        ax.text(midx, midy, f" {label}", **label_kwargs)

    elif rg.kind == "vertical_band":
        if rg.vbg_range:
            x0, x1 = sorted(rg.vbg_range)
            ax.axvspan(x0, x1, color=color, alpha=0.25)
            x_label = (x0 + x1) / 2
        elif rg.vbg is not None:
            ax.axvline(rg.vbg, color=color, linewidth=2)
            x_label = rg.vbg
        else:
            return
        ax.text(x_label, scan_limits.vtg_max, label,
                verticalalignment="top", horizontalalignment="center", **label_kwargs)

    elif rg.kind == "horizontal_band":
        if rg.vtg_range:
            y0, y1 = sorted(rg.vtg_range)
            ax.axhspan(y0, y1, color=color, alpha=0.25)
            y_label = (y0 + y1) / 2
        elif rg.vtg is not None:
            ax.axhline(rg.vtg, color=color, linewidth=2)
            y_label = rg.vtg
        else:
            return
        ax.text(scan_limits.vbg_min, y_label, label,
                horizontalalignment="left", **label_kwargs)
    # descriptive / unrecognized kinds: nothing to render geometrically.


def _build_caption(annotation) -> str:
    lines = []
    for i, finding in enumerate(annotation.findings):
        label = _label(i, finding)
        conf = f" (conf {finding.confidence:.2f})" if finding.confidence is not None else ""
        lines.append(f"{label}: {finding.title}{conf}")
    return "\n".join(lines)


def render_overlay(
    sidecar_path: Path,
    *,
    output_path: Optional[Path] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    image_path_override: Optional[Path] = None,
) -> Path:
    sidecar_path = Path(sidecar_path).resolve()
    sidecar = Sidecar.model_validate_json(sidecar_path.read_text())

    img_path = Path(image_path_override) if image_path_override else Path(sidecar.provenance.image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"source image not found: {img_path}")

    img = plt.imread(img_path)
    h, w = img.shape[:2]

    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax_bg = fig.add_axes(rect=(0.0, 0.0, 1.0, 1.0))
    ax_bg.imshow(img)
    ax_bg.set_axis_off()

    if bbox is None:
        detected = detect_data_bbox(img)
        bbox = detected if detected is not None else DEFAULT_BBOX
    left, bot, right, top = bbox
    ax = fig.add_axes(rect=(left, bot, right - left, top - bot))
    ax.set_facecolor("none")
    sl = sidecar.annotation.scan_limits
    ax.set_xlim(sl.vbg_min, sl.vbg_max)
    ax.set_ylim(sl.vtg_min, sl.vtg_max)
    ax.set_axis_off()

    for i, finding in enumerate(sidecar.annotation.findings):
        _draw_finding(ax, i, finding, sl)

    caption = _build_caption(sidecar.annotation)
    if caption:
        fig.text(0.01, 0.01, caption, fontsize=8, family="monospace",
                 verticalalignment="bottom",
                 bbox=dict(facecolor="white", edgecolor="black", alpha=0.85, pad=4))

    if output_path is None:
        # <sidecar_dir>/<image_stem>__<timestamp>__annotated.png
        stem = sidecar_path.stem
        if "__" in stem:
            ts = stem.split("__", 1)[1]
            output_path = sidecar_path.parent / f"{img_path.stem}__{ts}__annotated.png"
        else:
            output_path = sidecar_path.parent / f"{img_path.stem}__annotated.png"

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches=None)
    plt.close(fig)
    return output_path


def _parse_bbox(text: str) -> Tuple[float, float, float, float]:
    parts = [float(x) for x in text.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--bbox must be L,B,R,T (4 floats)")
    return tuple(parts)  # type: ignore[return-value]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hera-overlay",
        description="Render annotated gate-map image from a hera-classify sidecar JSON.",
    )
    parser.add_argument("sidecar", type=Path, help="Path to the sidecar JSON file.")
    parser.add_argument("--output", type=Path, help="Output PNG path (default: <sidecar_dir>/<image_stem>__<ts>__annotated.png).")
    parser.add_argument("--image", type=Path, help="Override source image path (default: sidecar's provenance.image_path).")
    parser.add_argument(
        "--bbox",
        type=_parse_bbox,
        default=None,
        help="Data-area bbox in source PNG as L,B,R,T fractional coords (default: auto-detect via axis-spine search).",
    )
    args = parser.parse_args()

    if not args.sidecar.exists():
        sys.exit(f"error: sidecar does not exist: {args.sidecar}")

    out = render_overlay(
        args.sidecar,
        output_path=args.output,
        bbox=args.bbox,
        image_path_override=args.image,
    )
    print(out)
