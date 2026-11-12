#!/usr/bin/env python3
"""Pool cards from several runs into one shuffled, relabelled scoring page.
usage: hera_pool.py <pool_name> <key1> <key2> ...   (reads cards/<key>.full.json)
Writes cards/<pool>.html, cards/<pool>.cards.jsonl (scrubbed), and appends the sealed P->key map to blind-map.yaml."""
import json, sys, random, pathlib, importlib.util
here = pathlib.Path(__file__).parent
import re
args = sys.argv[1:]; append = '--append' in args; args = [a for a in args if a != '--append']
pool, keys = args[0], args[1:]
bm = (here/'blind-map.yaml').read_text()
old = []   # existing pooled cards (append mode): rebuild from sealed map + per-key full.json
if append:
    sec = bm[bm.index(f'pool_{pool}:'):]
    prev = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(rf'^\s+({pool}-\d+): \{{key: (\w+), id: (\S+)\}}', sec, re.M)]
    full = {}
    for pid, k, oid in prev:
        full.setdefault(k, {c['id']: c for c in json.load(open(here/'cards'/f'{k}.full.json'))})
        c = dict(full[k][oid]); c['id'] = pid; old.append(c)
cards = []
for k in keys:
    for c in json.load(open(here/'cards'/f'{k}.full.json')): c['_key'] = k; cards.append(c)
random.Random(20260826 + len(old)).shuffle(cards)
idmap = {}
for i, c in enumerate(cards, len(old) + 1):
    new = f'{pool}-{i:03d}'; idmap[new] = {'key': c['_key'], 'id': c['id']}
    c['orig_id'] = c['id']; c['id'] = new; c.pop('_key')
for c in old + cards:
    if c.get('supersedes'): c['supersedes'] = '(an earlier claim in the same run)'
cards = old + cards
spec = importlib.util.spec_from_file_location('hc', here/'hera_cards.py')
# reuse render() without re-running the builder: exec only the render def
src = (here/'hera_cards.py').read_text(); start = src.index('def render(key, out):'); ns = {'html': __import__('html'), 'here': here}
exec(src[start:src.index('from collections import Counter', start)], ns)
for c in cards: c.pop('orig_id', None)
ns['render'](pool, cards)
with open(here/'cards'/f'{pool}.cards.jsonl', 'w') as f:
    for c in cards: f.write(json.dumps({k: v for k, v in c.items() if k != 'figs'}) + '\n')
with open(here/'blind-map.yaml', 'a') as f:
    if not append: f.write(f'\npool_{pool}:   # SEALED pooled-card id -> run key + original claim id\n')
    else: f.write(f'  # appended block\n')
    for new, m in idmap.items(): f.write(f'  {new}: {{key: {m["key"]}, id: {m["id"]}}}\n')
from collections import Counter
print(len(cards), Counter(c['type'] for c in cards), 'figs:', sum(bool(c['figs']) for c in cards))
