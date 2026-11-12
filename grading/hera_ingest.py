#!/usr/bin/env python3
"""Ingest exported scores → cards.csv (raw, unweighted, per card) + runs_quality.csv (S_claim per run).
usage: hera_ingest.py <pool> [rater]
  default: reads scores/<pool>.scores.json (scores of record) -> scores/<pool>.{items,cards,runs}.csv
  rater:   reads raters/<rater>/<pool>.<rater>.scores.json over that rater's manifest.json subset
           -> scores/<pool>.<rater>.{items,cards,runs}.csv (the filenames dossiers/hera_synth.py discovers)
Un-blinding: runs_quality.csv is keyed by run KEY only (T1A…), never by archive name. Aaron may look at it."""
import json, csv, sys, pathlib, re
here = pathlib.Path(__file__).parent; pool = sys.argv[1]; rater = sys.argv[2] if len(sys.argv) > 2 else None
out_stem = f'{pool}.{rater}' if rater else pool
cards = {c['id']: c for c in map(json.loads, open(here/'cards'/f'{pool}.cards.jsonl'))}
if rater:
    rd = here/'raters'/rater
    sc = json.load(open(rd/f'{pool}.{rater}.scores.json'))['scores']
    keep = set(json.load(open(rd/'manifest.json'))['card_ids'])
    cards = {k: v for k, v in cards.items() if k in keep}
else:
    sc = json.load(open(here/'scores'/f'{pool}.scores.json'))['scores']
# pooled id -> run key, from the sealed map (only the key is used downstream)
bm = (here/'blind-map.yaml').read_text(); sec = bm[bm.index(f'pool_{pool}:'):]
pmap = {m.group(1): m.group(2) for m in re.finditer(rf'^\s+({pool}-\d+): \{{key: (\w+), id: (\S+)\}}', sec, re.M)}
V = {'correct': 1.0, 'partial': 0.5, 'wrong': 0.0}; W = {'verdict': 2}
hidden = {}
try: hidden = json.load(open(here/'raw'/f'{pool}.decision-exclude.json'))
except FileNotFoundError: pass
rows = []
items_map = {}
try: items_map = json.load(open(here/'raw'/f'{pool}.items.json'))
except FileNotFoundError: pass
item_rows = []
for cid, c in cards.items():
    s = sc.get(cid, {}); its = s.get('items') or ([s['verdict']] if s.get('verdict') else [])
    texts = items_map.get(cid) or [c['claim']]
    vals = [V[x] for x in its if x in V]; n_unv = sum(1 for x in its if x == 'unverifiable')
    complete = bool(its) and all(its)
    if not complete: v = None
    elif not vals: v = 'unverifiable'
    else: v = round(sum(vals) / len(vals), 3)
    for j, x in enumerate(its): item_rows.append(dict(card=cid, item=j + 1, run=pmap.get(cid), type=c['type'], verdict=x, value=V.get(x), hidden=int(cid in hidden), text=texts[j] if j < len(texts) else ''))
    rows.append(dict(card=cid, run=pmap.get(cid), type=c['type'], n_items=len(texts), n_unverifiable_items=n_unv, verdict=v, value=(v if isinstance(v, float) else None), weight=W.get(c['type'], 1), hidden=int(cid in hidden),
                     recognized=int(bool(s.get('recognized'))), note=(s.get('note') or '').replace('\n', ' '), ts=s.get('ts')))
with open(here/'scores'/f'{out_stem}.items.csv', 'w', newline='') as f:
    if item_rows: w = csv.DictWriter(f, fieldnames=item_rows[0].keys()); w.writeheader(); w.writerows(item_rows)
(here/'scores').mkdir(exist_ok=True)
with open(here/'scores'/f'{out_stem}.cards.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
# per-run aggregate
runs = {}
for r in rows:
    R = runs.setdefault(r['run'], dict(run=r['run'], n_cards=0, n_scored=0, n_unverifiable=0, n_recognized=0, num=0.0, den=0.0,
                                       **{f'{t}_correct': 0 for t in ('observation','inference','decision','verdict')},
                                       **{f'{t}_n': 0 for t in ('observation','inference','decision','verdict')}))
    if r['hidden']: continue   # instrument/tooling decisions: kept in cards.csv, excluded from the score
    R['n_cards'] += 1; R['n_recognized'] += r['recognized']
    if r['verdict'] is None: continue
    if r['verdict'] == 'unverifiable': R['n_unverifiable'] += 1; continue
    R['n_scored'] += 1; R['num'] += r['weight'] * r['value']; R['den'] += r['weight']
    R[f"{r['type']}_n"] += 1; R[f"{r['type']}_correct"] += r['value']
for ir in item_rows:   # item-level accuracy, all items pooled
    if ir['hidden'] or ir['value'] is None: continue
    R = runs[ir['run']]; R['items_n'] = R.get('items_n', 0) + 1; R['items_sum'] = R.get('items_sum', 0) + ir['value']
out = []
for R in runs.values():
    R['S_claim'] = round(R['num'] / R['den'], 3) if R['den'] else None
    for t in ('observation','inference','decision','verdict'):
        R[f'{t}_acc'] = round(R[f'{t}_correct'] / R[f'{t}_n'], 3) if R[f'{t}_n'] else None
    R['item_acc'] = round(R.get('items_sum', 0) / R['items_n'], 3) if R.get('items_n') else None; R.pop('items_sum', None); R.pop('items_n', None)
    R.pop('num'); R.pop('den'); out.append(R)
with open(here/'scores'/f'{out_stem}.runs.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
for R in sorted(out, key=lambda r: r['run'] or ''):
    print(f"{R['run']}: S_claim={R['S_claim']}  scored {R['n_scored']}/{R['n_cards']}  unverifiable {R['n_unverifiable']}  recognized {R['n_recognized']}  "
          f"inf {R['inference_acc']} dec {R['decision_acc']} ver {R['verdict_acc']}  item_acc {R['item_acc']}")
