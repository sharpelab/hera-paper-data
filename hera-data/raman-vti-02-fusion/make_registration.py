"""vti-02 Raman x transport fusion — Step 2 registration artifact.

Frame bridges actually supplied (brief): the device card's contact map (pad
labels + arc positions, no um), the ana notebook's geometry (gate-stack
thicknesses; the B_1-B_2 path topology: dual-gated channel + a TG-only series
segment outside the graphite back-gate footprint + Si-doped contact regions),
and the positions raman.md gives (none: no map, no spot/region coordinates, no
spot size, no cut outline). No optical image, no GDS, no stage-registered
video frame. The artifact is therefore TOPOLOGICAL: it places the wired
channel on the card's contact topology and records that the Raman region
cannot be placed in any coordinate frame.

Run: uv run --no-project --with numpy --with scipy --with matplotlib python make_registration.py
Outputs: registration.png, registration.json
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

here = Path(__file__).resolve().parent

# --- device card contact map (labels, pad numbers, liveness, roles) ---
# "T = top arc L->R, B = left side then bottom L->R"; positions are ordinal only.
pads = {
    "T_0": dict(pad="29", alive=True,  role="source (I in)",    xy=(1.0, 5.2)),
    "T_1": dict(pad="41", alive=False, role="dead",             xy=(2.5, 5.6)),
    "T_2": dict(pad="01", alive=False, role="dead",             xy=(4.0, 5.7)),
    "T_3": dict(pad="42", alive=False, role="dead",             xy=(5.5, 5.6)),
    "T_4": dict(pad="43", alive=False, role="dead",             xy=(7.0, 5.2)),
    "B_1": dict(pad="12", alive=True,  role="sr1 Rxx probe +",  xy=(0.3, 3.0)),
    "B_2": dict(pad="04", alive=True,  role="sr1 Rxx probe -",  xy=(2.2, 0.6)),
    "B_3": dict(pad="27", alive=True,  role="drain (sr0, I out)", xy=(5.8, 0.6)),
}

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw=dict(width_ratios=[1.25, 1]))

# ---- left: transport frame (topological) ----
ax.set_xlim(-3.6, 8.6); ax.set_ylim(-2.4, 6.6); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("vti-02 — transport frame (device card contact topology; NO µm scale exists)", fontsize=11)

flake = FancyBboxPatch((0.9, 1.3), 5.6, 3.3, boxstyle="round,pad=0.3,rounding_size=0.6",
                       fc="#e9f2e9", ec="#557755", lw=1.5, ls="-")
ax.add_patch(flake)
ax.text(3.7, -1.55, "device flake (green) — raman.md: 'the cut region' (asserted = the isolated rhombohedral domain)\n"
        "outline, size, orientation vs parent flake: UNKNOWN (no image / GDS / cut outline supplied)",
        ha="center", va="center", fontsize=8, color="#335533")

# graphite back-gate footprint: extent unknown; B_1-B_2 path is partly outside it (ana cell 15)
bg = Polygon([(2.0, 1.3), (6.5, 1.3), (6.5, 4.6), (2.0, 4.6)], closed=True,
             fc="none", ec="#444444", lw=1.2, ls="--", hatch="..", alpha=0.6)
ax.add_patch(bg)
ax.text(4.3, 2.95, "graphite BG footprint (dotted box)\nextent UNKNOWN; B_1–B_2 path partly\noutside it (TG-only series segment,\nana cells 15/21)",
        ha="center", va="center", fontsize=7.5, color="#444444", bbox=dict(fc="white", ec="none", alpha=0.85))

# current path T_0 -> B_3 and the sr1 probe pair B_1 - B_2
ax.annotate("", xy=pads["B_3"]["xy"], xytext=pads["T_0"]["xy"],
            arrowprops=dict(arrowstyle="->", lw=1.2, color="#aa3333", ls=":", shrinkA=14, shrinkB=14))
ax.text(6.0, 4.0, "dotted arrow: I = 10 nA, T_0 → B_3\n(path through flake UNKNOWN)", fontsize=7.5, color="#aa3333", ha="left")
# probed channel band (schematic): between B_1 and B_2 along the left/bottom edge
chan = Polygon([(0.75, 2.75), (1.25, 3.25), (2.5, 1.1), (1.9, 0.9)], closed=True,
               fc="#f4c2c2", ec="#aa3333", lw=1.5, alpha=0.8)
ax.add_patch(chan)
ax.text(-3.5, 1.4, "sr1 = B_1–B_2 (Rxx), red band:\nthe ONLY stacking-read region\nABAB strong (transport, now)\n"
        "region = dual-gated channel +\nTG-only series segment +\ncontact regions\n(shape/extent UNKNOWN)",
        fontsize=7.5, color="#aa3333", ha="left", va="center")

for lab, p in pads.items():
    x, y = p["xy"]
    c = Circle((x, y), 0.26, fc=("#ffd27f" if p["alive"] else "#d9d9d9"), ec=("#aa3333" if lab in ("B_1", "B_2") else "#333333"),
               lw=(2.0 if lab in ("B_1", "B_2") else 1.0))
    ax.add_patch(c)
    ax.text(x, y, lab, ha="center", va="center", fontsize=7.5, fontweight="bold")
    ax.text(x, y - 0.42, f"pad {p['pad']}\n{p['role']}", ha="center", va="top", fontsize=6.5,
            color=("#222222" if p["alive"] else "#888888"))
ax.text(4.0, 6.35, "top arc: T_0 … T_4 (L→R; only T_0 alive)", ha="center", fontsize=8, color="#555555")
ax.text(-3.5, 4.2, "left side: B_1\nbottom L→R: B_2, B_3", fontsize=8, color="#555555", va="center")

# ---- right: Raman frame (unplaceable) + coverage table ----
ax2.set_xlim(0, 10); ax2.set_ylim(0, 10); ax2.axis("off")
ax2.set_title("vti-02 — Raman frame (raman.md): NOT PLACEABLE", fontsize=11)
box = FancyBboxPatch((0.6, 5.9), 8.8, 3.6, boxstyle="round,pad=0.2", fc="#fff3e0", ec="#b36b00", lw=1.5, ls="--")
ax2.add_patch(box)
ax2.text(5.0, 9.1, "Raman region per raman.md: 'a domain of rhombohedral … subsequently isolated'", ha="center", fontsize=8.5, color="#7a4a00", fontweight="bold")
ax2.text(5.0, 7.6,
         "coordinates: NONE (no map, no spot/region positions, no region mask/raster)\n"
         "spot size / step / wavelength / power / date: NONE ('unknown, ask Ben')\n"
         "spectra / flakemap files: NOT IN HAND ('pending from Ben')\n"
         "stage stamp: pre-stacking, on parent flake — but 'survived the cutting process'\n"
         "and 'spectra look like noise due to the laser cutting' ⇒ stage fork: pre-cut vs post-cut\n"
         "parent-flake URL: not an input (not fetched)",
         ha="center", va="center", fontsize=8, color="#5a3a00")
ax2.text(5.0, 6.15, "registration uncertainty: UNBOUNDED (no frame bridge) — domain scale: UNKNOWN (µm-scale typical)",
         ha="center", fontsize=8.5, color="#b30000", fontweight="bold")

rows = [
    ("sr1 = B_1–B_2", "ABAB (strong)", "none placeable", "UNCOVERED", "registration-limited: prose asserts\nwhole device ⊂ rhomb. domain (unverifiable)"),
    ("rest of flake\n('cut region')", "— (not probed)", "none placeable", "n/a (no transport)", "Raman-asserted only; transport-uncovered"),
]
y = 5.2
ax2.text(0.4, y, "channel", fontsize=8, fontweight="bold"); ax2.text(2.6, y, "transport", fontsize=8, fontweight="bold")
ax2.text(4.4, y, "Raman coords", fontsize=8, fontweight="bold"); ax2.text(6.2, y, "coverage", fontsize=8, fontweight="bold")
ax2.plot([0.3, 9.7], [y - 0.25, y - 0.25], color="#333333", lw=0.8)
for r in rows:
    y -= 1.35
    ax2.text(0.4, y, r[0], fontsize=7.5, va="center"); ax2.text(2.6, y, r[1], fontsize=7.5, va="center")
    ax2.text(4.4, y, r[2], fontsize=7.5, va="center"); ax2.text(6.2, y, r[3], fontsize=7.5, va="center", fontweight="bold", color="#b30000")
    ax2.text(0.4, y - 0.55, r[4], fontsize=6.8, va="center", color="#555555")
ax2.text(5.0, 0.9,
         "Rule applied (fusion recipe Step 2 + brief): coverage that cannot be established is UNCOVERED —\n"
         "no interpolation; no reconstruction of the missing map. Stress shift over an unbounded uncertainty\n"
         "flips any covered/partial label ⇒ the coverage label is registration-limited.",
         ha="center", va="center", fontsize=7.5, color="#333333",
         bbox=dict(boxstyle="round", fc="#f5f5f5", ec="#999999"))

fig.suptitle("vti-02 registration artifact — topological only: the Raman leg supplies no coordinate frame", fontsize=12)
fig.tight_layout()
fig.savefig(here / "registration.png", dpi=160)

reg = {
    "device": "vti-02 (tetralayer graphene, VTI cooldown 2026-08-21/22)",
    "frame": "topological (device-card contact map); no um coordinate frame exists for either modality",
    "frame_bridges_supplied": {
        "device_card_contact_map": "pad labels/numbers + arc order (T top arc L->R, B left side then bottom L->R); no positions",
        "ana_notebook_geometry": "gate-stack thicknesses (t_tg 9.5 nm, t_bg 11 nm); B_1-B_2 path topology: dual-gated channel + TG-only series segment outside graphite BG footprint (cell 15) + Si-doped contact regions (cell 21)",
        "raman_positions": "none (no map, no spot/region coordinates, no spot size, no cut outline)",
        "optical_images": None, "gds": None, "stage_registered_video": None,
    },
    "anchors_fit": 0,
    "registration_uncertainty": "unbounded (no anchors); domain scale unknown (um-scale typical, N=3 statistics) => uncertainty >> domain scale",
    "channels": [
        {"channel": "sr1", "pair": "B_1-B_2", "source": "T_0", "drain": "B_3", "pads": {"B_1": "12", "B_2": "04", "T_0": "29", "B_3": "27"},
         "transport_verdict": "ABAB (strong)", "raman_region_overlap": "not placeable",
         "coverage": "uncovered", "coverage_note": "registration-limited: raman.md asserts in prose that the whole device is the isolated rhombohedral domain (would be 'covered' if established); unverifiable without a map, cut outline, or device image"},
        {"channel": "rest-of-flake", "pair": None, "transport_verdict": None, "raman_region_overlap": "asserted (whole 'cut region')",
         "coverage": "n/a (no transport read)", "coverage_note": "transport-uncovered; Raman leg inadmissible (no evidence/coordinates)"},
    ],
    "stress_audit": "uncertainty unbounded: any covered/partial label flips under the stress shift -> coverage label registration-limited; 'uncovered' is the floor and does not flip; mechanism class is set by Step-1 admissibility (single-modality) and does not depend on the coverage label",
    "artifact": "registration.png",
}
(here / "registration.json").write_text(json.dumps(reg, indent=2))
print("wrote", here / "registration.png", "and registration.json")
