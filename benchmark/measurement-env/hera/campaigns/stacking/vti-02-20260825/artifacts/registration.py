"""Step-2 registration artifact for the vti-02 Raman x transport fusion.

Inputs actually available as frame bridges (nothing else was supplied):
  - inputs/device_card.md   : pad labels + bonding table + label convention
                              ("T = top arc L->R, B = left side then bottom L->R"),
                              wired roles. ORDINAL only: no metric pad coordinates,
                              no mesa outline, no GDS, no optical image, no scale.
  - inputs/20260824_ana.ipynb : electrical geometry only. Keyword scan
                              (artifacts/nb_checks.txt) finds no spatial content;
                              session_notes.md explicitly records that no Hall-bar
                              L/W is on the device card.
  - inputs/raman.md         : NO spot coordinates, NO region mask/raster, NO map,
                              NO image. One prose region only ("the cut region").

Consequence, and the point of this artifact: ZERO metric anchors exist on either
side, so no transform (rigid or otherwise) can be fitted, and the registration
uncertainty is not a number but UNBOUNDED. The artifact records the census, the
ordinal frame that IS derivable, and the coverage labels that follow.

Writes: artifacts/registration.json, artifacts/registration-frame.png
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

D = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260825-fusion")
ART = D / "artifacts"

# ---------------------------------------------------------------- census ----
census = {
    "device": "vti-02",
    "frame_bridges_requested_by_recipe": [
        "stage-registered video images inside the Raman files",
        "marker-frame optical images",
        "device GDS (pad/contact geometry)",
        "build-step list",
    ],
    "frame_bridges_supplied": {
        "raman_spot_or_region_coordinates": None,
        "raman_region_mask_or_raster": None,
        "raman_map_or_spectra_files": None,   # raman.md: "not yet in hand - pending from Ben"
        "stage_registered_video_images": None,
        "marker_frame_optical_images": None,
        "device_gds": None,
        "flake_or_cut_outline": None,
        "hall_bar_geometry_L_over_W": None,   # session_notes.md flags its absence explicitly
        "device_card_pad_table": "ordinal only (labels + bond pads + L->R convention)",
        "build_step_list": "prose, from raman.md + device_card.md gate stack; no dates",
    },
    "metric_anchors_available": 0,
    "transform_fitted": None,
    "anchor_variants": [],
    "registration_uncertainty": "UNBOUNDED / undefined - no anchor pair exists on "
                                "the Raman side, so no transform and no fit error "
                                "can be formed. Not a large number: no number.",
    "domain_scale_on_this_flake": "unknown - no Raman map was supplied. Literature "
                                  "expectation for exfoliated multilayer graphene is "
                                  "um-scale domains (Lui 2011, via raman-stacking-id.md). "
                                  "Unbounded uncertainty exceeds any um-scale domain "
                                  "trivially.",
    # ordinal frame, read off the device card's own label convention
    "ordinal_frame": {
        "convention_quoted": "label = position, T = top arc L->R, "
                             "B = left side then bottom L->R",
        "pads": {
            "T_0": {"bond_pad": 29, "edge": "top arc", "ordinal": 0, "alive": True,
                    "role": "source"},
            "T_1": {"bond_pad": 41, "edge": "top arc", "ordinal": 1, "alive": False,
                    "role": None},
            "T_2": {"bond_pad": 1,  "edge": "top arc", "ordinal": 2, "alive": False,
                    "role": None},
            "T_3": {"bond_pad": 42, "edge": "top arc", "ordinal": 3, "alive": False,
                    "role": None},
            "T_4": {"bond_pad": 43, "edge": "top arc", "ordinal": 4, "alive": False,
                    "role": None},
            "B_1": {"bond_pad": 12, "edge": "left side", "ordinal": 0, "alive": True,
                    "role": "sr1 Rxx (+)"},
            "B_2": {"bond_pad": 4,  "edge": "bottom L->R", "ordinal": 1, "alive": True,
                    "role": "sr1 Rxx (-)"},
            "B_3": {"bond_pad": 27, "edge": "bottom L->R", "ordinal": 2, "alive": True,
                    "role": "drain (sr0)"},
        },
        "caveat": "The edge assignment is a prose reading of the device card's label "
                  "convention, not a measured layout. It fixes ORDER around the mesa, "
                  "never position, spacing, or the mesa outline. No scale exists.",
    },
    "channels": [
        {
            "channel": "sr1 : B_1-B_2 (bond pads 12-04)",
            "kind": "four-terminal Rxx pair (the only live one this cooldown)",
            "transport_footprint": "the mesa segment between B_1 and B_2; extent unknown "
                                   "(no L/W, no outline)",
            "raman_coverage": "uncovered",
            "coverage_reason": "raman.md supplies no spot or region coordinates and no "
                               "mask/raster, so no Raman region can be placed on this "
                               "footprint. The document's device-level containment "
                               "assertion ('we cut out the rhombohedral domain and expect "
                               "the cut region to contain no ABA') is an unverified "
                               "expectation with no post-cut map and no cut outline - it "
                               "is an absence claim without a resolvability statement, "
                               "not a registration.",
            "composition_resolved": False,
        },
        {
            "channel": "T_0 -> B_3 (bond pads 29-27), two-terminal drive/drain path",
            "kind": "current path; carries no four-terminal stacking read",
            "transport_footprint": "diagonal across the mesa, top arc to bottom-right; "
                                   "strictly larger than the B_1-B_2 footprint",
            "raman_coverage": "uncovered",
            "coverage_reason": "same as above; additionally no stacking read exists on "
                               "this path for either leg to cover.",
            "composition_resolved": False,
        },
        {
            "channel": "sr2, sr3 (n.c.); T_1-T_4 (dead)",
            "kind": "not wired / not alive",
            "transport_footprint": None,
            "raman_coverage": "n/a - no channel",
            "coverage_reason": "device card: T_1-T_4 dead, sr2/sr3 not connected. This is "
                               "why no mosaic test exists on this cooldown.",
            "composition_resolved": False,
        },
    ],
    "raman_regions": [
        {
            "region": "R_cut - 'the cut region' (raman.md, prose)",
            "coordinates": None,
            "boundary": None,
            "stage": "pre-stacking, on the parent flake (acquisition date unknown)",
            "verdict_as_written": "ABC, 'strong' (labelled a lean by the document)",
            "localisable": False,
            "note": "The region is defined by an operation (a laser cut) whose outline "
                    "was not supplied. Whether the B_1-B_2 footprint lies inside it is "
                    "exactly the unregistered quantity.",
        }
    ],
    "stress_audit": "Shifting the registration by its uncertainty is vacuous here: with "
                    "no transform, every geometry-dependent conclusion flips under an "
                    "arbitrary shift. Every row whose conclusion depends on where the "
                    "Raman region sits is therefore REGISTRATION-LIMITED, not classified. "
                    "The sr1 row's fused verdict does not depend on registration - it is "
                    "carried by transport, whose footprint is the channel by definition - "
                    "so that row is stable.",
}
(ART / "registration.json").write_text(json.dumps(census, indent=2) + "\n")

# ---------------------------------------------------------------- figure ----
INK, MUTED, LIVE, DEAD, RAMAN = "#1f2430", "#6b7280", "#0f766e", "#b91c1c", "#7c3aed"
fig, ax = plt.subplots(figsize=(9.2, 6.4))
ax.set_xlim(0, 10); ax.set_ylim(-0.6, 7.2); ax.axis("off")

# schematic mesa - shape is arbitrary; only the pad ORDER around it is evidence
mesa = Polygon([(2.2, 1.5), (7.8, 1.5), (8.4, 3.4), (7.4, 5.1), (2.6, 5.1), (1.6, 3.4)],
               closed=True, facecolor="#eef2f7", edgecolor=MUTED, lw=1.2, zorder=1)
ax.add_patch(mesa)
ax.text(3.5, 3.9, "mesa outline NOT SUPPLIED\n(shape here is arbitrary)",
        ha="center", va="center", color=MUTED, fontsize=9, style="italic", zorder=2)

pads = {  # schematic placements honouring only the card's L->R ordinal convention
    "T_0": (2.9, 5.45), "T_1": (4.0, 5.62), "T_2": (5.0, 5.66),
    "T_3": (6.0, 5.62), "T_4": (7.1, 5.45),
    "B_1": (1.55, 3.0), "B_2": (3.6, 1.15), "B_3": (6.6, 1.15),
}
alive = {"T_0", "B_1", "B_2", "B_3"}
labels = {"T_0": "T_0 / 29\nsource", "T_1": "T_1 / 41", "T_2": "T_2 / 01",
          "T_3": "T_3 / 42", "T_4": "T_4 / 43", "B_1": "B_1 / 12\nsr1 +",
          "B_2": "B_2 / 04\nsr1 -", "B_3": "B_3 / 27\ndrain"}
for p, (x, y) in pads.items():
    on = p in alive
    ax.add_patch(Rectangle((x - 0.30, y - 0.20), 0.60, 0.40,
                           facecolor=LIVE if on else "white",
                           edgecolor=LIVE if on else DEAD,
                           lw=1.4, ls="-" if on else "--", zorder=3))
    va = "bottom" if y > 4 else "top"
    off = 0.28 if y > 4 else -0.28
    ax.text(x, y + off, labels[p], ha="center", va=va, fontsize=8.5,
            color=INK if on else DEAD, zorder=3)

# wired paths
ax.annotate("", xy=pads["B_2"], xytext=pads["B_1"],
            arrowprops=dict(arrowstyle="-", lw=3.0, color=LIVE), zorder=4)
ax.text(2.1, 1.95, "sr1  Rxx  B_1-B_2\ntransport verdict: ABAB (strong)",
        fontsize=9, color=LIVE, fontweight="bold", zorder=4)
ax.annotate("", xy=pads["B_3"], xytext=pads["T_0"],
            arrowprops=dict(arrowstyle="->", lw=1.6, color=MUTED, ls=(0, (5, 3))), zorder=4)
ax.text(5.6, 4.35, "T_0 -> B_3 drive path\n(no stacking read)", fontsize=8.5,
        color=MUTED, zorder=4)

# the Raman leg: unlocalisable
ax.add_patch(Rectangle((0.6, 0.55), 8.8, 5.9, facecolor=RAMAN, alpha=0.05,
                       edgecolor=RAMAN, lw=1.4, ls=(0, (2, 3)), hatch="//", zorder=0))
ax.text(5.0, 6.75,
        "Raman region R_cut  -  NO COORDINATES, NO MASK, NO MAP, NO IMAGE\n"
        "extent, boundary, and containment of B_1-B_2 are all UNREGISTERED",
        ha="center", va="center", fontsize=9.5, color=RAMAN, fontweight="bold", zorder=5)
ax.text(9.35, 2.0, "no scale bar:\nno metric frame exists\n0 anchors, no transform",
        ha="right", va="bottom", fontsize=8.5, color=RAMAN, style="italic", zorder=5)
ax.text(0.65, -0.55,
        "vti-02 registration artifact - ORDINAL frame only (device-card label convention: "
        "T = top arc L->R, B = left side then bottom L->R).\n"
        "Pad order is evidence; pad positions, spacing and mesa shape are not. "
        "Coverage of every channel by the Raman leg: UNCOVERED.",
        fontsize=8, color=INK, va="bottom", zorder=5)
fig.tight_layout()
fig.savefig(ART / "registration-frame.png", dpi=200, facecolor="white")
print("wrote", ART / "registration.json")
print("wrote", ART / "registration-frame.png")
