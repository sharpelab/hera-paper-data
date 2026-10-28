#!/usr/bin/env python3
"""
vti-02 — Raman x transport fusion, supporting analysis.

Regenerates every figure and intermediate cited by ../fusion-verdict.md.

Inputs (read-only, the complete supplied set):
    ../inputs/transport-call.md
    ../inputs/raman.md
    ../inputs/20260824_ana.ipynb     (parsed, never executed)
    ../inputs/session_notes.md
    ../inputs/device_card.md

Outputs:
    ../artifacts/fig1-discrimination-matrix.png
    ../artifacts/fig2-stage-timeline.png
    ../artifacts/fig3-odds.png
    ../artifacts/fusion-intermediates.json

Run:  python3 analysis/fuse_vti02.py      (from the fusion root)

Nothing here re-measures the device. Part A re-derives consistency checks from
numbers the ana notebook already printed; part B is an *evidence inventory* of
the two source documents; part C is an explicit-judgement odds model whose
likelihood ratios are stated, not measured, and are swept for sensitivity.
"""

import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "inputs"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# ---------------------------------------------------------------- chart chrome
# dataviz reference palette (references/palette.md), light surface.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
# status palette (fixed) — always paired with an in-cell text label, never
# colour-alone.
ST = {
    "excluded":   "#d03b3b",   # critical
    "disfavoured": "#ec835a",  # serious
    "consistent": "#0ca30c",   # good
    "silent":     "#e1e0d9",   # neutral / no information
    "serious":    "#ec835a",
    "critical":   "#d03b3b",
    "good":       "#0ca30c",
}
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]   # categorical slots 1-3

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "font.size": 9,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "axes.grid": False,
})

# =============================================================== A. transport
# Every value below is quoted from the ana notebook's own printed output
# (cells 20, 24, 28, 32) or its markdown reads; this block only re-derives the
# cross-checks the fused verdict leans on.

T = {
    "R_CNP_min_ohm": 296.0,
    "R_CNP_max_ohm": 3074.0,
    "R_CNP_rise": 10.4,
    "D_lo": -0.0798,             # V/nm, most negative D reached on the CNP line
    "D_hi": +0.3068,
    "ctg_over_cbg_meas": 1.2737,
    "ctg_over_cbg_err": 0.0470,
    "ctg_over_cbg_prior": 1.1579,
    "Dmin_R_CNP": 0.000, "Dmin_R_CNP_err": 0.008,
    "Dmin_gap": +0.016, "Dmin_gap_err": 0.004,
    "fold_dD": [0.02, 0.04, 0.06, 0.08],
    "fold_ratio": [1.07, 1.01, 1.03, 0.96],
    "noise_floor_frac": 0.03,
    "Delta_D0_meV": -0.621, "Delta_D0_err": 0.166,
    "Delta_max_meV": +1.359, "Delta_max_err": 0.144, "Delta_max_at_D": +0.238,
    "dRdT_sign_change_D": +0.126,
    "flank_meV_per_Vnm": 7.9,
    "sdh_ratio_hi_contrast": [0.835, 0.834],
    "alpha_sdh": 1.199, "alpha_ladder": 1.166,
    "double_peak_rows_Vbg": [-0.15, -0.10, -0.05, +0.10, +0.15, +0.20, +0.25],
    "n_map_rows": 35,
    "electron_T_K": 8.0,
}

