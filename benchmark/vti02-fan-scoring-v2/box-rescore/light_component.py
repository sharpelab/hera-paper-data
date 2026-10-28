"""What-if: give the light tone its own credit. light weight = ramp(rows per F_light period) x ramp(light periods from 0.75 T);
split weight = the current column weight. Each summed over light-tone cells (best column per cell)."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
def cellsum(w, fl, dF):
    ok = w > 0
    if not ok.any(): return 0.0
    c = np.floor((fl[ok] - fl[ok].min()) / dF)
    return float(sum(w[ok][c == k].max() for k in np.unique(c)))
print('| fan | B_min | split (current) | light | mean | h |'); print('|---|---|---|---|---|---|')
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan': continue
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    L, S = box.window(B, 0.75), box.window(B, 1.0)
    if not L['max_step_per_T']: continue
    fl = box.f_light(n, 'Halder_ABAB'); e = (n > 0) & ~np.isnan(fl); fl0 = np.nan_to_num(fl)
    step = L['max_step_per_T']
    rl = 1 / (np.maximum(fl0, 1e-9) * step); rL = 1 / (box.FLN * np.maximum(n, 1e-9) * step)
    ws = np.where(e, box.ramp(rL, box.M) * box.ramp(fl0 * S['W_per_T'], box.K), 0)
    wl = np.where(e, box.ramp(rl, box.M) * box.ramp(fl0 * L['W_per_T'], box.K), 0)
    A = box.acquisition(r['doc'])['A'] or 1.0
    dF = 1 / L['W_per_T']
    qs, ql = A * cellsum(ws, fl0, dF), A * cellsum(wl, fl0, dF)
    k = r['key'].replace('vti02-fan-design-', '').replace('/episodes', '')
    print(f"| {k} | {B[0]:.2f} | {qs:.2f} | {ql:.2f} | {(qs + ql) / 2:.2f} | {h:.2f} |")
