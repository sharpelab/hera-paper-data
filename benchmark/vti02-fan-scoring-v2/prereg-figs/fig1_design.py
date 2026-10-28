"""Figure 1: the pre-registered design at a glance (cuts x arms x models, N, censoring). No data."""
from style import *
from matplotlib.patches import FancyBboxPatch, Circle

N = 20
MODELS = [('Fable 5', True), ('Opus 5', True), ('Fable 5.1', False), ('Opus 5.5', False), ('GPT-6 Astra', False),
          ('GPT-6 Sol', False)]
W, H = 11.0, 8.5
fig, _ = page(W, H, 'The pre-registered matrix: corpus against no corpus, six models, two starting states',
              'Every episode is a fresh agent that picks up a frozen state of a live vti-02 session and designs the next '
              'measurement.\nAll models run at effort high. Each box is one cell: one model in one arm.', left=0.3 / W)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

X0, CW, GAP, RH = 2.15, 1.75, 0.12, 0.47      # first cell column, cell width, gap, row height
PANELS = [(X0, 'Primary cut: the 08-22 state', 'Both spot checks measured, none read; no fan drafted.',
           {'corpus': f'{N} fans', 'none': f'{N} fans'},
           f'Each cell runs until it holds {N} fans,\nstopping at {2 * N} episodes.',
           f'12 cells · 240 fans · at most {12 * 2 * N} episodes'),
          (X0 + 2 * CW + GAP + 1.05, 'Secondary cut: the 08-24 state (exploratory)',
           'Gate map read, no field data yet.',
           {'corpus': '3 episodes', 'none': '5 episodes'}, 'A fixed number of episodes per cell.',
           '12 cells · 48 episodes')]
YTOP = H - 2.45
for x0, head, state, cell, rule, total in PANELS:
    ax.text(x0, YTOP + 1.02, head, fontsize=11, fontweight='bold', color=INK, va='bottom')
    ax.text(x0, YTOP + 0.76, state, fontsize=9, color=INK2, va='bottom')
    for j, arm in enumerate(('corpus', 'none')):
        x = x0 + j * (CW + GAP)
        ax.add_patch(Circle((x + 0.09, YTOP + 0.33), 0.06, fc=ARM[arm], ec='none'))
        ax.text(x + 0.22, YTOP + 0.33, ARM_LABEL[arm], fontsize=9.5, color=INK, va='center')
        for i in range(len(MODELS)):
            y = YTOP - i * RH - RH + 0.05
            ax.add_patch(FancyBboxPatch((x, y), CW, RH - 0.10, boxstyle='round,pad=0,rounding_size=0.06',
                                        fc=ARM[arm], alpha=0.13, ec='none'))
            ax.text(x + CW / 2, y + (RH - 0.10) / 2, cell[arm], fontsize=9.5, color=INK, ha='center', va='center')
    yb = YTOP - len(MODELS) * RH - 0.10
    ax.text(x0, yb, rule, fontsize=9, color=INK2, va='top', linespacing=1.4)
    ax.text(x0, yb - 0.24 * (rule.count('\n') + 1) - 0.08, total, fontsize=9, color=INK, va='top', fontweight='bold')
for i, (name, live) in enumerate(MODELS):
    y = YTOP - i * RH - RH / 2
    ax.text(0.3, y + (0.07 if live else 0), name, fontsize=10, color=INK, va='center')
    if live:
        ax.text(0.3, y - 0.13, 'also ran live', fontsize=7.5, color=MUTED, va='center')

# how an episode ends
YE = 1.95
ax.plot([0.3, W - 0.3], [YE + 0.32, YE + 0.32], color=GRID, lw=0.8)
ax.text(0.3, YE, 'How an episode ends', fontsize=11, fontweight='bold', color=INK, va='center')
ENDS = [('A Landau fan', 'graded: P(call), hours, quality', INK, 'bold'),
        ('A spot check, a B = 0 cell, or no call', 'censored: counted per cell, not graded', INK, 'bold'),
        ('A harness failure', 'excluded and listed', INK, 'bold')]
for k, (what, fate, col, wt) in enumerate(ENDS):
    x = 0.3 + k * 3.55
    ax.text(x, YE - 0.38, what, fontsize=9.5, color=col, va='center', fontweight=wt)
    ax.text(x, YE - 0.62, fate, fontsize=9, color=INK2, va='center')
ax.text(0.3, 0.92, 'The headline, on the primary cut only', fontsize=11, color=INK, va='center', fontweight='bold')
ax.text(0.3, 0.62, 'The share of fans that support the stacking call within 8 h of measurement time. '
        'Δ is corpus minus no corpus, averaged over the six models.', fontsize=9.5, color=INK2, va='center')
ax.text(0.3, 0.22, 'Source: hera/docs/fan-design-grader.md § Statistics. Fable 5 and Opus 5 ran the five live sessions and '
        'carry the concordance check.', fontsize=8, color=MUTED, va='center')
save(fig, 'fig1_design.png')