D_span = T["D_hi"] - T["D_lo"]
checks = {
    "D_span_Vnm": D_span,
    "neg_D_lever_arm_frac": abs(T["D_lo"]) / T["D_hi"],
    "Dmin_gap_as_frac_of_D_span": T["Dmin_gap"] / D_span,
    # do the two independent gap-minimum locators actually disagree?
    "Dmin_discrepancy_Vnm": T["Dmin_gap"] - T["Dmin_R_CNP"],
    "Dmin_discrepancy_sigma_joint": (T["Dmin_gap"] - T["Dmin_R_CNP"]) /
        math.hypot(T["Dmin_gap_err"], T["Dmin_R_CNP_err"]),
    "Dmin_discrepancy_sigma_activation_only":
        (T["Dmin_gap"] - T["Dmin_R_CNP"]) / T["Dmin_gap_err"],
    # fold ratios vs the stated 3 % per-point noise floor
    "fold_max_abs_dev": max(abs(r - 1.0) for r in T["fold_ratio"]),
    "fold_dev_in_noise_floors": max(abs(r - 1.0) for r in T["fold_ratio"]) /
        (math.sqrt(2) * T["noise_floor_frac"]),
    "alpha_route_agreement_pct": 100 * abs(T["alpha_sdh"] / T["alpha_ladder"] - 1),
    "ctg_ratio_prior_tension_sigma":
        (T["ctg_over_cbg_meas"] - T["ctg_over_cbg_prior"]) / T["ctg_over_cbg_err"],
    "double_peak_row_fraction": len(T["double_peak_rows_Vbg"]) / T["n_map_rows"],
    # how big a Bernal-like parallel shunt would flatten R_CNP at ~3 kohm?
    # R_meas = (R_gap^-1 + R_shunt^-1)^-1 ; if the true gapped channel were
    # >> 3 kohm the observed plateau IS the shunt, to within a few percent.
    "shunt_upper_bound_ohm": 3074.0,
    "shunt_vs_D0_channel": 3074.0 / 296.0,
}

# ============================================== B. evidence inventory per leg
# Objective, reproducible counts over the two source documents. The point is
# not the exact number but the order of magnitude of the gap between legs.

NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*\.?\d*\s*(?:%|Ω|ohm|meV|V/nm|nm|mV|V|T|K|"
                 r"×|x)\b", re.I)
ERRBAR = re.compile(r"±|\+/-")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def inventory(path: Path) -> dict:
    txt = path.read_text()
    return {
        "file": path.name,
        "chars": len(txt),
        "quantities_with_units": len(NUM.findall(txt)),
        "quoted_uncertainties": len(ERRBAR.findall(txt)),
        "iso_dates": len(DATE.findall(txt)),
    }


inv = {
    "raman": inventory(INP / "raman.md"),
    "transport_call": inventory(INP / "transport-call.md"),
}
# hand-coded structural facts, each checkable against the documents by eye
inv["raman"].update({
    "acquisition_date_stated": False,
    "instrument_stated": False,
    "wavelength_spot_size_stated": False,
    "spectra_or_map_files_in_hand": False,
    "positions_or_coordinates_stated": False,
    "layer_count_established_by_this_leg": False,
    "domain_area_or_fraction_stated": False,
    "build_stage_stated": True,          # "pre-stacking, on parent flake"
    "build_stage_internally_consistent": False,   # see the laser-cut remark
    "post_stacking_read_exists": False,
    "self_declared_strength": "strong",
})
inv["transport_call"].update({
    "acquisition_date_stated": True,
    "instrument_stated": True,
    "raw_runs_reanalysable": True,
    "positions_or_coordinates_stated": False,     # pad labels only, no map
    "layer_count_established_by_this_leg": False,  # alpha*g is degenerate
    "self_declared_strength": "moderate",
})

# ========================================== C. explicit-judgement odds model
# NOT a measurement. Likelihood ratios are stated judgements, written down so a
# reader can move them; the sweep shows which conclusions survive moving them.

HYP = ["ABCA", "ABCB", "ABAB"]

# Transport likelihoods, relative to ABCA = 1.
#   ABAB: two independent disqualifications (D-driven metal->insulator crossover;
#         one SdH tone where two are required). Set very small.
#   ABCB: symmetry point at D = 0 to +-0.008 / +0.016 +- 0.004 V/nm, but only
#         over |D| <= 0.10 V/nm on the -D side. Disfavoured, not excluded.
LR_TRANSPORT = {"ABCA": 1.0, "ABCB": 1.0 / 6.0, "ABAB": 1.0 / 300.0}
LR_TRANSPORT_SWEEP = {                       # (optimistic, pessimistic)
    "ABCB": (1.0 / 15.0, 1.0 / 3.0),
    "ABAB": (1.0 / 1000.0, 1.0 / 50.0),
}

# Raman leg, AS SUPPLIED. It reports an ABC-vs-ABA call on a pre-stacking parent
# flake with no spectra, no positions and no post-conversion read. Its bearing
# on the device is entirely through s = P(rhombohedral order survives stacking +
# anneal + cut + litho in the measured span). Within the rhombohedral family it
# reports at ABC granularity, which does not name ABCB at all:
#   L(ABCA) = L(ABCB) = s ;  L(ABAB) = 1 - s
# => LR(ABCA : ABCB) from the Raman leg is exactly 1, for every s.
S_GRID = np.linspace(0.05, 0.95, 91)
S_NOMINAL = 0.6


