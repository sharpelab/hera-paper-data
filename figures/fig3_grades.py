"""Fig. 3(b): the expert's grades of the five tetralayer sessions.

Upper axes: Pass A item accuracy by claim type (inference / decision / verdict). Lower axes: the two Pass B
grades (answers the brief / independence, the rubric's supervision question) on the four rubric positions a-d, labelled only better / worse.
Grouped corpus / no corpus; the pre-registered original leads the corpus group so the repeat sits beside it.
The verdict rests on one or two items per session.

Reads grading/scores/T1.runs.csv and grading/scores/passb.runs.csv. Panel (a), the session table, stays TikZ
(fig-matrix-table.tex) and draws its own letter with the same rule; this PDF carries (b) and is placed 1:1.
Run from the repo root: uv run --project measurement-env python figures/fig3_grades.py [outdir]
Replaces the TikZ chart fig-matrix-bars.tex.
"""
import csv
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import style

style.use()
SCORES = style.ROOT / "grading/scores"

# the five tetralayer sessions in drawing order: (grading run, model label, arm)
SESSIONS = [("T1D", "Fable 5\noriginal", "corpus"), ("T1A", "Fable 5\nrepeat", "corpus"), ("T1E", "Opus 5", "corpus"),
            ("T1C", "Fable 5", "no corpus"), ("T1F", "Opus 5", "no corpus")]
KINDS = [("inference_acc", "inference", "#6250d6"), ("decision_acc", "decision", "#1baf7a"),
         ("verdict_acc", "verdict", "#c98500")]
PASSB = [("final_disposition", "answers the brief", "#616161"), ("final_supervision", "independence", "#b8b8b8")]
GRADE = {"a": 1.0, "b": 2 / 3, "c": 1 / 3, "d": 0.0}
W, H = 0.45 * style.TEXT_W, 2.95


def rows(name):
    return {r["run"]: r for r in csv.DictReader(open(SCORES / name))}


def edge(c):
    rgb = np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    return rgb * 0.7


def main(out):
    t1, pb = rows("T1.runs.csv"), rows("passb.runs.csv")
    fig = plt.figure(figsize=(W, H))
    up = style.axes_in(fig, 0.86, 1.32, W - 0.93, 1.15)
    lo = style.axes_in(fig, 0.86, 0.50, W - 0.93, 0.50)   # 2.3 : 1, as in the TikZ chart (4.4 : 1.9)
    x = np.arange(len(SESSIONS)) + np.array([0, 0, 0, 0.35, 0.35])   # a gap between the arms
    bw = 0.26

    for k, (col, lab, c) in enumerate(KINDS):
        v = [float(t1[r][col]) for r, _, _ in SESSIONS]
        up.bar(x + (k - 1) * bw, v, width=bw * 0.92, color=c, edgecolor=edge(c), linewidth=0.3, label=lab, zorder=2)
    up.set_ylim(0, 1); up.set_yticks([0, 0.5, 1])
    up.set_ylabel("claim grade")
    up.set_xticks(x); up.set_xticklabels([])
    up.tick_params(axis="x", length=0)
    up.grid(axis="x", visible=False)
    up.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, handlelength=1.0, handletextpad=0.4,
              columnspacing=1.0, borderaxespad=0.2)

    for k, (col, lab, c) in enumerate(PASSB):
        v = [max(GRADE[pb[r][col]], 0.012) for r, _, _ in SESSIONS]   # F = 0 drawn as a stub so the pair shows
        lo.bar(x + (k - 0.5) * bw, v, width=bw * 0.92, color=c, edgecolor=edge(c), linewidth=0.3, label=lab, zorder=2)
    lo.set_ylim(0, 1); lo.set_yticks([0, 1 / 3, 2 / 3, 1]); lo.set_yticklabels(["worse", "", "", "better"])
    lo.set_ylabel("session\ngrade")
    lo.set_xticks(x); lo.set_xticklabels([m for _, m, _ in SESSIONS], color="k")
    lo.tick_params(axis="x", length=0)
    lo.grid(axis="x", visible=False)
    lo.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, handlelength=1.0, handletextpad=0.4,
              columnspacing=1.0, borderaxespad=0.2)
    for ax in (up, lo):
        ax.set_xlim(x[0] - 0.55, x[-1] + 0.55)

    for ax in (up, lo):   # full | ablated divider, through the gap between the arms
        ax.axvline((x[2] + x[3]) / 2, color=style.MUTED, lw=0.6, ls=(0, (3, 2)), zorder=1)
    # the arm brackets under the model names
    tr = lo.get_xaxis_transform()
    hin = lo.get_position().height * H
    yb, yt = -(26 / 72) / hin, -(28 / 72) / hin       # bracket and its label, in points below the axis
    for i0, i1, arm in ((0, 2, "full corpus"), (3, 4, "ablated corpus")):
        lo.plot([x[i0] - 0.4, x[i1] + 0.4], [yb, yb], color=style.MUTED, lw=0.6, transform=tr, clip_on=False)
        lo.text((x[i0] + x[i1]) / 2, yt, arm, transform=tr, ha="center", va="top", fontweight="bold",
                fontsize=plt.rcParams["legend.fontsize"], color="k")
    # both y labels on one line, 4 pt left of the widest tick labels (better / worse)
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    x0 = min(t.get_window_extent(r).x0 for t in lo.get_yticklabels() if t.get_text())
    ax0 = lo.get_window_extent(r).x0
    for ax in (up, lo):
        ax.yaxis.set_label_coords((x0 - 4 / 72 * fig.dpi - ax0) / lo.get_window_extent(r).width, 0.5)
        ax.yaxis.label.set_ha("center"); ax.yaxis.label.set_va("bottom")
    style.panel_label(fig, up, "b")
    style.save(fig, out)
    plt.close(fig)


if __name__ == "__main__":
    out = style.outdir(sys.argv)
    main(out / "fig3-grades.pdf")
    print("wrote", out / "fig3-grades.pdf")
