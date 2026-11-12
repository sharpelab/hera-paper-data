"""Rescore every vti-02 dev-set fan with the repo's box grader (hera/graders/fan-design/box.py)."""
import sys, csv, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np
import common as C
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
from scipy.stats import spearmanr

old = {r['key']: r for r in csv.DictReader(open(C.OUT / 'v1-cells' / 'episodes.csv'))}
io = {}
for r in csv.DictReader(open(C.TOP / 'ideal-observer/scores.csv')):
    if r['setting'] == 'base':
        io[r['label']] = float(r['nats0.5'])

rows = []
for r in C.inventory() + C.live_fans():
    if r.get('ending') != 'fan':
        continue
    B, n, h = C.design(r)
    s = box.score(np.asarray(B), n * 1e12, r['doc'], b_lo_light=0.75, b_lo_split=1.0, tone_model='Halder_ABAB', signal_lockin='sr1')
    k = r['key'].replace('vti02-fan-design-', '')
    rows.append(dict(key=k, model=r.get('model', 'live'), arm=r.get('corpus', 'live'), cut=r.get('cut', ''),
                     src=r.get('source', 'grader'),
                     B=f"{min(B):.2f}-{max(B):.1f}x{len(np.unique(B))}", n=f"{n.min():+.2f}..{n.max():+.2f}x{n.size}",
                     light=s['light']['score'], split=s['split']['score'], A=s['A'], quality=s['quality'], p_call=s['p_call'], hours=h,
                     light_cols=s['light']['columns_weighted'], split_cols=s['split']['columns_weighted'],
                     chosen=' '.join(f"{x:.2f}" for x in s['split']['chosen_n_actual_1e12']),
                     old_cells=old.get(r['key'], {}).get('n_cells', ''), flags='; '.join(s['flags'])))
rows.sort(key=lambda x: (x['arm'] != 'live', x['model'], x['arm'], x['key']))
with open(Path(__file__).with_name('rescore.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print('| episode | model | arm | B (T) × rows | n actual × cols | light (cols) | split (cols) | split picks, n | A | quality | P(call) | h |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for x in rows:
    print(f"| {x['key']}{' (hand)' if x['src']=='hand' else ''} | {x['model']} | {x['arm']} | {x['B']} | {x['n']} | "
          f"{x['light']:.2f} ({x['light_cols']}) | {x['split']:.2f} ({x['split_cols']}) | {x['chosen']} | {x['A']:.2f} | {x['quality']:.2f} | {x['p_call']:.2f} | {x['hours']:.2f} |")
pairs = [(x['quality'], float(x['old_cells'])) for x in rows if x['old_cells'] not in ('', None)]
if len(pairs) > 3:
    print('\nSpearman vs prereg-stats capped-cells (corpus tones):', spearmanr(*zip(*pairs)))
