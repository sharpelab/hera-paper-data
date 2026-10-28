"""Figure 3: what gets graded. Dev-set endings per cell at the 08-22 state, one square per episode."""
import csv
from collections import Counter
from matplotlib.patches import FancyBboxPatch
from style import *

EPISODES = STATS + 'episodes.csv'
CUT_0822 = '3a4cf818'
ENDS = ('fan', 'probe', 'b0', 'none')                      # the counted endings, in drawing order
MARK = {'probe': 'S', 'b0': 'B', 'none': 'N'}
c = Counter((e['model'], e['corpus'], e['ending']) for e in csv.DictReader(open(EPISODES))
            if e['cut'] == CUT_0822 and e['ending'] in ENDS)
seen = {m for m, _, _ in c}
ROWS = [(m, True) for m in MATRIX] + [(m, False) for m in MODEL_LABEL if m in seen and m not in MATRIX]
tot = {a: Counter({k: sum(v for (m, arm, end), v in c.items() if arm == a and end == k) for k in ENDS}) for a in ARM}

PER_ROW = 12
W, H = 10.5, 3.55 + 0.44 * len(ROWS) + 1.8
fig, _ = page(W, H, 'What gets graded: a fan is graded, every other ending is counted',
              'One square per development-set episode at the 08-22 state, by the model that ran it. The headline reads the '
              'fans only;\nthe censored counts are reported per cell as a secondary result.', left=0.3 / W)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
SQ, GAP, RH = 0.25, 0.05, 0.44
XC = {'corpus': 2.35, 'none': 6.55}
NOTE = 3.15                                                # offset of the count from the column's left edge


def squares(x, y, n_by_end, arm):
    i = 0
    for end in ENDS:
        for _ in range(n_by_end.get(end, 0)):
            col, row = (i % PER_ROW, i // PER_ROW)
            px, py = x + col * (SQ + GAP), y - SQ / 2 - row * (SQ + GAP)
            ax.add_patch(FancyBboxPatch((px, py), SQ, SQ, boxstyle='round,pad=0,rounding_size=0.035',
                                        fc=ARM[arm] if end == 'fan' else HARD, ec='none'))
            if end != 'fan':
                ax.text(px + SQ / 2, py + SQ / 2 - 0.005, MARK[end], fontsize=8, color=INK, ha='center', va='center')
            i += 1


y0 = H - 2.05
for a in ARM:
    ax.scatter([XC[a] + 0.08], [y0 + 0.55], s=46, fc=ARM[a], ec='none')
    ax.text(XC[a] + 0.24, y0 + 0.55, ARM_LABEL[a], fontsize=10.5, color=INK, va='center', fontweight='bold')
y = y0
for k, (m, matrix) in enumerate(ROWS):
    if k == len(MATRIX):
        y -= 0.30
        ax.text(0.3, y + 0.34, 'smoke runs, models outside the matrix', fontsize=8.5, color=MUTED, va='center')
    if k == 0:
        ax.text(0.3, y + 0.34, 'models in the matrix', fontsize=8.5, color=MUTED, va='center')
    ax.text(0.3, y, MODEL_LABEL[m], fontsize=10, color=INK, va='center')
    for a in ARM:
        n = {e: c.get((m, a, e), 0) for e in ENDS}
        if sum(n.values()):
            squares(XC[a], y, n, a)
        else:
            ax.text(XC[a], y, 'no episode', fontsize=8.5, color=MUTED, va='center')
    y -= RH
y -= 0.12
ax.plot([0.3, W - 0.3], [y + 0.28, y + 0.28], color=GRID, lw=0.8)
ax.text(0.3, y - 0.17, 'all models', fontsize=10, color=INK, va='center', fontweight='bold')
for a in ARM:
    squares(XC[a], y, tot[a], a)
    n, cz = sum(tot[a].values()), sum(tot[a].values()) - tot[a]['fan']
    ax.text(XC[a], y - 0.42 - 0.30 * ((max(sum(t.values()) for t in tot.values()) - 1) // PER_ROW), f'{cz} of {n} censored', fontsize=10, color=INK, va='center', fontweight='bold')
y -= 1.05 + 0.30 * ((max(sum(t.values()) for t in tot.values()) - 1) // PER_ROW)
ax.text(0.3, y, 'Graded', fontsize=9, color=INK, va='center', fontweight='bold')
ax.text(3.35, y, 'Censored: counted, not graded', fontsize=9, color=INK, va='center', fontweight='bold')
for k, (end, lab) in enumerate((('fan', 'a Landau fan'), ('probe', 'a spot check'), ('b0', 'a B = 0 cell'),
                                ('none', 'no call'))):
    x = 1.05 if k == 0 else 5.75 + (k - 1) * 1.55
    ax.add_patch(FancyBboxPatch((x, y - SQ / 2), SQ, SQ, boxstyle='round,pad=0,rounding_size=0.035',
                                fc=INK2 if end == 'fan' else HARD, ec='none'))
    if end != 'fan':
        ax.text(x + SQ / 2, y - 0.005, MARK[end], fontsize=8, color=INK, ha='center', va='center')
    ax.text(x + SQ + 0.10, y, lab, fontsize=9, color=INK2, va='center')
foot(fig, 'Fan squares take the arm\'s colour. GPT-6 Astra with corpus: five low-field probes and one no-call, no fan. '
     'Fable 5.1, Opus 5.5 and GPT-6 Sol: one smoke episode per arm.\nHarness failures are excluded and not drawn. '
     'Source: prereg-stats/episodes.csv, labels by the model observed in the run.', left=0.3 / W, dev=True)
save(fig, 'fig3_endings.png')
print({a: dict(tot[a]) for a in ARM})
