"""Fig. 4: the offline benchmark, the vti-02 fan-design matrix's analysis of record.

(a) P(call) within 8 h per model, with and without the corpus, bootstrap 95% intervals; (b) every fan on the
registered (acquisition time, P(call)) plane with per-arm frontiers; (c) each cell as a one-s.d. ellipse in
the two design metrics, an arrow from no corpus to corpus per model.

Reads benchmark/vti02-fan-scoring-v2/final/analysis.json. Drawn at \\textwidth for 1:1 placement.
Run from the repo root: uv run --project measurement-env python figures/fig4_benchmark.py [outdir]
Adapted from main_figure() in the paper repo's figures/fig5_panels.py.
"""
import json
import re
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe

import style

style.use()
DATA = style.ROOT / "benchmark/vti02-fan-scoring-v2/final/analysis.json"

ARROW = "#4a3aa7"  # third hue for none -> corpus arrows; validated against the pair
ARM = {"corpus": style.BLUE, "none": style.ORANGE}
ARM_LABEL = {"corpus": "full corpus", "none": "ablated corpus"}
MODELS = ["claude-fable-5", "claude-opus-5", "claude-fable-5-1", "claude-opus-5-5", "gpt-6-astra", "gpt-6-sol"]
MODEL_LABEL = {"claude-fable-5": "Fable 5", "claude-opus-5": "Opus 5", "claude-fable-5-1": "Fable 5.1",
               "claude-opus-5-5": "Opus 5.5", "gpt-6-astra": "GPT-6 Astra", "gpt-6-sol": "GPT-6 Sol"}
BUDGET_H = 8.0
FIG_W, FIG_H = style.TEXT_W, style.TEXT_W * 5.0 / 17.2   # the old 17.2 x 5.0 cm aspect
NOTE = plt.rcParams["legend.fontsize"]  # in-axes annotations at the legend size


def load():
    d = json.loads(DATA.read_text())
    fans = [e for e in d["episodes"] if e.get("ending") == "fan"]
    for f in fans:
        f["v"] = f["p_call"] * (f["hours"] <= BUDGET_H)
        m = re.search(r"\((invB|stitched|B)\)", f["field_axis"])
        f["grid"] = m.group(1) if m else "other"
    return d, fans


def cell(fans, model, arm):
    return [f for f in fans if f["model"] == model and f["arm"] == arm]


def boot_ci(xs, rng, n=4000):
    xs = np.asarray(xs)
    means = rng.choice(xs, (n, xs.size), replace=True).mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def frontier_hull(front):
    """Upper-left concave hull of the Pareto-front cells (cost ascending): the frontier attainable by mixing two
    cells' strategies, since expected cost and score are linear in the mix."""
    h = []
    for q in front:
        while len(h) >= 2:
            (x1, y1), (x2, y2) = h[-2], h[-1]
            if (x2 - x1) * (q[1] - y1) - (y2 - y1) * (q[0] - x1) >= 0:
                h.pop()
            else:
                break
        h.append(q)
    return h


def pareto_front(points):
    """Upper-left staircase: fans no other fan beats on both P(call) (higher) and hours (lower)."""
    pts = sorted(points, key=lambda p: (p[0], -p[1]))  # by hours, then P(call) descending
    front, best = [], -1.0
    for h, p in pts:
        if p > best:
            front.append((h, p))
            best = p
    return front


