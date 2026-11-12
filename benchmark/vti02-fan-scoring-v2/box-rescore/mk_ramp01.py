"""What-if: soft edges on both lines. w(x) = 0 at 2, linear to 1 at 3.
Column weight = w(rows per F_L period) * w(light periods in the split window); the split window is the
shorter of the two nested windows, so its periods bound the light window's. A cell is worth its best column."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)

def w(x):
    return np.where(x >= 3, 1.0, np.where(x >= 2, x - 2, 0.0))

def soft(B, n, doc, soft_m=True, soft_k=True, comb='prod'):
    B = np.unique(B[B > 0]); L, S = box.window(B, 0.75), box.window(B, 1.0)
    if not L['max_step_per_T']: return 0.0, 0
    fl = box.f_light(n, 'Halder_ABAB')
    rpp = 1 / (box.FLN * n * L['max_step_per_T'])
    pl, ps = fl * L['W_per_T'], fl * S['W_per_T']
    wm = w(rpp) if soft_m else (rpp >= 3).astype(float)
    wk = np.minimum(w(pl), w(ps)) if soft_k else ((pl >= 3) & (ps >= 3)).astype(float)
    wt = np.where((n > 0) & ~np.isnan(fl), wm * wk if comb == 'prod' else np.minimum(wm, wk), 0.0)
    ok = wt > 0
    if not ok.any(): return 0.0, 0
    c = np.floor((fl[ok] - fl[ok].min()) * L['W_per_T'])
    A = box.acquisition(doc)['A'] or 1.0
    return A * sum(wt[ok][c == k].max() for k in np.unique(c)), int(ok.sum())

rows = []
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan': continue
    B, n, h = C.design(r)
    B = np.asarray(B)
    hard = soft(B, n, r['doc'], False, False)
    m_only = soft(B, n, r['doc'], True, True, 'min')
    both = soft(B, n, r['doc'], True, True)
    rows.append((r['key'].replace('vti02-fan-design-', '').replace('/episodes', ''), f"{B[B>0].min():.2f}", hard, m_only, both, h))
print('| episode | B_min | hard | min | product | h |'); print('|---|---|---|---|---|---|')
for k, bmin, hd, mo, bo, h in rows:
    flag = '' if abs(bo[0] - hd[0]) < 1e-9 and abs(mo[0] - hd[0]) < 1e-9 else ' ←'
    print(f"| {k} | {bmin} | {hd[0]:.2f} ({hd[1]}) | {mo[0]:.2f} ({mo[1]}) | {bo[0]:.2f} ({bo[1]}){flag} | {h:.2f} |")
