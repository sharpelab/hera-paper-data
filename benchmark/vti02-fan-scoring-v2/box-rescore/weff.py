"""What-if: one domain. Per column and part, effective periods p = F_light * W_eff, where W_eff is the 1/B record
above the part's floor, each row interval weighted by how well it samples the part's tone locally
(ramp over rows per period, 2 -> 3). Column weight = ramp(p, 1.5 -> 3.5). Best 5 spaced per part; quality = A(l+s)/10."""
import sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore')
from figlib import *

def w_eff(B, lo, F, rows=(2.0, 3.0)):
    Bw = B[B >= lo - 1e-9]
    if Bw.size < 2 or F <= 0: return 0.0
    u = np.sort(1 / Bw); du = np.diff(u)
    return float(np.sum(du * box.ramp(1 / (F * du), rows)))

def score(r, per=(1.5, 3.5), rows=(2.0, 3.0)):
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    s = box.score(B, n * 1e12, r['doc'], b_lo_light=0.75, b_lo_split=1.0, tone_model='Halder_ABAB', signal_lockin='sr1')
    fl = box.f_light(n, 'Halder_ABAB'); e = (n > 0) & ~np.isnan(fl); f = np.where(e, fl, 0)
    lo_l, lo_s = max(B[0], 0.75), max(B[0], 1.0)
    wl = np.array([box.ramp(f[j] * w_eff(B, lo_l, f[j], rows), per) if e[j] else 0 for j in range(n.size)])
    ws = np.array([box.ramp(f[j] * w_eff(B, lo_s, box.FLN * n[j], rows), per) if e[j] else 0 for j in range(n.size)])
    gap = s['min_spacing_T'] or np.inf
    L, _ = box.best_spaced(wl, f, gap, 5); S, _ = box.best_spaced(ws, f, gap, 5)
    A = s['A'] if s['A'] is not None else 1.0
    return s, L, S, A * (L + S) / 10, h

rows = []
for k, r in all_fans().items():
    s, L, S, q, h = score(r)
    rows.append((k.replace('vti02-fan-design-', '').replace('/episodes', ''), s['light']['score'], s['split']['score'], s['quality'], L, S, q, h))
rows.sort(key=lambda x: -x[6])
print('| fan | current light / split | Q now | W_eff light / split | Q new | h |'); print('|---|---|---|---|---|---|')
for k, l0, s0, q0, l1, s1, q1, h in rows:
    flag = ' ←' if abs(q1 - q0) > 0.05 else ''
    print(f"| {k} | {l0:.2f} / {s0:.2f} | {q0:.2f} | {l1:.2f} / {s1:.2f} | {q1:.2f}{flag} | {h:.2f} |")
