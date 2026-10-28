"""Shared style for every Python figure in the paper.

rcparams_paper.json is the CSC paper's (sharpelab/Fermiology-and-the-cCSC, utils/rcparams_paper.json),
copied verbatim. Figures are drawn at their printed width and placed 1:1 with a bare \\includegraphics,
so the font sizes in the PDF are the font sizes on the page.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

PT = 1 / 72.27                 # TeX points per inch
TEXT_W = 510 * PT              # revtex reprint \textwidth
COL_W = 246 * PT               # revtex reprint \columnwidth

# panel letters: bold, lowercase, at the default text size (CSC's rule), left-aligned with the panel's y-axis
# label and LABEL_DY points above the top of its axes, so they clear the top tick label in every figure
LABEL_DY = 8

BLUE, ORANGE = "#1170aa", "#d1610d"  # the paper's agrees / hedged pair (fig-matrix-table.tex)


INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

# CSC's style, with Nature's text sizes, plus the light grid kept from the old Fig. 4 and frameless legends
LOOK = {
    # Nature's sizes on top of CSC's: text 6-7 pt, panel letters 8 pt bold (DejaVu's large x-height makes CSC's
    # 8/7 pt read as large as the 9 pt captions)
    "font.size": 8, "axes.labelsize": 7, "axes.titlesize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
    "legend.fontsize": 6, "legend.title_fontsize": 6,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.axisbelow": "line",           # grid and ticks over images and patches, under lines: inward ticks stay visible
    "legend.frameon": False,
    "pdf.fonttype": 42,                 # embed TrueType so the text stays text
}


def use():
    plt.rcParams.update(json.loads((HERE / "rcparams_paper.json").read_text()))
    plt.rcParams.update(LOOK)


def panel_label(fig, ax, letter, y=None, x=None):
    """Bold letter left-aligned with ax's y-axis label (tick labels if it has none), baseline LABEL_DY points
    above ax's top, or at y inches from the figure bottom for panels whose top carries a colour bar.
    Call after everything on ax is drawn."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    bb = ax.yaxis.get_tightbbox(r)
    if x is None:
        x = (bb.x0 if bb is not None and bb.width > 0 else ax.get_window_extent(r).x0) / fig.dpi
    if y is None:
        y = ax.get_window_extent(r).y1 / fig.dpi + LABEL_DY / 72
    fig.text(x / fig.get_figwidth(), y / fig.get_figheight(), letter, fontweight="bold", ha="left",
             va="baseline", color="k")


def timeline(ax, end, breaks, ticks, events, xlabel, waits=(), fs=6, gap_pt=7):
    """A session timeline on ax (axis off): a line from 0 to an arrow at `end` with a // glyph at each x in
    `breaks`, `ticks` as (x, label), `events` as (x, label or None) points with labels rotated 60 degrees, and
    `waits` as (x, label) in the muted colour. x is in drawn units; the caller maps hours to them."""
    k = "#4d4d4d"
    ax.set_xlim(-0.02 * end, end * 1.01); ax.set_ylim(-1, 1)
    ax.axis("off")
    w_in = ax.get_position().width * ax.figure.get_figwidth()
    g = (gap_pt / 72) / w_in * (ax.get_xlim()[1] - ax.get_xlim()[0]) / 2     # half the gap, in data units
    xs = [0.0] + [v for b in breaks for v in (b - g, b + g)]
    for x0, x1 in zip(xs[0::2], xs[1::2]):
        ax.plot([x0, x1], [0, 0], color=k, lw=0.6)
    ax.annotate("", xy=(end, 0), xytext=(xs[-1], 0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.15", color=k, lw=0.6))
    for b in breaks:
        for c in (b - g * 0.45, b + g * 0.45):
            ax.plot([c - g * 0.35, c + g * 0.35], [-0.12, 0.12], color=k, lw=0.6)
    for x, lab in ticks:
        ax.plot([x, x], [0, -0.08], color=k, lw=0.6)
        ax.text(x, -0.12, lab, ha="center", va="top", fontsize=fs)
    ax.text(end / 2, -0.55, xlabel, ha="center", va="top", fontsize=fs + 1)
    # labels at 60 degrees, baseline started 3 pt out along the label from the point and shifted half an x-height
    # across it, so each label's letters sit centred on the line through its point
    xh = 0.55 * fs                                     # DejaVu x-height, pt
    off = (3 * 0.5 + xh / 2 * 0.866, 3 * 0.866 - xh / 2 * 0.5)
    rot = dict(rotation=60, rotation_mode="anchor", ha="left", va="baseline", textcoords="offset points", xytext=off)
    for x, lab in waits:
        ax.annotate(lab, (x, 0), fontsize=fs, color=MUTED, **rot)
    for x, lab in events:
        ax.plot(x, 0, "o", ms=2.4, color="#404040", zorder=3)
        if lab:
            ax.annotate(lab, (x, 0), fontsize=fs, **rot)


CBAR_H, CBAR_GAP = 0.083, 0.06   # colour-bar thickness and its gap above the axes, in


def topbar(fig, ax, im, label, ticks=None, x0=0.55, w=0.45):
    """Horizontal colour bar over the right of ax's top edge, ticks on top, its label to its left."""
    h_in = ax.get_position().height * fig.get_figheight()
    cax = ax.inset_axes([x0, 1 + CBAR_GAP / h_in, w, CBAR_H / h_in])
    fig.colorbar(im, cax=cax, orientation="horizontal", ticks=ticks)
    cax.xaxis.set_ticks_position("top"); cax.tick_params(length=2, pad=1)
    cax.minorticks_off()                 # major ticks only: minor ticks are lost against the colours
    cax.grid(False)
    cax.annotate(label, xy=(0, 0.5), xycoords="axes fraction", xytext=(-3, 0), textcoords="offset points",
                 ha="right", va="center", fontsize=plt.rcParams["legend.fontsize"])
    return cax


def snug_below(fig, ax, top, pad=0.08):
    """Move ax up or down so the highest text on it sits pad inches below `top` (inches from the bottom)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    hi = max(t.get_window_extent(r).y1 for t in ax.texts if t.get_text()) / fig.dpi
    p = ax.get_position()
    ax.set_position([p.x0, p.y0 + (top - pad - hi) / fig.get_figheight(), p.width, p.height])


def save(fig, out, pad=2):
    """Save at the full drawn width but cropped top and bottom to the ink plus pad points, so no figure
    carries empty margin into the page."""
    from matplotlib.transforms import Bbox
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    # dpi: rasterized artists (the maps, and colour-bar gradients, which matplotlib rasterizes itself) are drawn on a
    # pixel grid at this resolution; at the default 100 dpi they snap up to 0.01 in off their vector frames
    fig.savefig(out, dpi=600, bbox_inches=Bbox.from_extents(0, bb.y0 - pad / 72, fig.get_figwidth(), bb.y1 + pad / 72))


def axes_in(fig, x, y, w, h, **kw):
    """Axes placed in inches from the figure's bottom-left corner."""
    W, H = fig.get_figwidth(), fig.get_figheight()
    return fig.add_axes([x / W, y / H, w / W, h / H], **kw)


def outdir(argv):
    out = Path(argv[1]) if len(argv) > 1 else HERE / "out"
    out.mkdir(parents=True, exist_ok=True)
    return out
