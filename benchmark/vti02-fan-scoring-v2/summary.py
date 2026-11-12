"""Snapshot table for hera/docs/fan-design-scoring-v2.md: (n, F) band count and tone cells at
window floors, SNR score, estimated hours, for every fan-tier extraction at vti02-fan-design
and the live fans."""
import sys; sys.path.insert(0, sys.argv[1])
import warnings; warnings.filterwarnings('ignore')
import json, glob; from pathlib import Path
import roi, band
g = roi.g
latest = {}
for f in glob.glob('/data/sharpelab/hera-data/frontier/calibration/vti02-live/*/grades/fan-design/*/output.json') + \
         glob.glob('/data/sharpelab/hera-data/replay/runs/vti02-fan-design-*/*/episodes/*/grades/fan-design/*/output.json'):
    ep = f.split('/grades/')[0]
    if ep not in latest or f > latest[ep]: latest[ep] = f
print('| Episode | Field | n actual (1e12) × cols | cols / cells, own B_min | at 0.55 T | at 1.0 T | credit @0.55 T, 2→0 / 2→0.25 | I (nA) | τ (s) | SNR | est h |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for ep, f in sorted(latest.items()):
    doc = json.load(open(f))
    if doc.get('status') != 'extracted' or g.tier_of(doc) != 'fan': continue
    case = g.case_of(Path(ep)/'session'); B = g.field_axis(doc, case); sc = case.get('n_scale', 1.0)
    n = sc * g.columns(doc) / 1e12
    lab = ep.replace('/data/sharpelab/hera-data/','').replace('frontier/calibration/vti02-live/','live ').replace('replay/runs/vti02-fan-design-','').replace('/episodes/00','').replace('/episodes/0',' #')
    c = ['{} / {:.1f}'.format(*band.cells(B, n, x)[:2]) for x in (1e-3, 0.55, 1.0)]
    cr = [band.credit(B, n, 0.55, a) for a in (0.0, 0.25)]
    li = {x['name']: x for x in doc['lockins']}; tau = li.get('sr1', doc['lockins'][0])['time_constant_s']
    I = doc['excitation_V'] / doc['bias_resistor_ohm'] * 1e9
    snr = min(1.0, I / 50 * (tau / 0.3) ** 0.5)
    h = g.derived(doc, B, g.columns(doc), sc, g.cost_model(case))['cost']['estimated_wall_h']
    if doc.get('form') == 'column_series': h *= 1 + len(doc.get('declared_columns_cm2') or [])
    form = {'2d_megasweep': '', 'continuous_ramp': ' ramp', 'column_series': ' col. series'}.get(doc['form'], '')
    print(f"| {lab} | {B.min():.2f}–{B.max():.1f} T × {B.size}{form} | {n.min():+.2f}…{n.max():+.2f} × {n.size} | {c[0]} | {c[1]} | {c[2]} | {cr[0]:.1f} / {cr[1]:.1f} | {I:.0f} | {tau} | {snr:.2f} | {h:.2f} |")
