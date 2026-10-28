#!/usr/bin/env python3
"""Re-render a pool from its SEALED map order (after per-run card rebuilds). Never reshuffles; ids preserved.
usage: hera_repool.py <pool>"""
import re, json, sys, pathlib, statistics
here = pathlib.Path(__file__).parent; pool = sys.argv[1]
bm = (here/'blind-map.yaml').read_text(); i = bm.index(f'pool_{pool}:')
prev = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(rf'^\s+({pool}-\d+): \{{key: (\w+), id: (\S+)\}}', bm[i:], re.M)]
full, cards = {}, []
for pid, k, oid in prev:
    full.setdefault(k, {c['id']: c for c in json.load(open(here/'cards'/f'{k}.full.json'))})
    c = dict(full[k][oid]); c['id'] = pid
    if c.get('supersedes'): c['supersedes'] = '(an earlier claim in the same run)'
    cards.append(c)
src = (here/'hera_cards.py').read_text(); start = src.index('def render(key, out):'); ns = {'html': __import__('html'), 'here': here}
hidden = {}
try: hidden = json.load(open(here/'raw'/f'{pool}.decision-exclude.json'))
except FileNotFoundError: pass
items = {}
try: items = json.load(open(here/'raw'/f'{pool}.items.json'))
except FileNotFoundError: pass
for c in cards: c['items'] = items.get(c['id'])
shown = [c for c in cards if c['id'] not in hidden]
exec(src[start:src.index('from collections import Counter', start)], ns); ns['render'](pool, shown)
print('hidden (instrument/tooling decisions):', len(hidden), '| cards with items:', sum(bool(c.get('items')) for c in shown), 'items total:', sum(len(c.get('items') or []) for c in shown))
with open(here/'cards'/f'{pool}.cards.jsonl', 'w') as f:
    for c in cards: f.write(json.dumps({k: v for k, v in c.items() if k != 'figs'}) + '\n')
print(len(cards), 'cards; figs:', sum(bool(c['figs']) for c in cards), 'verbatim median', statistics.median(c['verbatim_score'] for c in cards))
