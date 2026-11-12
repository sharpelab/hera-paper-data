"""What-if: high-line credit ramps 0.5 at 2 rows/period -> 1 at 3 (0 below 2); a cell is worth its best column."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)

def ramp_q(B, n, doc):
    B = np.unique(B[B > 0]); L, S = box.window(B, 0.75), box.window(B, 1.0)
    fl = box.f_light(n, 'Halder_ABAB')
    if not L['max_step_per_T']: return 0.0, 0
    rpp = 1 / (box.FLN * n * L['max_step_per_T'])
    w = np.where(rpp >= 3, 1.0, np.where(rpp >= 2, 0.5 + 0.5 * (rpp - 2), 0.0))
    ok = (n > 0) & ~np.isnan(fl) & (fl * L['W_per_T'] >= 3) & (fl * S['W_per_T'] >= 3) & (w > 0)
    if not ok.any(): return 0.0, 0
    c = np.floor((fl[ok] - fl[ok].min()) * L['W_per_T'])
    A = box.acquisition(doc)['A'] or 1.0
    return A * sum(w[ok][c == k].max() for k in np.unique(c)), int(ok.sum())

print('| episode | quality m=3 | quality ramp | columns m=3 → ramp |')
print('|---|---|---|---|')
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan': continue
    B, n, h = C.design(r)
    s = box.score(np.asarray(B), n * 1e12, r['doc'], b_lo_light=0.75, b_lo_split=1.0, tone_model='Halder_ABAB', signal_lockin='sr1')
    q, k = ramp_q(np.asarray(B), n, r['doc'])
    if abs(q - s['quality']) > 1e-9 or k != s['counted']:
        print(f"| {r['key'].replace('vti02-fan-design-','')} | {s['quality']:.2f} | {q:.2f} | {s['counted']} → {k} |")
