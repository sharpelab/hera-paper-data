"""What-if: quality = mean over parts of P(the fan yields >= m independent detected points).
Independent: light tones >= 1/2 bin apart (measured residual decorrelation). Per-column detection
p = A * column weight. Columns: the spaced set with the largest total p (DP, no cap)."""
import sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore')
from figlib import *

def p_at_least(ps, m):
    d = np.zeros(len(ps) + 1); d[0] = 1.0
    for p in ps:
        d[1:] = d[1:] * (1 - p) + d[:-1] * p; d[0] *= (1 - p)
    return float(d[m:].sum())

def q_success(c, m, frac=0.5):
    A = c['s']['A'] if c['s']['A'] is not None else 1.0
    f = np.where(c['e'], c['fl'], 0); W = c['WL']
    out = []
    for w in (c['wl'], c['ws']):
        _, chosen = box.best_spaced(w, f, frac / W, 200)
        out.append(p_at_least([A * w[j] for j in chosen], m))
    return np.mean(out), out

if __name__ == '__main__':
    F = all_fans(); rows = []
    for k, r in F.items():
        c = columns(r)
        q3, (l3, s3) = q_success(c, 3); q4, (l4, s4) = q_success(c, 4)
        f = np.where(c['e'], c['fl'], 0); A = c['s']['A'] or 1
        Lb, _ = box.best_spaced(c['wl'], f, 0.5 / c['WL'], 7); Sb, _ = box.best_spaced(c['ws'], f, 0.5 / c['WL'], 7)
        rows.append((k.replace('vti02-fan-design-', '').replace('/episodes', ''), c['s']['quality'], A * (Lb + Sb) / 14, q3, l3, s3, q4, c['h']))
    rows.sort(key=lambda t: -t[3])
    print('| fan | now | (b) ½ bin cap 7 | P(≥3): light / split → Q | P(≥4) Q | h |'); print('|---|---|---|---|---|---|')
    for k, q0, qb, q3, l3, s3, q4, h in rows:
        print(f'| {k[:44]} | {q0:.2f} | {qb:.2f} | {l3:.2f} / {s3:.2f} → {q3:.2f} | {q4:.2f} | {h:.1f} |')
