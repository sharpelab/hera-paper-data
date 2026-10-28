# s2_registration.py — fusion Step 2 registration artifact for vti-01
#
# Places every frame bridge actually supplied on one stage-coordinate figure:
#   - the three stage-registered video images inside inputs/vti-01.wip
#     (exact per-pixel stage grids via witio position_grid — 0.5° rotation kept)
#   - the Raman region raster (inputs/regions.npz, from the locked Raman contract)
#   - map A / map B footprints and the S1 leftover rectangle
# and documents the *absent* bridge: no optical image, GDS, or build testimony
# links the stage frame to the finished vti-01 Hall bar, so the transport
# channels (sr1: B_SD–L4, sr2: L4–L1, sr3: L3–L2) cannot be placed here.
#
# Outputs: fig_registration.png, registration_numbers.txt
#
# Run from the run dir:
#   uv run --no-project --with numpy --with scipy --with matplotlib --with witio \
#       python s2_registration.py

import numpy as np
import witio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D

WIP = "inputs/vti-01.wip"
REG = "inputs/regions.npz"
DS = 4  # video downsample factor for pcolormesh

# fixed categorical assignment (entity -> hue, never cycled)
LABEL_COLORS = {
    1: "#2563eb",  # R1 ABA band — blue
    2: "#ea580c",  # R2 ABC main domain — orange
    3: "#9333ea",  # R3 mixed texture — purple
    4: "#ca8a04",  # R4 fold triangle — dark yellow
    5: "#0d9488",  # R5 thin sliver — teal
    6: "#6b7280",  # rim / unclassified — gray
}
LABEL_NAMES = {
    1: "R1 ABA (strong, S0)",
    2: "R2 ABC (strong, S0; leftover re-confirmed S1)",
    3: "R3 mixed ABA+ABC (strong as mixture, S0)",
    4: "R4 fold — uninformative",
    5: "R5 thin sliver — uninformative",
    6: "rim — unclassified",
}

p = witio.read(WIP)

def video(bid):
    bm = p.find_by_id(bid)
    rgb = np.asarray(bm.array())          # (nx, ny, 3)
    pg = np.asarray(bm.position_grid())   # (2, nx, ny)
    return rgb, pg

def show_video(ax, rgb, pg, ds=DS):
    # exact stage-frame rendering (keeps the 0.5° rotation): pcolormesh on the
    # true per-pixel grid, downsampled; color via flat shading of RGB
    x = pg[0, ::ds, ::ds]
    y = pg[1, ::ds, ::ds]
    c = rgb[::ds, ::ds, :].astype(float) / 255.0
    m = ax.pcolormesh(x, y, np.zeros((x.shape[0] - 1, x.shape[1] - 1)),
                      shading="flat")
    m.set_array(None)
    m.set_facecolor(c[:-1, :-1].reshape(-1, 3))
    ax.set_aspect("equal")

z = np.load(REG, allow_pickle=True)
labels = z["labels"]          # (ny=40, nx=55), raster frame (axis-aligned approx)
x_um, y_um = z["x_um"], z["y_um"]

# map A true grid (rotation kept) for the exact overlay
gA = p.find_by_id(87)
pgA = np.asarray(gA.position_grid())      # (2, 55, 40)
labels_T = labels.T                       # (nx=55, ny=40) to match pgA

# raster-vs-true-grid deviation (in-frame registration error of the raster)
XX = np.stack(np.meshgrid(x_um, y_um), 0)         # (2, ny, nx) raster centers
dev = np.hypot(pgA[0].T - XX[0], pgA[1].T - XX[1])
rot_dev_max, rot_dev_mean = dev.max(), dev.mean()

vids = {bid: video(bid) for bid in (80, 92, 110)}

# footprints (from raman-provenance.md / regions.npz)
mapA_box = (-12078.0, -12023.0, 1264.0, 1304.0)     # x0,x1,y0,y1 (approx, axis-aligned)
mapB_box = (-12049.7, -12027.7, 1264.5, 1299.5)
leftover_box = (-12047.0, -12035.0, 1266.0, 1289.0)  # S1 leftover rectangle (part of R2)

def draw_box(ax, box, color, label=None, ls="--", lw=1.6):
    x0, x1, y0, y1 = box
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           edgecolor=color, ls=ls, lw=lw))
    if label:
        ax.annotate(label, (x0 + 0.4, y1 - 0.6), color=color, fontsize=8,
                    va="top", fontweight="bold")

def overlay_regions(ax, alpha=0.40, contour_lw=1.2):
    for lab, col in LABEL_COLORS.items():
        mask = (labels_T == lab).astype(float)
        if mask.sum() == 0:
            continue
        ax.contour(pgA[0], pgA[1], mask, levels=[0.5], colors=[col],
                   linewidths=contour_lw)
        ax.contourf(pgA[0], pgA[1], np.ma.masked_where(mask < 0.5, mask),
                    levels=[0.5, 1.5], colors=[col], alpha=alpha)

fig, axes = plt.subplots(2, 2, figsize=(14.5, 11.5), dpi=150)
fig.patch.set_facecolor("white")

# panel a — S0 video + region raster
ax = axes[0, 0]
show_video(ax, *vids[80])
overlay_regions(ax)
draw_box(ax, mapA_box, "#111827", "map A (S0, 19:57 UTC)")
ax.set_title("(a) S0 — Video 002 (19:55 UTC), intact flake\n"
             "+ Raman region raster (regions.npz via map A true grid)", fontsize=10)