def raman_lr(s: float) -> dict:
    return {"ABCA": s, "ABCB": s, "ABAB": 1.0 - s}


def posterior(prior: dict, *lrs: dict) -> dict:
    w = {h: prior[h] for h in HYP}
    for lr in lrs:
        for h in HYP:
            w[h] *= lr[h]
    z = sum(w.values())
    return {h: w[h] / z for h in HYP}


PRIOR = {"ABCA": 1 / 3, "ABCB": 1 / 3, "ABAB": 1 / 3}

post = {
    "prior": PRIOR,
    "raman_only": posterior(PRIOR, raman_lr(S_NOMINAL)),
    "transport_only": posterior(PRIOR, LR_TRANSPORT),
    "fused": posterior(PRIOR, raman_lr(S_NOMINAL), LR_TRANSPORT),
}

# the headline invariance: ABCA:ABCB odds are untouched by the Raman leg, for
# any s, because the leg reports at a granularity blind to that split.
odds_ABCA_ABCB = {
    k: v["ABCA"] / v["ABCB"] for k, v in post.items()
}
s_sensitivity = [
    {"s": float(s),
     "fused_ABCA": posterior(PRIOR, raman_lr(s), LR_TRANSPORT)["ABCA"],
     "fused_ABCB": posterior(PRIOR, raman_lr(s), LR_TRANSPORT)["ABCB"],
     "fused_ABAB": posterior(PRIOR, raman_lr(s), LR_TRANSPORT)["ABAB"],
     "odds_ABCA_over_ABCB": posterior(PRIOR, raman_lr(s), LR_TRANSPORT)["ABCA"] /
                            posterior(PRIOR, raman_lr(s), LR_TRANSPORT)["ABCB"]}
    for s in S_GRID
]
lr_sensitivity = []
for lo_hi, tag in ((0, "optimistic"), (1, "pessimistic")):
    lr = dict(LR_TRANSPORT)
    lr["ABCB"] = LR_TRANSPORT_SWEEP["ABCB"][lo_hi]
    lr["ABAB"] = LR_TRANSPORT_SWEEP["ABAB"][lo_hi]
    p = posterior(PRIOR, raman_lr(S_NOMINAL), lr)
    lr_sensitivity.append({"transport_LR": tag, **p})

# ================================================= figure 1 — what separates what
ROWS = [
    ("T-a", "transport", "R_CNP rises 10.4x with D (296 -> 3074 ohm)",
     {"ABCA": "consistent", "ABCB": "consistent", "ABAB": "excluded",
      "ABCA+patch": "consistent"}),
    ("T-b", "transport", "gap minimum at D = 0.000 +- 0.008 / +0.016 +- 0.004 V/nm",
     {"ABCA": "consistent", "ABCB": "disfavoured", "ABAB": "silent",
      "ABCA+patch": "consistent"}),
    ("T-c", "transport", "metal -> insulator crossover at neutrality, dR/dT flips",
     {"ABCA": "consistent", "ABCB": "consistent", "ABAB": "excluded",
      "ABCA+patch": "consistent"}),
    ("T-d", "transport", "one SdH tone, f prop. to n; no second tone",
     {"ABCA": "consistent", "ABCB": "consistent", "ABAB": "excluded",
      "ABCA+patch": "silent"}),
    ("T-e", "transport", "R_CNP floor ~3 kohm; Delta_max 1.36 meV (10-100x low)",
     {"ABCA": "silent", "ABCB": "silent", "ABAB": "silent",
      "ABCA+patch": "consistent"}),
    ("T-f", "transport", "double-peaked neutrality in 7 of 35 map rows",
     {"ABCA": "silent", "ABCB": "silent", "ABAB": "silent",
      "ABCA+patch": "consistent"}),
    ("R-a", "Raman", "rhombohedral domain on the PARENT FLAKE, pre-stacking",
     {"ABCA": "consistent", "ABCB": "consistent", "ABAB": "disfavoured",
      "ABCA+patch": "silent"}),
    ("R-b", "Raman", "'domain survived the cut' (stage-inconsistent, no spectra)",
     {"ABCA": "consistent", "ABCB": "consistent", "ABAB": "disfavoured",
      "ABCA+patch": "silent"}),
    ("R-c", "Raman", "'expect the cut region to contain no ABA' (expectation)",
     {"ABCA": "silent", "ABCB": "silent", "ABAB": "silent",
      "ABCA+patch": "silent"}),
]
COLS = ["ABCA", "ABCB", "ABAB", "ABCA+patch"]
COL_LABEL = ["ABCA\n(rhombohedral)", "ABCB\n(mixed)", "ABAB\n(Bernal)",
             "ABCA + residual\npatch in the span"]

