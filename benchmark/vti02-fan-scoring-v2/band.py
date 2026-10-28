"""Zack's (n, F) band: high line = F where rows/period = m (worst 1/B step in [B_min,B_max]),
low line = k / (1/B_min - 1/B_max); a column counts when F_light(n) and F_L(n) both lie in the band.
Also: independent tone cells = distinct bins of width dF = 1/window along the counted light tone."""
import sys; sys.path.insert(0, sys.argv[1])
import warnings; warnings.filterwarnings('ignore')
import numpy as np, roi
def cells(B, ns, floor):
    B = np.unique(B); B = B[B >= floor]
    if B.size < 2: return 0, 0, None
    win = 1/B[0] - 1/B[-1]; hi = 1/(3*np.max(-np.diff(1/B))); lo = 3/win
    ok = [x for x in ns if not np.isnan(roi.f_light(x)) and roi.f_light(x) >= lo and roi.f_L(x) <= hi]
    if not ok: return 0, 0, (lo, hi)
    fl = sorted(roi.f_light(x) for x in ok)
    return len(ok), (fl[-1]-fl[0])*win + 1, (lo, hi)   # tone span in resolution cells (+1: the first cell)
def credit(B, ns, floor, at2=0.0):
    """Per-column scalar credit: 0 below 2 low-tone periods, at2 at 2, linear to 1 at 3; F_L must clear the high line."""
    B = np.unique(B); B = B[B >= floor]
    if B.size < 2: return 0.0
    win = 1/B[0] - 1/B[-1]; hi = 1/(3*np.max(-np.diff(1/B)))
    tot = 0.0
    for x in ns:
        fl = roi.f_light(x)
        if np.isnan(fl) or roi.f_L(x) > hi: continue
        p = fl * win
        tot += 0.0 if p < 2 else 1.0 if p >= 3 else at2 + (1 - at2) * (p - 2)
    return tot
import json, glob
def main():
    from pathlib import Path
    g = roi.g
    files = glob.glob('/data/sharpelab/hera-data/frontier/calibration/vti02-live/*/grades/fan-design/*/output.json') + \
            glob.glob('/data/sharpelab/hera-data/replay/runs/vti02-fan-design-*/*/episodes/*/grades/fan-design/*/output.json')
    latest = {}
    for f in files:
        ep = f.split('/grades/')[0]
        if ep not in latest or f > latest[ep]: latest[ep] = f
    print("| Episode | band lo–hi (T) @ raw B_min | cols | tone cells | cols @ floor 1.0 T | est h |")
    print("|---|---|---|---|---|---|")
    for ep, f in sorted(latest.items()):
        doc = json.load(open(f))
        if doc.get('status') != 'extracted' or g.tier_of(doc) != 'fan': continue
        case = g.case_of(Path(ep)/'session'); B = g.field_axis(doc, case)
        n = case.get('n_scale', 1.0) * g.columns(doc) / 1e12
        c0, cell0, band = cells(B, n, 1e-3)
        c1, cell1, _ = cells(B, n, 1.0)
        h = g.derived(doc, B, g.columns(doc), case.get('n_scale',1.0), g.cost_model(case))['cost']['estimated_wall_h']
        lab = ep.replace('/data/sharpelab/hera-data/','').replace('frontier/calibration/vti02-live/','live ').replace('replay/runs/vti02-fan-design-','').replace('/episodes/00','').replace('/episodes/0',' #')
        bs = f"{band[0]:.1f}–{band[1]:.1f}" if band else "—"
        print(f"| {lab} | {bs} | {c0} | {cell0:.1f} | {c1} ({cell1:.1f} cells) | {h:.2f} |")

if __name__ == "__main__":
    main()
