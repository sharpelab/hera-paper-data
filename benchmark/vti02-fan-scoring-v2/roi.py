"""Scratch: Aaron's ROI score (columns where both the ABCA/F_L tone and the ABAB light tone are
in the acquisition's passband) over every saved fan-design extraction at vti02."""
import sys, json, glob, os, importlib.util
from pathlib import Path
import numpy as np
REPO = Path('/home/zack/sharpelab/measurement-env')
spec = importlib.util.spec_from_file_location('grade', REPO/'hera/graders/fan-design/grade.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
T = json.load(open(Path(__file__).with_name('tones.json')))
ks = np.array(sorted(float(k) for k in T))
light = np.array([T[f"{k:.1f}"][0][0] for k in ks])
def f_light(n12):  # n in 1e12, signed
    return float(np.interp(n12, ks, light, left=np.nan, right=np.nan))
def f_L(n12): return float(g.resolution.luttinger_frequency(abs(n12)*1e12))

def column_ok(B, n12, onset, m, k):
    """F_L sampled at >= m rows/period everywhere in [onset, Bmax]; light tone holds >= k periods there."""
    B = np.unique(B); lo = max(onset, B[0]); Bw = B[B >= lo - 1e-9]
    if Bw.size < 2 or np.isnan(f_light(n12)): return False, 0.0, 0.0
    dinv = -np.diff(1/Bw)  # positive steps in 1/B
    # the interval straddling the onset counts too
    below = B[B < lo - 1e-9]
    steps = np.r_[dinv, (1/below[-1] - 1/Bw[0])] if (below.size and onset > B[0]) else dinv
    rpp = 1/(f_L(n12)*steps.max())
    periods = f_light(n12) * (1/lo - 1/Bw[-1])
    return (rpp >= m and periods >= k), rpp, periods

def run(onset, m, k, cap=15):
    rows = []
    files = glob.glob('/data/sharpelab/hera-data/frontier/calibration/vti02-live/*/grades/fan-design/*/output.json') + \
            glob.glob('/data/sharpelab/hera-data/replay/runs/vti02-fan-design-*/*/episodes/*/grades/fan-design/*/output.json')
    latest = {}
    for f in files:
        ep = f.split('/grades/')[0]
        if ep not in latest or f > latest[ep]: latest[ep] = f
    for ep, f in sorted(latest.items()):
        doc = json.load(open(f))
        if doc.get('status') != 'extracted' or g.tier_of(doc) != 'fan':
            continue
        arch = Path(ep)/'session'
        try:
            case = g.case_of(arch)
        except Exception as e:
            continue
        B = g.field_axis(doc, case); n = case.get('n_scale', 1.0) * g.columns(doc) / 1e12
        res = [column_ok(B, x, onset, m, k) for x in n]
        cnt = sum(r[0] for r in res)
        cost = g.cost_model(case)
        try:
            h = g.derived(doc, B, g.columns(doc), case.get('n_scale',1.0), cost)['cost']['estimated_wall_h']
            if doc.get('form') == 'column_series': h *= 1 + len(doc.get('declared_columns_cm2') or [])
        except Exception: h = None
        lab = ep.replace('/data/sharpelab/hera-data/','').replace('frontier/calibration/vti02-live/','live ').replace('replay/runs/vti02-fan-design-','').replace('/episodes/','#')
        taus = {x['name']: x['time_constant_s'] for x in doc['lockins']}
        rows.append((lab, doc['form'][:6], f"{B.min():.2f}-{B.max():.1f}T x{B.size}", f"{n.min():+.2f}..{n.max():+.2f} x{n.size}",
                     cnt, min(cnt, cap)/cap, h, doc.get('fast_delay_s'), taus.get('sr1'), doc.get('excitation_V'), doc.get('bias_resistor_ohm'),
                     [x for x, r in zip(n, res) if r[0]][:1]))
    return rows

if __name__ == '__main__':
    onset, m, k = map(float, sys.argv[1:4])
    for r in run(onset, m, k):
        print(f"{r[0][:62]:62s} {r[1]:6s} {r[2]:18s} {r[3]:18s} cnt={r[4]:3d} s={r[5]:.2f} h={r[6] if r[6] is None else round(r[6],2)} fd={r[7]} tau={r[8]} I={None if not (r[9] and r[10]) else round(r[9]/r[10]*1e9,1)}nA n_first_ok={[round(x,2) for x in r[11]]}")
