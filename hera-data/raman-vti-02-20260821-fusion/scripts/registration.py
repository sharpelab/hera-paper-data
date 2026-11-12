#!/usr/bin/env python
"""Step 2 registration artifact for the vti-02 Raman x transport fusion.

There is NO metric frame bridge in the input set: raman.md carries no
coordinates, no map, no scale; no optical image or GDS was supplied; the
ana notebook contains only electrical geometry. The only registration
available is the topological chain attested in raman.md plus the device
card's contact map. This script draws that chain, with every link labeled
by what it is (attestation vs. record) and produces the registration
record alongside.

Output: artifacts/registration-vti-02.png (+ .md record written by hand,
pointed to from the figure caption).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Polygon, FancyBboxPatch

# palette (dataviz reference instance, light mode)
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a897f"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE = "#fcfcfb"

fig, ax = plt.subplots(figsize=(13.5, 6.8), dpi=160)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
ax.set_xlim(0, 13.5); ax.set_ylim(0, 6.8); ax.axis("off")

def label(x, y, s, size=8.5, color=INK2, ha="center", weight="normal", style="normal"):
    ax.text(x, y, s, size=size, color=color, ha=ha, va="top",
            weight=weight, style=style, linespacing=1.35)

# ---- Panel 1: parent flake, Raman stage -------------------------------
flake = Polygon([(0.7,4.1),(1.3,5.6),(2.4,5.9),(3.3,5.3),(3.4,4.3),(2.6,3.5),(1.4,3.4)],
                closed=True, facecolor="#e9e8e3", edgecolor=MUTED, lw=1.0)
ax.add_patch(flake)
abc = Polygon([(1.5,4.0),(1.9,5.2),(2.8,5.3),(3.0,4.5),(2.4,3.8)], closed=True,
              facecolor="none", edgecolor=ORANGE, lw=1.6, hatch="///", zorder=3)
abc.set_facecolor((0.922, 0.408, 0.204, 0.12))
ax.add_patch(abc)
ax.text(2.2, 6.35, "Parent flake — Raman stage", size=10, color=INK, ha="center", weight="bold")
ax.text(2.25, 4.65, "attested\nABC domain", size=8.5, color=ORANGE, ha="center", va="center")
label(2.1, 3.2,
      "flake 84135 (URL not fetched)\nno map · no coordinates · no scale\nstage: pre-stacking; date unknown\n(cut ordering internally inconsistent)",
      size=7.8)

# ---- Panel 2: cut region ---------------------------------------------
cut = Polygon([(5.3,4.2),(5.5,5.3),(6.5,5.4),(6.7,4.4),(6.0,3.9)], closed=True,
              facecolor=(0.922, 0.408, 0.204, 0.12), edgecolor=ORANGE, lw=1.6, hatch="///")
ax.add_patch(cut)
ax.text(6.0, 6.35, "Cut region", size=10, color=INK, ha="center", weight="bold")
label(6.0, 3.65,
      'claimed ⊂ ABC domain\n("expect the cut region to\ncontain no ABA") — attestation,\nnot a registered boundary',
      size=7.8)

# ---- Panel 3: finished device (contact map, device card) --------------
dev = FancyBboxPatch((8.9, 3.7), 3.6, 1.9, boxstyle="round,pad=0.08",
                     facecolor="#eef3fa", edgecolor=MUTED, lw=1.0)
ax.add_patch(dev)
ax.text(10.7, 6.35, "Device vti-02 (wired)", size=10, color=INK, ha="center", weight="bold")
# pads: T arc on top (T_0 alive, T_1..T_4 dead), B_1,B_2 left/bottom, B_3 bottom right
pads = {"T_0": (9.3, 5.45, True), "T_1": (10.0, 5.6, False), "T_2": (10.7, 5.65, False),
        "T_3": (11.4, 5.6, False), "T_4": (12.1, 5.45, False),
        "B_1": (9.1, 4.55, True), "B_2": (9.55, 3.95, True), "B_3": (12.1, 3.95, True)}
for name, (x, y, alive) in pads.items():
    c = Circle((x, y), 0.13, facecolor=(BLUE if alive else "#d5d4cc"),
               edgecolor=INK2 if alive else MUTED, lw=0.8, zorder=4)
    ax.add_patch(c)
    dx = -0.22 if name in ("B_1", "B_2") else (0.24 if name == "B_3" else 0.0)
    dy = 0.0 if name in ("B_1", "B_2", "B_3") else 0.26
    ax.text(x + dx, y + dy, name, size=7.2, ha="center", va="center",
            color=INK if alive else MUTED, zorder=5)
# sr1 channel B_1-B_2
ax.plot([9.1, 9.55], [4.55, 3.95], color=BLUE, lw=3.0, solid_capstyle="round", zorder=3)
ax.text(8.55, 4.3, "sr1 (R$_{xx}$)\nB$_1$–B$_2$", size=8, color=BLUE, ha="center", va="center", weight="bold")
# source-drain path
ax.annotate("", xy=(12.1, 4.1), xytext=(9.35, 5.35),
            arrowprops=dict(arrowstyle="->", color=INK2, lw=1.0, ls=":"))
ax.text(11.0, 4.9, "I: T$_0$ → B$_3$", size=7.5, color=INK2, ha="center")
label(10.7, 3.5,
      "pad layout schematic only (card gives label order,\nnot coordinates); no GDS, no optical image;\nT$_1$–T$_4$ dead; sr2/sr3 n.c. — one wired channel",
      size=7.8)

# ---- arrows between panels -------------------------------------------
for (x0, x1, txt) in [(3.6, 5.1, "laser cut\n(local heating —\nconversion risk\nat edges)"),
                      (6.9, 8.7, "stack (hBN pickup) · anneal · litho\n(metal deposition on region)\nall post-Raman, all\nABC→ABA risk classes")]:
    ax.add_patch(FancyArrowPatch((x0, 4.7), (x1, 4.7), arrowstyle="->",
                                 mutation_scale=16, color=INK2, lw=1.2))
    ax.text((x0 + x1) / 2, 5.35, txt, size=7.6, color=INK2, ha="center", va="bottom")

# ---- registration statement band -------------------------------------
band = FancyBboxPatch((0.55, 0.35), 12.4, 1.75, boxstyle="round,pad=0.1",
                      facecolor="#f3f2ee", edgecolor=MUTED, lw=0.8)
ax.add_patch(band)
ax.text(0.85, 1.92, "Registration statement", size=9.5, color=INK, weight="bold", va="top")
ax.text(0.85, 1.55,
        "Metric anchors: 0 (no shared coordinate frame exists at any link — every link above is attestation or a schematic).  "
        "Registration uncertainty: unbounded;\ndomain scale: unknown (no Raman map in hand). "
        "Uncertainty ≳ domain scale at every link ⇒ Raman coverage of sr1 (B$_1$–B$_2$) is AT BEST PARTIAL —\n"
        "recorded as attested-covered, metrically unverifiable. Transport coverage outside the sr1 footprint: uncovered (sr2/sr3 n.c.). "
        "No interpolation performed.",
        size=8.3, color=INK2, va="top", linespacing=1.5)

ax.text(0.55, 0.16, "vti-02 fusion 2026-08-27 · record: artifacts/registration-vti-02.md · "
        "sources: inputs/raman.md (attestations), inputs/device_card.md (contact map)",
        size=7, color=MUTED, va="top")

fig.savefig("/data/sharpelab/hera-data/raman-vti-02-20260821-fusion/artifacts/registration-vti-02.png",
            bbox_inches="tight", facecolor=SURFACE)
print("wrote artifacts/registration-vti-02.png")
