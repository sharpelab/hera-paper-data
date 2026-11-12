"""Figure 5: what N buys. Detectable difference against N, pooled and per model, with the cost per cut.

Numbers parsed from prereg-stats/power_budget.md and power_per_model.md (smoothed pilot, T = 8 h).
"""
import re
from style import *

MDE_K = (1.959964 + 0.841621) / 1.959964         # 80 % power at two-sided 5 %, in 95 % half-widths
N_PICK, NMAX = 20, 42
AX = [0.17, 0.30, 0.62]                          # left, bottom, width of the plot

budget, per_model = open(STATS + 'power_budget.md').read(), open(STATS + 'power_per_model.md').read()
cells = lambda line: [c.strip() for c in line.strip().strip('|').split('|')]
rows = [cells(l) for l in budget.split('## Precision, power and cost')[1].split('##')[0].splitlines()
        if l.startswith('| smoothed')]
HW = {int(r[1]): float(r[6]) for r in rows}      # 95 % half-width of the headline Δ
HEAD = {int(r[1]): float(r[7]) for r in rows}    # its detectable difference
USD = {int(r[1]): float(r[10]) for r in rows}
MODEL = {int(cells(l)[1]): MDE_K * float(np.median([float(x) for x in re.findall(r'\w+ ([\d.]+) \(', cells(l)[2])]))
         for l in per_model.splitlines() if l.startswith('| smoothed')}   # median over the six models
PILOT = sorted(float(cells(l)[2]) for l in budget.split('## Population Δ')[1].split('##')[0].splitlines()
               if l.startswith(('| smoothed', '| pooled')))

fig, ytop = page(10.5, 6.9, f'What N buys: 20 fans per cell detects a corpus effect of {HEAD[N_PICK]:.2f}',
                 'The smallest difference in the share of fans supporting the call within 8 h that the matrix detects '
                 'with 80 % power\n(two-sided 5 %), against the number of fans per cell. Simulated from the development '
                 'set, with censoring and the 2N cap.')
ax = fig.add_axes(AX + [ytop - AX[1] - 0.03])
n = np.linspace(4, NMAX, 200)
ax.axhspan(*PILOT, color=AQUA, alpha=0.30, lw=0)
ax.text(NMAX - 0.4, PILOT[1] + 0.012, f"the pilot's Δ, +{PILOT[0]:.2f} to +{PILOT[1]:.2f}: one or two episodes\n"
        'per cell, not the number to plan on', fontsize=8.5, color=INK2, va='bottom', ha='right', linespacing=1.35)
for d, col, lab in ((MODEL, MUTED, 'one model\'s Δ, or a\ncontrast between models'),
                    (HEAD, BLUE, 'the headline Δ\n(mean over six models)')):
    ax.plot(n, d[N_PICK] * np.sqrt(N_PICK / n), color=col, lw=1.2, alpha=0.55, zorder=2)
    ax.plot(list(d), list(d.values()), color=col, lw=2, solid_capstyle='round', zorder=3)
    ax.scatter(list(d), list(d.values()), s=64, fc=col, ec=SURF, lw=1.6, zorder=4)
    ax.text(NMAX + 0.6, d[N_PICK] * np.sqrt(N_PICK / NMAX), lab, fontsize=9, color=INK2, va='center',
            linespacing=1.35, clip_on=False)
for k, v in HEAD.items():
    ax.text(k - 0.5, v - 0.018, f'{v:.2f}', fontsize=9.5, color=INK, ha='right', va='top',
            fontweight='bold' if k == N_PICK else 'normal')
for k, v in MODEL.items():
    ax.text(k + (-0.5 if k == N_PICK else 0.5), v + 0.018, f'{v:.2f}', fontsize=9.5, color=INK,
            ha='right' if k == N_PICK else 'left', va='bottom')
YMAX = 0.56
ax.axvline(N_PICK, color=INK, lw=1.0, ymax=0.91, zorder=1)
ax.text(N_PICK, 0.92 * YMAX, 'N = 20, the plan', fontsize=9.5, color=INK, ha='center', va='bottom', fontweight='bold')
ax.text(NMAX - 0.4, 0.035, 'thin lines: 1/√N through N = 20, not simulated', fontsize=8.5, color=MUTED, va='center',
        ha='right')
ax.set_xlim(3, NMAX); ax.set_ylim(0, YMAX)
ax.set_yticks(np.arange(0, 0.51, 0.1))
ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.set_xticks([5, 10, 20, 30, 40])
ax.set_xlabel('N, fans per cell')
ax.set_ylabel('detectable difference in share (80 % power)')

# cost and precision at the simulated N, aligned under the axis
tb = fig.add_axes([AX[0], 0.165, AX[2], 0.075], sharex=ax); tb.axis('off'); tb.set_ylim(0, 1)
for y, lab, val in ((0.78, 'expected cost per cut', lambda k: f'${10 * round(USD[k] / 10):,}'),
                    (0.22, '95 % half-width of Δ', lambda k: f'{HW[k]:.2f}')):
    fig.text(AX[0] - 0.012, 0.165 + 0.075 * y, lab, fontsize=8.5, color=INK2, ha='right', va='center')
    for k in HEAD:
        tb.text(k, y, val(k), fontsize=9.5, color=INK, ha='center', va='center',
                fontweight='bold' if k == N_PICK else 'normal')
foot(fig, 'Smoothed pilot; the per-model line is the median over the six models (GPT-6 Astra is the widest: its corpus '
     'cell censors most episodes). Cost counts censored episodes.\nThe secondary cut runs a fixed 48 episodes. The pilot '
     'pools smoke runs of models outside the matrix.\nSource: prereg-stats/power_budget.md and power_per_model.md '
     '(400 simulations × 500 bootstraps).', y_in=0.10, dev=True)
save(fig, 'fig5_power.png')
print('HEAD', HEAD, 'HW', HW, 'USD', USD, 'MODEL', {k: round(v, 3) for k, v in MODEL.items()}, 'PILOT', PILOT)