# panel b — S1 video + map B + leftover rectangle
ax = axes[0, 1]
show_video(ax, *vids[92])
overlay_regions(ax, alpha=0.12, contour_lw=0.8)
draw_box(ax, mapB_box, "#111827", "map B (S1, 20:20 UTC)")
draw_box(ax, leftover_box, "#ea580c", "S1 leftover (ABC re-confirmed)", ls="-")
ax.set_title("(b) S1 — Video 004 (20:19 UTC), after pickup 1\n"
             "(pickup 1 material = candidate device stock A)", fontsize=10)

# panel c — post-pickup-2 video
ax = axes[1, 0]
show_video(ax, *vids[110])
overlay_regions(ax, alpha=0.12, contour_lw=0.8)
draw_box(ax, leftover_box, "#ea580c", "was: S1 leftover", ls="-")
ax.set_title("(c) Video 007 (20:29 UTC), after pickup 2 removed the\n"
             "leftover's upper part (pickup 2 = candidate device stock B)", fontsize=10)

for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
    ax.set_xlabel("stage x (µm)")
    ax.set_ylabel("stage y (µm)")
    ax.set_xlim(-12085, -12016)
    ax.set_ylim(1258, 1310)

# panel d — the bridge ledger (what is and is not registrable)
ax = axes[1, 1]
ax.axis("off")
ledger = (
    "(d) BRIDGE LEDGER — stage frame ↔ finished device vti-01\n"
    "\n"
    "Frame bridges supplied:\n"
    "  ✓ in-file stage-registered video images (panels a–c; exact per-pixel\n"
    "     stage grids, 0.5° rotation kept)\n"
    "  ✓ Raman region raster in the same stage frame (regions.npz)\n"
    "  ✗ optical image of the finished device — NOT SUPPLIED\n"
    "  ✗ device GDS — NOT SUPPLIED\n"
    "  ✗ build-step list / pickup→device testimony — NOT SUPPLIED\n"
    "\n"
    "Transport channels (device card, topological only — no coordinates):\n"
    "  Hall bar: T_SD (src) — L1/L2/L3/L4 left probes — B_SD (drain)\n"
    "     sr1 = B_SD–L4     sr2 = L4–L1     sr3 = L3–L2\n"
    "\n"
    "ANCHORS between the two frames: ZERO. Two disjoint candidate stocks\n"
    "exist (pickup 1 ≈ flake minus leftover: spans R1 ABA + R2 ABC + R3\n"
    "mixed; pickup 2 = leftover's upper part: ABC at S1). Which stock — if\n"
    "either — became vti-01 is unknown; channel placement within it is\n"
    "unknown.\n"
    "\n"
    "REGISTRATION UNCERTAINTY\n"
    "  within stage frame:  ±1 µm (map step; raster-vs-true-grid dev\n"
    f"     max {rot_dev_max:.2f} µm, mean {rot_dev_mean:.2f} µm)\n"
    "  stage → device:      UNBOUNDED (no anchors) — exceeds the 2–5 µm\n"
    "     domain scale by construction\n"
    "\n"
    "RAMAN COVERAGE OF TRANSPORT CHANNELS\n"
    "  sr1 (B_SD–L4):  UNCOVERED\n"
    "  sr2 (L4–L1):    UNCOVERED\n"
    "  sr3 (L3–L2):    UNCOVERED\n"
    "  (recipe: uncovered stays uncovered — no interpolation)"
)
ax.text(0.0, 1.0, ledger, transform=ax.transAxes, va="top", ha="left",
        fontsize=9.0, family="monospace", color="#111827")

handles = [Patch(facecolor=c, edgecolor=c, alpha=0.5, label=LABEL_NAMES[l])
           for l, c in LABEL_COLORS.items()]
handles += [Line2D([], [], color="#111827", ls="--", label="map footprint"),
            Line2D([], [], color="#ea580c", ls="-", label="S1 leftover rectangle")]
fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False)
fig.suptitle("vti-01 fusion Step 2 — registration artifact: Raman stage frame; "
             "device-frame bridge ABSENT → all channels UNCOVERED",
             fontsize=12, y=0.995)
fig.tight_layout(rect=(0, 0.05, 1, 0.98))
fig.savefig("fig_registration.png", bbox_inches="tight")

with open("registration_numbers.txt", "w") as f:
    f.write("vti-01 fusion Step 2 registration numbers\n")
    f.write(f"raster-vs-true-mapA-grid deviation: max {rot_dev_max:.3f} um, "
            f"mean {rot_dev_mean:.3f} um (0.5 deg rotation + center convention)\n")
    f.write("within-stage-frame registration uncertainty: +/-1 um class "
            "(1 um map step dominates)\n")
    f.write("stage->device bridge: NO ANCHORS (no device optical image, no GDS, "
            "no build testimony) -> uncertainty unbounded\n")
    f.write("domain scale (Raman contract R3): 2-5 um -> unbounded >> domain "
            "scale -> coverage cannot be established\n")
    f.write("coverage: sr1 UNCOVERED, sr2 UNCOVERED, sr3 UNCOVERED\n")
    for lab in sorted(LABEL_COLORS):
        n = int((labels == lab).sum())
        f.write(f"label {lab} px count: {n}\n")
print("wrote fig_registration.png, registration_numbers.txt")
print(f"raster dev max {rot_dev_max:.3f} mean {rot_dev_mean:.3f} um")