fig, ax = plt.subplots(figsize=(11.6, 5.4))
for i, (tag, leg, desc, verd) in enumerate(ROWS):
    y = len(ROWS) - 1 - i
    for j, c in enumerate(COLS):
        v = verd[c]
        ax.add_patch(Rectangle((j, y), 0.96, 0.92, facecolor=ST[v],
                               edgecolor=SURFACE, linewidth=2,
                               alpha=1.0 if v != "silent" else 0.9))
        ax.text(j + 0.48, y + 0.46, v if v != "silent" else "no information",
                ha="center", va="center", fontsize=7.4,
                color="#ffffff" if v in ("excluded", "consistent") else INK,
                weight="bold" if v != "silent" else "normal")
    ax.text(-0.25, y + 0.46, f"{tag}  {desc}", ha="right", va="center",
            fontsize=8.2, color=INK if leg == "transport" else INK2,
            style="normal" if leg == "transport" else "italic")

ax.set_xlim(-7.6, len(COLS))
ax.set_ylim(-0.9, len(ROWS) + 0.55)
for j, lab in enumerate(COL_LABEL):
    ax.text(j + 0.48, len(ROWS) + 0.12, lab, ha="center", va="bottom",
            fontsize=8.6, color=INK, weight="bold")
ax.text(-0.25, len(ROWS) + 0.12,
        "upright = transport leg      italic = Raman leg",
        ha="right", va="bottom", fontsize=8, color=MUTED)
ax.text(-7.5, -0.55,
        "Every Raman row is flat across ABCA and ABCB: the document reports an "
        "ABC/ABA call and never names ABCB,\nso it cannot move the one split the "
        "transport call is actually uncertain about. Rows T-e/T-f and the "
        "'+ residual patch'\ncolumn are where BOTH legs are empty.",
        ha="left", va="center", fontsize=8, color=INK2)
ax.set_title("vti-02 — which evidence line separates which stacking hypothesis  "
             "(channel sr1 = B_1-B_2)", fontsize=10.5, color=INK, loc="left",
             pad=26)
ax.axis("off")
fig.tight_layout()
fig.savefig(ART / "fig1-discrimination-matrix.png", dpi=200,
            bbox_inches="tight")
plt.close(fig)

# ============================================ figure 2 — stage & frame bridges
fig, (ax, bx) = plt.subplots(2, 1, figsize=(11.6, 6.4),
                             gridspec_kw={"height_ratios": [1.15, 1.0]})

stages = [
    ("Raman read\n(parent flake)", 0.5, SERIES[1]),
    ("stacking", 2.0, MUTED),
    ("anneal", 3.0, MUTED),
    ("cut", 4.0, MUTED),
    ("litho / gating", 5.0, MUTED),
    ("cooldown +\ntransport", 6.6, SERIES[0]),
]
ax.plot([0.2, 7.2], [0, 0], color=AXIS, lw=2, solid_capstyle="round", zorder=1)
for name, x, c in stages:
    ax.plot([x], [0], "o", ms=11, color=c, mec=SURFACE, mew=2, zorder=3)
    ax.text(x, 0.30, name, ha="center", va="bottom", fontsize=8.4, color=INK)
# the unbracketed conversion-risk window
ax.add_patch(Rectangle((1.4, -0.62), 4.2, 0.5, facecolor=ST["serious"],
                       alpha=0.20, edgecolor="none", zorder=0))
ax.text(3.5, -0.37, "four ABC -> ABA conversion-risk steps, NO Raman bracket "
                    "before or after any of them",
        ha="center", va="center", fontsize=8.4, color=INK)
