"""What-if: per component (light, split), the best <= 5 columns whose light tones sit >= 1/W apart (no fixed grid),
Q = A x (light/5 + split/5)/2 in [0, 1]. Compared with the fixed cell grid."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
CAP = 5

def best_spaced(w, f, dF, cap=CAP):
    """Max total weight of <= cap columns with pairwise |f_i - f_j| >= dF (DP over f-sorted columns)."""
    ok = w > 0
    w, f = w[ok], f[ok]
    if not w.size: return 0.0
    o = np.argsort(f); w, f = w[o], f[o]
    prev = np.searchsorted(f, f - dF + 1e-12, side='right') - 1   # last index at least dF below
    D = np.zeros((w.size + 1, cap + 1))
    for i in range(1, w.size + 1):
        for k in range(1, cap + 1):
            D[i, k] = max(D[i - 1, k], w[i - 1] + D[prev[i - 1] + 1, k - 1])
    return float(D[-1, cap])

def grid(w, f, dF):
    ok = w > 0
    if not ok.any(): return 0.0
    c = np.floor((f[ok] - f[ok].min()) / dF)
    return float(sum(w[ok][c == k].max() for k in np.unique(c)))

rows = []
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan': continue
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    L, S = box.window(B, 0.75), box.window(B, 1.0)
    if not L['max_step_per_T']: continue
    fl = box.f_light(n, 'Halder_ABAB'); e = (n > 0) & ~np.isnan(fl); f = np.nan_to_num(fl)
    step = L['max_step_per_T']
    ws = np.where(e, box.ramp(1 / (box.FLN * np.maximum(n, 1e-9) * step), box.M) * box.ramp(f * S['W_per_T'], box.K), 0)
    wl = np.where(e, box.ramp(1 / (np.maximum(f, 1e-9) * step), box.M) * box.ramp(f * L['W_per_T'], box.K), 0)
    A = box.acquisition(r['doc'])['A'] or 1.0
    dF = 1 / L['W_per_T']
    gl, gs = grid(wl, f, dF), grid(ws, f, dF)
    bl, bs = best_spaced(wl, f, dF), best_spaced(ws, f, dF)
    rows.append((r['key'].replace('vti02-fan-design-', '').replace('/episodes', ''), gl, gs, bl, bs,
                 A * (min(gl, CAP) + min(gs, CAP)) / (2 * CAP), A * (bl + bs) / (2 * CAP), h))
rows.sort(key=lambda x: -x[6])
print('| fan | grid light / split | best-5 spaced light / split | Q grid, capped | Q best-5 | h |')
print('|---|---|---|---|---|---|')
for k, gl, gs, bl, bs, qg, qb, h in rows:
    print(f"| {k} | {gl:.2f} / {gs:.2f} | {bl:.2f} / {bs:.2f} | {qg:.2f} | {qb:.2f} | {h:.2f} |")
