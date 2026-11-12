#!/usr/bin/env python3
"""Bar charts, per run: S_claim and the three per-type accuracies, scores of record beside a
second rater. usage: hera_rater_bars.py <pool> <rater> [out]
Reads scores/<pool>.cards.csv (record, full pool), scores/<pool>.<rater>.cards.csv, and
raters/<rater>/manifest.json. Writes raters/<rater>/bars.png and prints the plotted table.
With [out] (a .pdf or .png path) it writes there instead, with the paper's session names and
"first/second expert" wording in place of run keys and rater ids.

Three series: the record on its full pool, the record restricted to the rater's subset, and
the rater on that subset. Aggregation is the ingest's (card values, verdict weight 2 in
S_claim), so the record-full bars equal scores/<pool>.runs.csv and the two subset series are
like-for-like. Not the pre-declared agreement quantities — those are hera_agree.py's."""
import csv, json, sys, pathlib
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent; pool, rater = sys.argv[1], sys.argv[2]
out = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None
rd = here / 'raters' / rater
RUNS = ['T1B', 'T1D', 'T1A', 'T1E', 'T1C', 'T1F']        # corpus arms first, then no-corpus
NOCORPUS = {'T1C', 'T1F'}
PAPER = {'T1B': 'Fable + C\n(device 1)', 'T1D': 'Fable + C\n(1)', 'T1A': 'Fable + C\n(2)',
         'T1E': 'Opus + C', 'T1C': 'Fable\nno C', 'T1F': 'Opus\nno C'}
TYPES = ['inference', 'decision', 'verdict']
W = {'verdict': 2}
SERIES = ([('first expert, all claims', '#2a78d6'), ('first expert, subset', '#1baf7a'), ('second expert, subset', '#eb6834')] if out
          else [('record, full pool', '#2a78d6'), ('record, subset', '#1baf7a'), (f'{rater}, subset', '#eb6834')])

def cards(p):
    return [r for r in csv.DictReader(open(p)) if not int(r['hidden']) and r['value'] not in ('', None)]
keep = set(json.load(open(rd / 'manifest.json'))['card_ids'])
rec = cards(here / 'scores' / f'{pool}.cards.csv')
data = [rec, [r for r in rec if r['card'] in keep], cards(here / 'scores' / f'{pool}.{rater}.cards.csv')]

def agg(rows, run):
    rs = [r for r in rows if r['run'] == run]
    out = {}
    num = sum(W.get(r['type'], 1) * float(r['value']) for r in rs); den = sum(W.get(r['type'], 1) for r in rs)
    out['S_claim'] = (num / den if den else float('nan'), len(rs))
    for t in TYPES:
        v = [float(r['value']) for r in rs if r['type'] == t]
        out[t] = (sum(v) / len(v) if v else float('nan'), len(v))
    return out
A = [{run: agg(rows, run) for run in RUNS} for rows in data]

# table first: the aqua series sits under 3:1 on the surface, so the numbers travel with the chart
hdr = ['run'] + [f'{m} [{s.split(",")[0]}{"/sub" if "subset" in s else ""}]' for m in ['S_claim'] + TYPES for s, _ in SERIES]
print(','.join(hdr))
for run in RUNS:
    print(','.join([run] + [f'{A[i][run][m][0]:.3f} (n={A[i][run][m][1]})' for m in ['S_claim'] + TYPES for i in range(3)]))

plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': '#333', 'xtick.color': '#333', 'ytick.color': '#333'})
fig, axes = plt.subplots(*((2, 2) if out else (1, 4)), figsize=(8.5, 6) if out else (13, 3.6), sharey=True)
axes = axes.ravel()
bw, x = 0.26, range(len(RUNS))
for ax, m in zip(axes, ['S_claim'] + TYPES):
    for i, (label, color) in enumerate(SERIES):
        vals = [A[i][run][m][0] for run in RUNS]
        ax.bar([xi + (i - 1) * (bw + 0.02) for xi in x], vals, bw, color=color, label=label, linewidth=0)
        if m == 'verdict':   # n is 1–2 per run here; the bar is nearly a single card's value
            for xi, run in zip(x, RUNS):
                ax.text(xi + (i - 1) * (bw + 0.02), 0.02, str(A[i][run][m][1]), ha='center', va='bottom', fontsize=6.5, color='white')
    ax.set_title({'S_claim': 'claim score' if out else 'S_claim (verdict ×2)'}.get(m, f'{m} items'), fontsize=10, loc='left')
    ax.set_xticks(list(x)); ax.set_xticklabels([PAPER[r] for r in RUNS] if out else RUNS, fontsize=7 if out else 8)
    ax.set_ylim(0, 1.02); ax.yaxis.grid(True, color='#e6e5df', linewidth=0.6); ax.set_axisbelow(True)
    ax.axvline(3.5, color='#c3c2b7', linewidth=0.6, linestyle=(0, (3, 3)))
    if not out:
        ax.text(1.5, -0.2, 'corpus', ha='center', va='top', fontsize=7.5, color='#666', transform=ax.get_xaxis_transform())
        ax.text(4.5, -0.2, 'no corpus', ha='center', va='top', fontsize=7.5, color='#666', transform=ax.get_xaxis_transform())
for a in (axes[::2] if out else axes[:1]): a.set_ylabel('mean claim value (1 / 0.5 / 0)' if out else 'mean card value (1 / 0.5 / 0)')
fig.legend(*axes[0].get_legend_handles_labels(), loc='upper right' if not out else 'upper center', ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.99, 1.0) if not out else (0.5, 1.0))
if not out:
    fig.suptitle(f'Pass A per run — scores of record beside {rater} ({len(keep)}-card subset); verdict bars show n cards',
                 fontsize=10, x=0.01, ha='left')
fig.tight_layout(rect=(0, 0.02 if not out else 0, 1, 0.94 if not out else 0.95))
out = out or rd / 'bars.png'; fig.savefig(out, dpi=160); print(out)
