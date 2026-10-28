"""Figure 6: the time flag. The five live vti-02 sessions as timelines from the autonomy grant.

Run times: $HERA_DATA/vti-noise/index/runs.parquet. Grant, call, outage and handoff times: the run record
(Primer, "HERA T1 no-corpus control - vti-02") and hera/campaigns/stacking/vti-02*/. Cut times: the archived
transcripts, at the case files' cut uuids.
"""
import pandas as pd
from matplotlib.patches import Patch
from style import *

PDT = 'US/Pacific'
ts = lambda s: pd.Timestamp('2026-' + s, tz=PDT)
GATE, SPOT, FAN, TSER = 'gate', 'spot', 'fan', 'tser'
COLOR = {GATE: '#b5b4ae', SPOT: VIOLET, FAN: AQUA, TSER: YEL}
LABEL = {GATE: 'gate sweeps and maps at B = 0', SPOT: 'SdH spot check (one density, field swept)',
         FAN: 'Landau fan', TSER: 'temperature series'}
# session dir, row label, arm, grant, markers [(time, label, filled)], run -> kind
S = [('20260821-vti-02', '08-21', 'Fable 5', 'corpus', ts('08-21 20:21:07'),
      [(ts('08-22 09:37:00'), 'final handoff 13.3 h, ABAB', False)],
      {5: SPOT, 8: FAN, **{r: TSER for r in range(9, 16)}}),
     ('20260822-vti-02', '08-22', 'Fable 5', 'corpus', ts('08-22 23:45:39'),
      [(ts('08-23 14:09:57'), 'call 14.4 h, ABAB', True)],
      {6: SPOT, 7: SPOT, 8: FAN, **{r: TSER for r in range(9, 15)}}),
     ('20260823-vti-02', '08-23', 'Fable 5', 'none', ts('08-23 20:27:25'),
      [(ts('08-24 02:18:46'), 'call 3.9 h active, ABAB', True)],
      {6: FAN, 7: FAN, **{r: TSER for r in range(8, 19)}}),
     ('20260824-vti-02', '08-24', 'Opus 5', 'none', ts('08-24 12:08:29'),
      [(ts('08-24 16:14:27'), 'call 4.1 h, ABCA (wrong)', True)],
      {4: FAN, 5: FAN, **{r: TSER for r in range(6, 13)}}),
     ('20260825-vti-02', '08-25', 'Opus 5', 'corpus', ts('08-24 17:17:10'),
      [(ts('08-24 22:49:11'), 'blind call 5.5 h, ABAB', True), (ts('08-25 04:51:43'), 'revised call 11.6 h', False)],
      {5: FAN, 6: FAN, 7: FAN, 8: FAN})]
OUTAGE = ('08-23', ts('08-23 22:38:03'), ts('08-24 00:37:24'))
CUTS = {'08-22': (pd.Timestamp('2026-08-23T12:11:33Z'), 'primary cut'),
        '08-24': (pd.Timestamp('2026-08-24T20:06:56Z'), 'secondary cut')}

runs = pd.read_parquet('/data/sharpelab/hera-data/vti-noise/index/runs.parquet')
hrs = lambda t, t0: (t - t0).total_seconds() / 3600

fig, ytop = page(11.0, 6.5, 'The time flag: live, the corpus sessions spent hours that the primary cut does not count',
                 'The five live vti-02 sessions from the autonomy grant to the stacking call. Bars are measurement runs. '
                 'The primary cut starts offline episodes\nafter the 08-22 spot checks, so both arms begin with those '
                 '3.6 h already spent.')