ax.annotate("", xy=(4.15, 0.62), xytext=(0.85, 0.62),
            arrowprops=dict(arrowstyle="<->", color=ST["critical"], lw=1.6,
                            linestyle=(0, (4, 2))))
ax.text(2.5, 0.72, "stage ambiguity: header says pre-stacking, but "
                   "\"spectra look like noise due to the laser cutting\"\n"
                   "implies acquisition at or after the cut. Unresolvable "
                   "from the inputs.",
        ha="center", va="bottom", fontsize=8, color=ST["critical"])
ax.text(0.5, -0.95, "date: UNKNOWN\ninstrument: UNKNOWN\nfiles: not in hand",
        ha="center", va="top", fontsize=7.8, color=INK2)
ax.text(6.6, -0.95, "2026-08-24 11:36-16:53 PDT\nSR830 / VTI, T = 1.18-40 K\n"
                    "7 runs on disk, re-analysable",
        ha="center", va="top", fontsize=7.8, color=INK2)
ax.set_xlim(0, 7.4)
ax.set_ylim(-1.75, 1.35)
ax.axis("off")
ax.set_title("Temporal correspondence — ordering is known, the interval is not, "
             "and the conversion steps are unbracketed",
             fontsize=10, color=INK, loc="left")

# --- spatial frames
bx.axis("off")
bx.set_xlim(0, 10)
bx.set_ylim(0, 4)
bx.add_patch(Rectangle((0.3, 0.5), 3.4, 3.0, facecolor="none",
                       edgecolor=SERIES[1], lw=2))
bx.text(2.0, 3.15, "Raman frame", ha="center", fontsize=9, color=INK,
        weight="bold")
bx.text(2.0, 2.55, "parent-flake scan-inspector\ncoordinates\n"
                   "(flake 84135, URL not an input)",
        ha="center", va="center", fontsize=8, color=INK2)
bx.text(2.0, 1.35, "domain outline: not given\ndomain area: not given\n"
                   "cut outline: not given",
        ha="center", va="center", fontsize=8, color=ST["critical"])

bx.add_patch(Rectangle((6.3, 0.5), 3.4, 3.0, facecolor="none",
                       edgecolor=SERIES[0], lw=2))
bx.text(8.0, 3.15, "Transport frame", ha="center", fontsize=9, color=INK,
        weight="bold")
bx.text(8.0, 2.55, "bond-pad labels only\nB_1 = pad 12,  B_2 = pad 04",
        ha="center", va="center", fontsize=8, color=INK2)
bx.text(8.0, 1.35, "probe separation: not given\nchannel width: not given\n"
                   "optical image / GDS: not supplied",
        ha="center", va="center", fontsize=8, color=ST["critical"])

bx.annotate("", xy=(6.2, 2.0), xytext=(3.8, 2.0),
            arrowprops=dict(arrowstyle="-", color=ST["critical"], lw=2.4,
                            linestyle=(0, (2, 3))))
bx.text(5.0, 2.25, "NO REGISTRATION", ha="center", fontsize=9,
        color=ST["critical"], weight="bold")
bx.text(5.0, 1.72, "no optical image, no GDS,\nno build-step list, no map",
        ha="center", va="top", fontsize=7.8, color=INK2)
bx.set_title("Spatial correspondence — the two legs cannot be put on one "
             "coordinate frame with the supplied inputs",
             fontsize=10, color=INK, loc="left")
fig.tight_layout()
fig.savefig(ART / "fig2-stage-timeline.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ==================================================== figure 3 — the odds model
fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 4.2),
                             gridspec_kw={"width_ratios": [1.25, 1.0]})

order = ["prior", "raman_only", "transport_only", "fused"]
labels = ["flat prior", "+ Raman leg\n(as supplied)", "+ transport leg",
          "fused\n(both legs)"]
x = np.arange(len(order))
w = 0.26
for k, h in enumerate(HYP):
    vals = [post[o][h] for o in order]
    ax.bar(x + (k - 1) * w, vals, w - 0.03, color=SERIES[k], label=h,
           edgecolor=SURFACE, linewidth=2)
    for xi, v in zip(x + (k - 1) * w, vals):
        ax.text(xi, v + 0.015, f"{v:.2f}", ha="center", va="bottom",
                fontsize=7.6, color=INK2)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8.4)
