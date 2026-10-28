"""f2_registration.py — the registration artifact for the vti-01 fusion.

One stage-µm frame carrying everything that CAN be registered:
  panel A: video 002 (pre-pickup) + map-003 region labels (labels_pre)
  panel B: video 004 (post-pickup) + map-005 region labels (labels_post)
  panel C: the transport channels — topology-only device schematic,
           explicitly NOT registered (no stage↔device bridge in inputs).

Outputs: registration.png, registration.json.
Also prints a quantitative orientation/overlay check (video gray sampled
at region world-coords: sheet must be darker than background).
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Affine2D

V = np.load("fusion_videos.npz")
R = np.load("inputs/regions.npz", allow_pickle=True)
x_um, y_um = R["x_um"], R["y_um"]

# identity hues (validated): ABC blue, ABA orange; context in neutrals
C_ABC, C_ABA = "#2a78d6", "#eb6834"
GRAY_EDGE, GRAY_WEDGE, GRAY_GRAPHITE = "#b8b6ae", "#8a887f", "#55534c"
INK, INK2 = "#0b0b0b", "#52514e"
SURF = "#fcfcfb"

LABEL_COLOR = {1: C_ABC, 2: C_ABA, 3: GRAY_WEDGE, 4: GRAY_GRAPHITE,
               5: C_ABC, 6: C_ABA, 7: GRAY_EDGE}


def world_transform(tag):
    """pixel (col,row) -> stage µm, from the in-file WITec transform."""
    wo, sc, rot = V[f"wo{tag}"], V[f"scale{tag}"], V[f"rot{tag}"]
    M = rot[:2, :2] @ sc[:2, :2]
    return np.array([[M[0, 0], M[0, 1], wo[0]],
                     [M[1, 0], M[1, 1], wo[1]],
                     [0, 0, 1]])


def sample_video_at(tag, xw, yw):
    """video gray at world points (bilinear-free nearest lookup)."""
    A = np.linalg.inv(world_transform(tag))
    img = V[f"img{tag}"]
    p = A @ np.vstack([xw, yw, np.ones_like(xw)])
    c, r = np.round(p[0]).astype(int), np.round(p[1]).astype(int)
    ok = (c >= 0) & (c < img.shape[1]) & (r >= 0) & (r < img.shape[0])
    out = np.full(xw.shape, np.nan)
    out[ok] = img[r[ok], c[ok]]
    return out


# ---- quantitative overlay check: sheet pixels must be darker than bg ----
XX, YY = np.meshgrid(x_um, y_um)
for tag, lay in (("002", "labels_pre"), ("004", "labels_post")):
    L = R[lay]
    sheet = np.isin(L, [1, 2, 5, 6])
    bg = L == 0
    gs = sample_video_at(tag, XX[sheet], YY[sheet])
    gb = sample_video_at(tag, XX[bg], YY[bg])
    print(f"video {tag} vs {lay}: gray sheet {np.nanmean(gs):.1f} "
          f"vs background {np.nanmean(gb):.1f} (sheet darker => aligned)")

# ---------------------------------------------------------------- figure
fig, axes = plt.subplots(1, 3, figsize=(16.5, 6.2), facecolor=SURF)
fig.subplots_adjust(left=0.05, right=0.985, top=0.86, bottom=0.16, wspace=0.18)

XLIM = (-12085, -12018)
YLIM = (1258, 1310)

def draw_panel(ax, tag, lay, title):
    img = V[f"img{tag}"]
    tr = Affine2D(world_transform(tag)) + ax.transData
    ax.imshow(img, cmap="gray", origin="upper",
              extent=(0, img.shape[1], img.shape[0], 0),
              transform=tr, interpolation="bilinear",
              vmin=np.percentile(img, 1), vmax=np.percentile(img, 99))
    L = R[lay]
    rgba = np.zeros(L.shape + (4,))
    for k, col in LABEL_COLOR.items():
        m = L == k
        rgba[m] = matplotlib.colors.to_rgba(col, alpha=0.5)
    ax.imshow(rgba, origin="lower", interpolation="nearest",
              extent=(x_um[0] - .25, x_um[-1] + .25, y_um[0] - .25, y_um[-1] + .25))
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.set_xlabel("stage x (µm)", color=INK2, fontsize=9)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_color("#d8d6cf")
    # 10 µm scale bar
    ax.plot([-12082, -12072], [1260.5, 1260.5], color=INK, lw=2)
    ax.text(-12077, 1262, "10 µm", color=INK, fontsize=8, ha="center")

draw_panel(axes[0], "002", "labels_pre",
           "A  PRE-pickup — video 002 (19:55 UTC) + map-003 regions")
axes[0].set_ylabel("stage y (µm)", color=INK2, fontsize=9)
axes[0].annotate("wedge >3L", xy=(-12073.5, 1292.5), xytext=(-12083, 1302),
                 color=INK, fontsize=8,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
axes[0].annotate("graphite", xy=(-12068.6, 1265.1), xytext=(-12062, 1260.5),
                 color=INK, fontsize=8,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

draw_panel(axes[1], "004", "labels_post",
           "B  POST-pickup — video 004 (20:19 UTC) + map-005 regions")
axes[1].annotate("tombstone remnant\n(78% ABC)", xy=(-12040.6, 1278.9),
                 xytext=(-12030, 1300), color=INK, fontsize=8,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
axes[1].annotate("sheet here was PICKED UP\n~20:10–20:19 UTC\n(mixed ABA/ABC mosaic)",
                 xy=(-12065, 1290), color=INK2, fontsize=8, ha="center")

# ---- panel C: device frame, topology only, explicitly unregistered ----
ax = axes[2]
ax.set_facecolor(SURF)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_color("#d8d6cf"); s.set_linestyle("--")
ax.set_title("C  DEVICE FRAME — NOT REGISTERED to A/B", color=INK,
             fontsize=11, loc="left")

VERDICT = {"sr1": (C_ABA, 1.0, "sr1  B_SD–L4   ABA (strong, two-branch)"),
           "sr3": (C_ABA, 0.45, "sr3  L3–L2      ABA (consistent-with)"),
           "sr2": (GRAY_EDGE, 1.0, "sr2  L4–L1      uninformative")}
ax.text(5.0, 9.7, "No frame bridge in the inputs links this Hall bar to the\n"
        "stage frame of panels A/B — no optical image of the finished\n"
        "device, no GDS, no build-step testimony. Even whether the\n"
        "channel came from the picked-up sheet (A, mixed mosaic) or\n"
        "a later pickup of the remnant (B, ABC-dominant) is undetermined.",
        color=INK2, fontsize=8, ha="center", va="top")
# topology-only bar: contacts in device-card order, no geometry implied
bar_x = 3.0
ax.add_patch(FancyBboxPatch((bar_x - 0.55, 2.0), 1.1, 5.5,
                            boxstyle="round,pad=0.1", fc="#eceae4", ec=INK2))
ypos = {"T_SD": 7.3, "L_1": 6.35, "L_2": 5.4, "L_3": 4.45, "L_4": 3.5,
        "B_SD": 2.2}
for name, yy in ypos.items():
    ax.plot([bar_x - 0.95, bar_x - 0.55], [yy, yy], color=INK2, lw=1.5)
    ax.text(bar_x - 1.1, yy, name, ha="right", va="center", color=INK, fontsize=8)
segs = {"sr1": (ypos["B_SD"], ypos["L_4"]), "sr2": (ypos["L_4"], ypos["L_1"]),
        "sr3": (ypos["L_3"], ypos["L_2"])}
for i, (ch, (y0, y1)) in enumerate(segs.items()):
    col, al, _ = VERDICT[ch]
    xoff = bar_x + 0.9 + 0.75 * i
    ax.plot([xoff, xoff], [y0, y1], color=col, alpha=al, lw=5,
            solid_capstyle="butt")
    ax.text(xoff, y0 + 0.25 if ch != "sr1" else y1 + 0.25, ch,
            color=INK, fontsize=8, ha="center", va="bottom")
for i, ch in enumerate(("sr1", "sr3", "sr2")):
    col, al, txt = VERDICT[ch]
    ax.plot([0.5, 0.9], [1.45 - 0.42 * i] * 2, color=col, alpha=al, lw=5)
    ax.text(1.05, 1.45 - 0.42 * i, txt, color=INK, fontsize=8, va="center")
ax.text(9.6, 0.15, "contact order per device card; lengths/positions\n"
        "schematic only (no geometry in inputs)", color=INK2, fontsize=7,
        ha="right", style="italic")

# shared legend
handles = [plt.Rectangle((0, 0), 1, 1, fc=matplotlib.colors.to_rgba(c, 0.6))
           for c in (C_ABC, C_ABA, GRAY_EDGE)]
fig.legend(handles, ["ABC-stacked (Raman)", "ABA-stacked (Raman)",
                     "edge / unassigned / uninformative"],
           loc="lower center", ncol=3, frameon=False, fontsize=9,
           bbox_to_anchor=(0.5, 0.01))
fig.suptitle("vti-01 registration — Raman regions on the stage frame (A, B); "
             "transport channels have no bridge into that frame (C)",
             color=INK, fontsize=12, x=0.05, ha="left")
fig.savefig("registration.png", dpi=170, facecolor=SURF)
print("wrote registration.png")

# ------------------------------------------------------- machine-readable
reg = {
    "frames": {
        "stage": "WITec stage µm (WorldOrigin coords), the common frame of panels A/B",
        "map003": "scan pixels of Scan LA 003 (pre-pickup survey)",
        "map005": "scan pixels of Scan LA 005 (post-pickup)",
        "video002/004/007": "video image pixels",
        "device": "finished vti-01 Hall bar (transport channels sr1/sr2/sr3)",
    },
    "edges": [
        {"from": "map003", "to": "stage", "how": "in-file TDSpaceTransformation",
         "uncertainty_um": 1.0,
         "basis": "003 vs 005 same-region agreement ~1 µm (Raman contract hedge 7)"},
        {"from": "map005", "to": "stage", "how": "in-file TDSpaceTransformation",
         "uncertainty_um": 1.0, "basis": "same"},
        {"from": f"video{t}", "to": "stage", "how": "in-file TDSpaceTransformation",
         "uncertainty_um": 2.0,
         "basis": "map005-on-video004 registration r=0.77, no flip (Raman contract); "
                  "sheet-darker-than-background check reproduced here (f2 stdout)"}
        if False else None,
    ],
    "video_to_stage": {
        tag: {"world_origin_um": V[f"wo{tag}"][:2].tolist(),
              "affine_2x3_px_to_um": world_transform(tag)[:2].tolist(),
              "um_per_px": float(V[f"scale{tag}"][0, 0]),
              "rotation_deg": float(np.degrees(np.arctan2(
                  V[f"rot{tag}"][1, 0], V[f"rot{tag}"][0, 0]))),
              "utc": str(V[f"utc{tag}"])}
        for tag in ("002", "004", "007")
    },
    "region_masks": "inputs/regions.npz (labels_pre/labels_post on x_um/y_um grid, "
                    "0.5 um/px, already in the stage frame)",
    "registration_uncertainty": {
        "raman_internal_um": "1-2 (map<->map and map<->video), vs 5-20 um domain "
                             "scale: domains are resolved within the Raman frame",
        "stage_to_device": "NO BRIDGE - unbounded. No transform exists; no channel "
                           "can be placed on any lamella. Source material of the "
                           "device (picked-up sheet vs remnant) also undetermined."
    },
    "timeline_attachment": {
        "map003_labels_pre": "2026-05-28 19:57 UTC, flake on substrate, PRE-pickup",
        "map005_labels_post": "2026-05-28 20:20 UTC, remnant after ~20:10-20:19 pickup",
        "transport_runs_0_18": "2026-08-18..20, finished encapsulated dual-gated "
                               "device at 1.2-15 K (call, ana cell 33)",
        "transport_runs_19_20": "2026-08-20, same cooldown (addendum, ana cell 38)",
        "gap": "~3 months of unrecorded processing (pickup -> encapsulation -> "
               "gating -> cooldown) between Raman evidence and transport evidence",
    },
}
reg["edges"] = [e for e in reg["edges"] if e]
for t in ("002", "004", "007"):
    reg["edges"].append(
        {"from": f"video{t}", "to": "stage", "how": "in-file TDSpaceTransformation",
         "uncertainty_um": 2.0,
         "basis": "map005-on-video004 registration r=0.77, no flip (Raman "
                  "contract); sheet-darker-than-background check reproduced "
                  "here (f2 stdout)"})
reg["edges"].append(
    {"from": "stage", "to": "device", "how": "NONE — no bridge supplied",
     "uncertainty_um": None,
     "basis": "no optical/GDS of finished device, no build-step testimony"})
with open("registration.json", "w") as fh:
    json.dump(reg, fh, indent=2)
print("wrote registration.json")