def main_figure(fans, out):
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(FIG_W, FIG_H),
                                  gridspec_kw={"left": 0.075, "right": 0.99, "top": 0.86, "bottom": 0.25, "wspace": 0.32})
    rng = np.random.default_rng(1)

    # (a) bars
    x = np.arange(len(MODELS))
    w = 0.36
    for k, arm in enumerate(("none", "corpus")):
        xs = x + (k - 0.5) * w
        means, lo, hi = [], [], []
        for m in MODELS:
            v = [f["v"] for f in cell(fans, m, arm)]
            means.append(np.mean(v))
            q0, q1 = boot_ci(v, rng)
            lo.append(means[-1] - q0)
            hi.append(q1 - means[-1])
        a.bar(xs, means, width=w * 0.94, color=ARM[arm], linewidth=0, zorder=2)
        a.errorbar(xs, means, yerr=[lo, hi], fmt="none", ecolor="k", elinewidth=0.6, capsize=1.5, zorder=3)
    a.set_xticks(x)
    a.set_xticklabels([MODEL_LABEL[m] for m in MODELS], color="k", rotation=35, ha="right", rotation_mode="anchor")
    a.set_ylabel(r"$P(\mathrm{call})$ within 8 h")
    a.set_ylim(0, 1.0)
    a.set_yticks([0, 0.5, 1])
    a.grid(axis="x", visible=False)
    a.tick_params(axis="x", which="both", length=0)

    # (b) the registered plane, every fan, per-arm frontier
    XMAX = 21
    b.axvline(BUDGET_H, color=style.MUTED, lw=0.6, ls=(0, (3, 2)), zorder=1)
    b.text(BUDGET_H, 1.02, "8 h budget", transform=b.get_xaxis_transform(), color=style.MUTED, fontsize=NOTE,
           ha="center", va="bottom")                     # above the frame, on the line
    for arm in ("none", "corpus"):
        fs = [f for f in fans if f["arm"] == arm]
        b.scatter([f["hours"] for f in fs], [f["p_call"] for f in fs], s=7, color=ARM[arm], alpha=0.5,
                  linewidths=0, zorder=3)
        hull = frontier_hull(pareto_front([(f["hours"], f["p_call"]) for f in fs]))
        b.plot([q[0] for q in hull] + [XMAX], [q[1] for q in hull] + [hull[-1][1]], color=ARM[arm], lw=1.0, zorder=4)
    b.set_xlim(0, XMAX)
    b.set_ylim(-0.05, 1.05)
    b.set_xlabel("acquisition time (h)")
    b.set_ylabel(r"$P(\mathrm{call})$")
    b.set_yticks([0, 0.5, 1])

    # (c) one-s.d. ellipses per cell, an arrow from none to corpus per model
    for m in MODELS:
        mu = {}
        for arm in ("none", "corpus"):
            xs = np.array([f["rows_fl"] for f in cell(fans, m, arm)])
            ys = np.array([f["span"] for f in cell(fans, m, arm)])
            mu[arm] = (xs.mean(), ys.mean())
            # no-corpus cells: a lighter fill and a firmer edge, so the large overlapping ones stay readable
            fill = 0.13 if arm == "corpus" else 0.05
            c.add_patch(Ellipse(mu[arm], 2 * xs.std(ddof=1), 2 * ys.std(ddof=1), facecolor=mcolors.to_rgba(ARM[arm], fill),
                                edgecolor=mcolors.to_rgba(ARM[arm], 0.7), lw=0.6, zorder=2))
        c.annotate("", xy=mu["corpus"], xytext=mu["none"],
                   arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.15", color=ARROW, lw=0.9,
                                   shrinkA=3, shrinkB=3), zorder=4)
        for arm in ("none", "corpus"):
            c.scatter(*mu[arm], s=14, color=ARM[arm], edgecolor="white", linewidths=0.5, zorder=5)
    place = {"claude-opus-5-5": ((-4, 2), "right", "bottom"), "claude-fable-5": ((-5, 4), "right", "center"),
             "claude-opus-5": ((-4, 1), "right", "top"), "claude-fable-5-1": ((5, -2), "left", "top"),
             "gpt-6-astra": ((9, 1), "left", "bottom"), "gpt-6-sol": ((3, -2), "left", "top")}
    for m in MODELS:
        xs = np.mean([f["rows_fl"] for f in cell(fans, m, "none")])
        ys = np.mean([f["span"] for f in cell(fans, m, "none")])
        off, ha, va = place.get(m, ((-3, 3), "right", "bottom"))
        c.annotate(MODEL_LABEL[m], (xs, ys), xytext=off, textcoords="offset points", fontsize=NOTE,
                   color="k", ha=ha, va=va, zorder=6,
                   path_effects=[pe.withStroke(linewidth=1.2, foreground="white")])   # a white halo over ellipses and arrows
    c.axvline(3, color=style.MUTED, lw=0.6, ls=(0, (3, 2)), zorder=1)
    c.text(3, 1.02, "3 points per period", transform=c.get_xaxis_transform(), color=style.MUTED, fontsize=NOTE,
           ha="center", va="bottom")                     # above the frame, on the line, as the 8 h budget in (b)
    # the better-fan direction, just right of the corpus cells
    c.annotate("", xy=(8.2, 4.5), xytext=(7.3, 3.6),
               arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.15", color="k", lw=0.8))
    c.text(7.3, 3.6, "better\nLandau fan", color="k", fontsize=NOTE, ha="center", va="top",
           linespacing=1.1)   # at the arrow's base
    # limits wide enough that no one-s.d. ellipse is cut
    c.set_xlim(-0.7, 10)
    c.set_ylim(-0.8, 5.3)
    c.set_xticks([0, 2, 4, 6, 8, 10])
    c.set_yticks([0, 1, 2, 3, 4, 5])
    c.set_xlabel("sampling rate (points per period)")
    c.set_ylabel("frequency span (bins)")

    handles = [Line2D([], [], marker="o", ls="", color=ARM[k], markersize=5, label=ARM_LABEL[k]) for k in ("corpus", "none")]
    a.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, handletextpad=0.4,
             columnspacing=1.5, borderaxespad=0.2)        # the strip above (a); it keys all three panels
    for ax, letter in ((a, "a"), (b, "b"), (c, "c")):
        style.panel_label(fig, ax, letter)
    style.save(fig, out)
    plt.close(fig)


if __name__ == "__main__":
    out = style.outdir(sys.argv)
    _, fans = load()
    main_figure(fans, out / "fig4-benchmark.pdf")
    print("wrote", out / "fig4-benchmark.pdf", "from", len(fans), "fans")