ax = fig.add_axes([0.155, 0.185, 0.815, ytop - 0.185 - 0.075])
BH = 0.30
spot_h = 0.0
for i, (sdir, day, model, arm, grant, marks, kinds) in enumerate(S):
    y = -i
    end = max(t for t, _, _ in marks)
    ax.plot([0, hrs(end, grant)], [y, y], color=AXIS, lw=0.8, zorder=1)
    r = runs[runs.path.str.startswith(f'zack/{sdir}/data/')].dropna(subset=['end_time'])
    for _, q in r.iterrows():
        k = kinds.get(int(q.run), GATE)
        x0, x1 = hrs(q.start_time, grant), hrs(q.end_time, grant)
        ax.barh(y, x1 - x0 - 0.03, left=x0 + 0.015, height=BH, color=COLOR[k], lw=0, zorder=3)
        if day == '08-22' and k == SPOT:
            spot_h += x1 - x0
    if day == '08-25':   # run 8 was specified by the operator after the blind call
        q = r[r.run.astype(int) == 8].iloc[0]
        ax.text((hrs(q.start_time, grant) + hrs(q.end_time, grant)) / 2, y - 0.30, 'fan specified by the operator',
                fontsize=8, color=INK2, ha='center', va='top')
    if day == OUTAGE[0]:
        x0, x1 = hrs(OUTAGE[1], grant), hrs(OUTAGE[2], grant)
        ax.barh(y, x1 - x0, left=x0, height=BH, fc='none', ec=MUTED, lw=0.8, hatch='////', zorder=2)
        ax.text((x0 + x1) / 2, y - 0.30, 'platform outage 2.0 h,\nnot counted', fontsize=8, color=INK2, ha='center',
                va='top', linespacing=1.3)
    for t, lab, filled in marks:
        x = hrs(t, grant)
        ax.plot([x, x], [y - 0.26, y + 0.26], color=INK, lw=1.4, zorder=5)
        ax.scatter([x], [y + 0.26], marker='v', s=42, fc=INK if filled else SURF, ec=INK, lw=1.2, zorder=6)
        ax.text(x + 0.15, y + 0.30, lab, fontsize=8.5, color=INK, va='bottom', fontweight='bold' if filled else 'normal')
    if day in CUTS:
        x = hrs(CUTS[day][0], grant)
        ax.plot([x, x], [y - 0.42, y + 0.42], color=INK, lw=1.0, ls=(0, (3, 2)), zorder=5)
        ax.text(x - 0.1, y - 0.30, CUTS[day][1], fontsize=8.5, color=INK, ha='right', va='top', fontweight='bold')
    ax.scatter([-0.45], [y + 0.10], s=46, fc=ARM[arm], ec='none', clip_on=False, zorder=5,
               transform=ax.transData)
    ax.text(-0.75, y + 0.10, f'{model}, {ARM_LABEL[arm]}', fontsize=9.5, color=INK, ha='right', va='center')
    ax.text(-0.75, y - 0.17, f'session {day}', fontsize=8, color=MUTED, ha='right', va='center')
# the 08-22 spot checks
q = runs[runs.path.isin(['zack/20260822-vti-02/data/6', 'zack/20260822-vti-02/data/7'])]
g = S[1][4]
x0, x1 = hrs(q.start_time.min(), g), hrs(q.end_time.max(), g)
ax.plot([x0, x0, x1, x1], [-1 + 0.24, -1 + 0.33, -1 + 0.33, -1 + 0.24], color=INK2, lw=0.9, zorder=4)
ax.text((x0 + x1) / 2, -1 + 0.38, f'spot checks, {spot_h:.1f} h', fontsize=8.5, color=INK, ha='center', va='bottom',
        fontweight='bold')
ax.set_xlim(-0.2, 16.2); ax.set_ylim(-4.75, 0.75)
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.set_xticks(range(0, 17, 2))
ax.xaxis.grid(True); ax.set_axisbelow(True)
ax.set_xlabel('hours since the autonomy grant')
ax.legend([Patch(fc=COLOR[k], ec='none') for k in (GATE, SPOT, FAN, TSER)], [LABEL[k] for k in (GATE, SPOT, FAN, TSER)],
          loc='lower left', bbox_to_anchor=(0.0, 1.005), ncol=4, fontsize=8.5, labelcolor=INK2, handlelength=1.2,
          handleheight=0.9, columnspacing=1.6, borderaxespad=0)
foot(fig, 'Live sessions, n = 1 per cell. Run times from the vti run index; grant, call and outage times from the run '
     'record and the wall-clock ledgers; cut times from the archived transcripts.\nThe secondary cut is the 08-24 state, '
     'before any field data.', y_in=0.10)
save(fig, 'fig6_time_flag.png')
print('08-22 spot checks', round(spot_h, 2), 'h')
