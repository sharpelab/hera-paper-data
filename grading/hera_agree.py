#!/usr/bin/env python3
"""Second-rater agreement on a Pass A subset — the pre-declared computation.
usage: hera_agree.py <pool> <rater>
Reads scores/<pool>.scores.json (scores of record), raters/<rater>/<pool>.<rater>.scores.json,
raters/<rater>/manifest.json, raters/<rater>/<pool>.<rater>.cards.jsonl (types), blind-map.yaml (run keys).
Writes raters/<rater>/agreement.md and raters/<rater>/agreement.csv. Nothing else.

Pre-declared (PREREG.md, "Second rater, Pass A subset"):
  main text : item exact agreement + quadratic-weighted Cohen's kappa on item values (1/0.5/0),
              over items both raters scored correct/partial/wrong; unverifiable-by-either excluded, counted.
  supplement: the same by claim type and by run; card-level kappa on card values; S_claim per run
              from each rater's items on the subset; partition test (every corpus arm above every
              no-corpus arm under the second rater); disagreement characterized from both raters' notes.
Corpus arms: T1A T1B T1D T1E.  No-corpus arms: T1C T1F.  Verdict weight 2, else 1 (rubric)."""
import json, sys, re, csv, pathlib
from collections import defaultdict
here = pathlib.Path(__file__).parent
pool, rater = sys.argv[1], sys.argv[2]
rd = here / 'raters' / rater
V = {'correct': 1.0, 'partial': 0.5, 'wrong': 0.0}
CORPUS, NOCORPUS = {'T1A', 'T1B', 'T1D', 'T1E'}, {'T1C', 'T1F'}

ref = json.load(open(here / 'scores' / f'{pool}.scores.json'))['scores']
try: sec = json.load(open(rd / f'{pool}.{rater}.scores.json'))['scores']
except FileNotFoundError: sys.exit(f'waiting: no {pool}.{rater}.scores.json yet')
man = json.load(open(rd / 'manifest.json'))
types = {json.loads(l)['id']: json.loads(l)['type'] for l in open(rd / f'{pool}.{rater}.cards.jsonl')}
bm = (here / 'blind-map.yaml').read_text(); s = bm[bm.index(f'pool_{pool}:'):]
run = {m.group(1): m.group(2) for m in re.finditer(rf'^\s+({pool}-\d+): \{{key: (\w+), id: (\S+)\}}', s, re.M)}

def kappa_w(pairs):
    """Quadratic-weighted Cohen's kappa on paired categorical values (3 ordered levels)."""
    if len(pairs) < 2: return float('nan')
    levels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    if len(levels) < 2: return float('nan')
    idx = {v: i for i, v in enumerate(levels)}; k = len(levels); n = len(pairs)
    O = [[0] * k for _ in range(k)]
    for a, b in pairs: O[idx[a]][idx[b]] += 1
    ra = [sum(r) for r in O]; rb = [sum(O[i][j] for i in range(k)) for j in range(k)]
    w = lambda i, j: ((i - j) ** 2) / ((k - 1) ** 2)
    po = sum(w(i, j) * O[i][j] for i in range(k) for j in range(k)) / n
    pe = sum(w(i, j) * ra[i] * rb[j] for i in range(k) for j in range(k)) / n / n
    return float('nan') if pe == 0 else 1 - po / pe

rows = []          # one row per item
n_unv = {'ref': 0, 'rater': 0, 'either': 0}; n_unscored = 0
for cid in man['card_ids']:
    a = (ref.get(cid) or {}).get('items') or []; b = (sec.get(cid) or {}).get('items') or []
    n = max(len(a), len(b))
    for j in range(n):
        va = a[j] if j < len(a) else None; vb = b[j] if j < len(b) else None
        if vb is None: n_unscored += 1
        if va == 'unverifiable': n_unv['ref'] += 1
        if vb == 'unverifiable': n_unv['rater'] += 1
        if va == 'unverifiable' or vb == 'unverifiable': n_unv['either'] += 1
        rows.append({'card': cid, 'item': j + 1, 'run': run[cid], 'type': types[cid],
                     'ref': va, 'rater': vb,
                     'ref_v': V.get(va), 'rater_v': V.get(vb),
                     'paired': int(va in V and vb in V)})
paired = [r for r in rows if r['paired']]