ax.set_ylabel("posterior probability")
ax.set_ylim(0, 1.0)
ax.legend(frameon=False, fontsize=8.4, ncols=3, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, lw=0.8)
ax.set_axisbelow(True)
ax.set_title("Explicit-judgement odds model — stated LRs, not measurements\n"
             f"(Raman survival s = {S_NOMINAL:.2f}; transport LR "
             f"ABCB:ABCA = 1:6, ABAB:ABCA = 1:300)",
             fontsize=9.2, color=INK, loc="left")

s = np.array([r["s"] for r in s_sensitivity])
bx.plot(s, [r["odds_ABCA_over_ABCB"] for r in s_sensitivity], lw=2.5,
        color=SERIES[0])
bx.plot(s, [odds_ABCA_ABCB["transport_only"]] * len(s), lw=2.0, ls=(0, (5, 3)),
        color=SERIES[1])
bx.text(0.5, 6.35, "fused ABCA : ABCB odds", ha="center", fontsize=8.6,
        color=SERIES[0])
bx.text(0.5, 5.45, "transport leg alone", ha="center", fontsize=8.6,
        color=SERIES[1])
bx.set_xlabel("s = P(rhombohedral order survives stacking, anneal, cut, litho)")
bx.set_ylabel("odds ABCA : ABCB")
bx.set_ylim(0, 8)
bx.spines[["top", "right"]].set_visible(False)
bx.yaxis.grid(True, lw=0.8)
bx.set_axisbelow(True)
bx.set_title("The lines coincide for every s: the Raman leg as supplied\n"
             "carries zero information on the ABCA/ABCB split",
             fontsize=9.2, color=INK, loc="left")
fig.tight_layout()
fig.savefig(ART / "fig3-odds.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ==================================================================== dump
out = {
    "device": "vti-02",
    "channel": "sr1 = B_1-B_2 (the only four-terminal pair wired this cooldown)",
    "transport_quoted": T,
    "transport_derived_checks": checks,
    "evidence_inventory": inv,
    "odds_model": {
        "note": "explicit judgement, not measurement; LRs are stated so they "
                "can be moved by a reader",
        "hypotheses": HYP,
        "prior": PRIOR,
        "transport_LR_vs_ABCA": LR_TRANSPORT,
        "transport_LR_sweep": LR_TRANSPORT_SWEEP,
        "raman_LR_form": "L(ABCA)=L(ABCB)=s, L(ABAB)=1-s",
        "s_nominal": S_NOMINAL,
        "posteriors": post,
        "odds_ABCA_over_ABCB": odds_ABCA_ABCB,
        "s_sensitivity": s_sensitivity[::10],
        "transport_LR_sensitivity": lr_sensitivity,
    },
    "figures": [
        "artifacts/fig1-discrimination-matrix.png",
        "artifacts/fig2-stage-timeline.png",
        "artifacts/fig3-odds.png",
    ],
}
(ART / "fusion-intermediates.json").write_text(json.dumps(out, indent=2))

# ------------------------------------------------------------------- console
print("== transport derived checks ==")
for k, v in checks.items():
    print(f"  {k:42s} {v:.4f}")
print("\n== evidence inventory ==")
for leg, d in inv.items():
    print(f"  {leg}:")
    for k, v in d.items():
        print(f"      {k:42s} {v}")
print("\n== posteriors ==")
for k in order:
    print(f"  {k:16s} " + "  ".join(f"{h} {post[k][h]:.3f}" for h in HYP) +
          f"   | ABCA:ABCB = {odds_ABCA_ABCB[k]:.3f}")
print("\n  ABCA:ABCB odds over s in [0.05, 0.95]: "
      f"{min(r['odds_ABCA_over_ABCB'] for r in s_sensitivity):.4f} .. "
      f"{max(r['odds_ABCA_over_ABCB'] for r in s_sensitivity):.4f}"
      "   (flat => the Raman leg is uninformative on this split)")
print("\n== transport-LR sensitivity (fused) ==")
for r in lr_sensitivity:
    print(f"  {r['transport_LR']:12s} " +
          "  ".join(f"{h} {r[h]:.3f}" for h in HYP))
print("\nwrote:", ", ".join(out["figures"]),
      ", artifacts/fusion-intermediates.json")
