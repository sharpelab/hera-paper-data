"""Registration-chain schematic for the vti-02 Raman x transport fusion.

Draws the frame chain from the Raman acquisition frame (parent flake) to
the transport frame (finished device / contact map), marking which links
carry coordinates (none do) and the resulting coverage classification.
Schematic only — no quantitative geometry exists to plot.

Run: uv run --no-project --with matplotlib python make_registration_figure.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(11, 5.2))
ax.set_xlim(0, 11)
ax.set_ylim(0, 5.2)
ax.axis("off")

BOX = dict(boxstyle="round,pad=0.12", linewidth=1.2)


def box(x, y, w, h, title, lines, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, facecolor=fc, edgecolor=ec, **BOX))
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top",
            fontsize=9.5, fontweight="bold")
    ax.text(x + w / 2, y + h - 0.62, lines, ha="center", va="top", fontsize=8)


def link(x0, x1, y, label, risk):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
                                 mutation_scale=14, color="0.25", linewidth=1.4,
                                 linestyle=(0, (4, 3))))
    ax.text((x0 + x1) / 2, y + 0.14, label, ha="center", va="bottom", fontsize=8)
    ax.text((x0 + x1) / 2, 1.42, risk, ha="center", va="top",
            fontsize=7.5, color="#8c2d04", style="italic")


Y = 2.6
box(0.25, Y - 0.95, 2.3, 1.9, "Parent flake\n(Raman frame)",
    "\nfab-record: one rhombohedral\ndomain, position NOT given\nno map, no raster,\nno spot coordinates",
    "#f6e8c3", "#8c6d1f")
box(3.75, Y - 0.95, 1.9, 1.9, "Cut piece",
    "\n\"cut out the rhomb.\ndomain\" — prose only,\nno cut outline",
    "#eeeeee", "0.4")
box(6.55, Y - 0.95, 1.7, 1.9, "Stack",
    "\n\nno stack imagery\nsupplied",
    "#eeeeee", "0.4")
box(9.0, Y - 0.95, 1.85, 1.9, "Finished device\n(transport frame)",
    "\ncontact labels only\n(no image / GDS):\nsr1 = B_1−B_2, straddles\na flake corner; regions\nA + B in series",
    "#d9e8f5", "#1f4e79")

link(2.55, 3.75, Y, "laser cut", "clean thermal / local heat\n(stage fork: pre- or post- last Raman)")
link(5.65, 6.55, Y, "stacking + anneal", "pickup + chem/bake\n(ABC→ABA risk)")
link(8.25, 9.0, Y, "litho / contacts", "metal deposition\n(highest ABC→ABA risk)")

ax.text(5.5, 4.85,
        "vti-02 registration chain — Raman frame → transport frame",
        ha="center", fontsize=11.5, fontweight="bold")
ax.text(5.5, 4.5,
        "Every inter-frame link is dashed: NO link carries coordinates. No anchor exists in any frame.",
        ha="center", fontsize=9)

ax.text(5.5, 0.72,
        "Registration uncertainty: not quantifiable (no common frame, no anchors); domain scale: unknown (no map).\n"
        "Coverage of channel B_1−B_2 by Raman: UNCOVERED — the only linkage is the testimony “device ⊂ rhombohedral domain”,\n"
        "which carries no coordinates and cannot establish coverage. No interpolation performed.",
        ha="center", va="top", fontsize=8.8,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fdf2f2", edgecolor="#a33"))

fig.savefig("registration_chain.png", dpi=200, bbox_inches="tight")
print("wrote registration_chain.png")