def stats(rs):
    if not rs: return {'n': 0, 'exact': float('nan'), 'kappa_w': float('nan')}
    return {'n': len(rs), 'exact': sum(r['ref'] == r['rater'] for r in rs) / len(rs),
            'kappa_w': kappa_w([(r['ref_v'], r['rater_v']) for r in rs])}

main = stats(paired)
by_type = {t: stats([r for r in paired if r['type'] == t]) for t in ('inference', 'decision', 'verdict')}
by_run = {k: stats([r for r in paired if r['run'] == k]) for k in sorted(set(run[c] for c in man['card_ids']))}

# card-level: card value = mean of items each rater scored (own unverifiables excluded); both raters need >= 1
cards = defaultdict(lambda: {'ref': [], 'rater': []})
for r in rows:
    if r['ref_v'] is not None: cards[r['card']]['ref'].append(r['ref_v'])
    if r['rater_v'] is not None: cards[r['card']]['rater'].append(r['rater_v'])
cv = {c: (sum(d['ref']) / len(d['ref']), sum(d['rater']) / len(d['rater'])) for c, d in cards.items() if d['ref'] and d['rater']}
card_k = kappa_w([(round(a, 3), round(b, 3)) for a, b in cv.values()])
card_exact = sum(abs(a - b) < 1e-9 for a, b in cv.values()) / len(cv) if cv else float('nan')

# S_claim per run on the subset, each rater's own items, verdict weight 2
def sclaim(side):
    out = {}
    for k in by_run:
        num = den = 0.0
        for c, (va, vb) in cv.items():
            if run[c] != k: continue
            w = 2 if types[c] == 'verdict' else 1
            num += w * (va if side == 'ref' else vb); den += w
        out[k] = num / den if den else float('nan')
    return out
S_ref, S_sec = sclaim('ref'), sclaim('rater')
def partition(S):
    c = [S[k] for k in S if k in CORPUS]; n = [S[k] for k in S if k in NOCORPUS]
    return bool(c and n) and min(c) > max(n)

# write
f = lambda x: 'n/a' if x != x else f'{x:.3f}'
L = [f'# Second-rater agreement — {rater} vs scores of record, pool {pool}', '',
     f'*Computed by `hera_agree.py` (pre-declared). Subset: {man["n_cards"]} cards / {man["n_items"]} items, seed {man["seed"]}.*', '',
     '## Main text (pre-declared, two numbers)', '',
     f'- Items paired (both raters correct/partial/wrong): **{main["n"]}** of {len(rows)}; unverifiable by either rater: {n_unv["either"]} (record {n_unv["ref"]}, {rater} {n_unv["rater"]}); unscored by {rater}: {n_unscored}.',
     f'- **Exact agreement: {f(main["exact"])}**', f'- **Quadratic-weighted κ (items, 1/0.5/0): {f(main["kappa_w"])}**', '',
     '## Supplement (pre-declared)', '', '| stratum | n items | exact | κ_w |', '|---|---|---|---|']
for t, st in by_type.items(): L.append(f'| type {t} | {st["n"]} | {f(st["exact"])} | {f(st["kappa_w"])} |')
for k, st in by_run.items(): L.append(f'| run {k} | {st["n"]} | {f(st["exact"])} | {f(st["kappa_w"])} |')
L += ['', f'Card level ({len(cv)} cards with both raters scoring ≥1 item): exact {f(card_exact)}, κ_w {f(card_k)}.', '',
      '| run | S_claim record (subset) | S_claim ' + rater + ' (subset) |', '|---|---|---|']
for k in by_run: L.append(f'| {k} | {f(S_ref[k])} | {f(S_sec[k])} |')
L += ['', f'Partition test (every corpus arm > every no-corpus arm): record on subset **{partition(S_ref)}**; {rater} **{partition(S_sec)}**.', '',
      '## Disagreements (for characterization; both raters\' notes)', '']
for cid in man['card_ids']:
    its = [r for r in rows if r['card'] == cid and r['paired'] and r['ref'] != r['rater']]
    if not its: continue
    L.append(f'- **{cid}** ({run[cid]}/{types[cid]}): ' + '; '.join(f'item {r["item"]} record={r["ref"]} {rater}={r["rater"]}' for r in its))
    na, nb = (ref.get(cid) or {}).get('note', ''), (sec.get(cid) or {}).get('note', '')
    if na: L.append(f'  - record: {na}')
    if nb: L.append(f'  - {rater}: {nb}')
(rd / 'agreement.md').write_text('\n'.join(L) + '\n')
with open(rd / 'agreement.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('\n'.join(L[:12]))
