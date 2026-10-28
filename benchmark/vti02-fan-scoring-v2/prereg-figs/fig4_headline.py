"""Figure 4: from fans to the headline. Dev fans at (hours, P(call)) and the share-within-budget curve per arm."""
import csv
import re
from matplotlib.lines import Line2D
from style import *

EPISODES = STATS + 'episodes.csv'  # devset.py: the grader's box score
CUT_0822 = '3a4cf818'
T_HEAD, T_SENS, XMAX = 8.0, (6.0, 12.0), 20.0
fans = [dict(e, p_call=float(e['p_call']), hours=float(e['hours'])) for e in csv.DictReader(open(EPISODES))
        if e['cut'] == CUT_0822 and e['ending'] == 'fan']
with open(OUT + 'fig4_dev_fans.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'model', 'arm', 'matrix_model', 'p_call', 'hours'])
    for e in sorted(fans, key=lambda e: (e['corpus'], e['hours'])):
        w.writerow([e['key'], e['model'], e['corpus'], e['model'] in MATRIX, f"{e['p_call']:.3f}", f"{e['hours']:.2f}"])
arm = {a: np.array([[e['hours'], e['p_call'], e['model'] in MATRIX] for e in fans if e['corpus'] == a], float)
       for a in ARM}
share = lambda a, T: float((arm[a][:, 1] * (arm[a][:, 0] <= T)).mean())
n_out = sum(e['model'] not in MATRIX for e in fans)
out = sorted({MODEL_LABEL[e['model']] for e in fans if e['model'] not in MATRIX})
dev_d, dev_p = re.search(r'fans in both arms: ([+−-][\d.]+) \(permutation p ([\d.]+)\)',
                         open(STATS + 'power_budget.md').read()).groups()

fig, ytop = page(10.5, 8.2, 'The headline: what share of an arm\'s fans support the call within 8 hours?',
                 'A fan counts its P(call), the chance that its data support the call (independent detections of each tone, four making it), '
                 'if its measurement time\nfits the budget, and 0 if it does not. An arm\'s share is the mean over its '
                 'fans. Censored episodes do not enter.')
L, R = 0.085, 0.80
a1 = fig.add_axes([L, 0.505, R - L, ytop - 0.505 - 0.055])
a2 = fig.add_axes([L, 0.175, R - L, 0.255], sharex=a1)
for ax in (a1, a2):
    ax.axvspan(T_HEAD, XMAX, color=SOFT, alpha=0.55, lw=0)
    ax.axvline(T_HEAD, color=INK, lw=1.0, ymax=0.93)
    ax.set_xlim(0, XMAX); ax.set_ylim(-0.04, 1.06)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.grid(True); ax.set_axisbelow(True)

# (a) the fans
a1.set_title('Each dot is one fan an agent designed', loc='left', fontsize=10.5, color=INK, pad=8)
for a in ('corpus', 'none'):
    for mat, fc in ((0, SURF), (1, ARM[a])):
        d = arm[a][arm[a][:, 2] == mat]
        a1.scatter(d[:, 0], d[:, 1], s=46 if not mat else 78, fc=fc, ec=ARM[a] if not mat else SURF, lw=1.6 if not mat else 1.4,
                   zorder=3 + mat, clip_on=False)
a1.set_ylabel('P(call) of the fan')
a1.text(T_HEAD + 0.25, 0.60, 'over the 8 h budget:\nthese fans count 0', fontsize=9, color=INK2, va='center')
a1.text(T_HEAD - 0.25, 0.60, 'within budget:\na fan counts its P(call)', fontsize=9, color=INK2, va='center', ha='right')
plt.setp(a1.get_xticklabels(), visible=False)
mk = lambda fc, ec: Line2D([], [], ls='', marker='o', ms=8, mfc=fc, mec=ec, mew=1.5)
a1.legend([mk(ARM['corpus'], SURF), mk(ARM['none'], SURF), mk(INK2, SURF), mk(SURF, INK2)],
          [f"with corpus, {len(arm['corpus'])} fans", f"no corpus, {len(arm['none'])} fans", 'a model in the matrix',
           'smoke run of a model\noutside the matrix'],
          loc='upper left', bbox_to_anchor=(1.02, 1.0), fontsize=9, labelcolor=INK2, handletextpad=0.4,
          labelspacing=0.75, borderaxespad=0)

# (b) the share within budget
a2.set_title('The share of fans that support the call, as the budget grows', loc='left', fontsize=10.5, color=INK, pad=8)
T = np.linspace(0, XMAX, 2001)
for a in ('corpus', 'none'):
    a2.plot(T, [share(a, t) for t in T], color=ARM[a], lw=2, solid_capstyle='round', zorder=3)
    a2.scatter([T_HEAD], [share(a, T_HEAD)], s=70, fc=ARM[a], ec=SURF, lw=1.6, zorder=4)
    a2.text(XMAX + 0.3, share(a, XMAX), ARM_LABEL[a], fontsize=9, color=INK2, va='center', clip_on=False)
sc, sn = share('corpus', T_HEAD), share('none', T_HEAD)
a2.text(T_HEAD - 0.3, sc + 0.02, f'{sc:.2f}', fontsize=9.5, color=INK, ha='right', va='bottom', fontweight='bold')
a2.text(T_HEAD - 0.3, sn - 0.03, f'{sn:.2f}', fontsize=9.5, color=INK, ha='right', va='top', fontweight='bold')
a2.annotate('', (T_HEAD + 0.55, sc), (T_HEAD + 0.55, sn), arrowprops=dict(arrowstyle='<->', color=INK, lw=1.0, shrinkA=3, shrinkB=3))
a2.text(T_HEAD + 0.8, (sc + sn) / 2, f'gap read at 8 h: {sc - sn:+.2f}', fontsize=9.5, color=INK, va='center',
        fontweight='bold', bbox=dict(fc=SURF, ec='none', pad=1.5, alpha=0.9))
for t in T_SENS:
    a2.axvline(t, color=MUTED, lw=0.8, ymax=0.93)
    a2.text(t, 1.02, f'{t:.0f} h', fontsize=8, color=MUTED, ha='center', va='bottom')
a2.text(T_HEAD, 1.02, '8 h', fontsize=8.5, color=INK, ha='center', va='bottom', fontweight='bold')
a2.text(T_SENS[1] + 0.3, 0.06, '6 h and 12 h are reported as sensitivities', fontsize=8.5, color=INK2, va='center')
a2.set_ylabel('share of fans')
a2.set_xlabel('measurement time of the fan, from the rig cost model (hours)')
a2.set_xticks(range(0, 21, 2))
foot(fig, f'{len(fans)} fans at the 08-22 state; {n_out} come from smoke runs of models outside the matrix '
     f'({", ".join(out)}), at effort medium or high.\nThe arms are pooled over models here. '
     'The pre-registered Δ averages the within-model gaps over six models, with 20 fans per cell.\n'
     f'On the matrix models the dev-set Δ is {dev_d} (permutation p {dev_p}). Source: prereg-stats/episodes.csv (the grader\'s box score); table in '
     'fig4_dev_fans.csv.', dev=True)
save(fig, 'fig4_headline.png')
print({a: (len(arm[a]), round(share(a, 8), 3)) for a in arm}, 'outside matrix', n_out)
