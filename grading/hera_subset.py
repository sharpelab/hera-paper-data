#!/usr/bin/env python3
"""Build a second-rater Pass A subset page from a sealed pool.
usage: hera_subset.py <pool> <rater> [--seed N] [--frac F] [--practice KEY:N]

Reads blind-map.yaml (pool_<pool>), raw/<pool>.decision-exclude.json (hidden cards),
raw/<pool>.items.json (enumerated items), cards/<key>.full.json (card bodies + figures).
Writes raters/<rater>/<pool>.<rater>.html (scoring page; export = <pool>.<rater>.scores.json),
raters/<rater>/<pool>.<rater>.cards.jsonl, raters/<rater>/manifest.json.
Optional --practice CAL2:6 writes raters/<rater>/CAL2.<rater>.html with N cards from that key.

Sampling: every visible verdict card; a stratified random fraction of inference and
decision cards per run (ceil); fresh shuffle for the rater. Pooled ids are preserved so
the rater's scores join Aaron's on card id. The rater page carries a header stating the
standard of correctness verbatim from the rubric."""
import json, sys, re, math, random, pathlib, importlib.util, html, shutil
here = pathlib.Path(__file__).parent
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
seed = int(opt('--seed', '20260904')); frac = float(opt('--frac', '0.30')); practice = opt('--practice', None)
pool, rater = args[0], args[1]
out = here / 'raters' / rater; out.mkdir(parents=True, exist_ok=True)

bm = (here / 'blind-map.yaml').read_text(); sec = bm[bm.index(f'pool_{pool}:'):]
pmap = {m.group(1): (m.group(2), m.group(3)) for m in
        re.finditer(rf'^\s+({pool}-\d+): \{{key: (\w+), id: (\S+)\}}', sec, re.M)}
hidden = set(json.load(open(here / 'raw' / f'{pool}.decision-exclude.json')))
items = json.load(open(here / 'raw' / f'{pool}.items.json'))
full = {}
def card(pid):
    key, oid = pmap[pid]
    full.setdefault(key, {c['id']: c for c in json.load(open(here / 'cards' / f'{key}.full.json'))})
    c = dict(full[key][oid]); c['id'] = pid; c['_key'] = key
    c['items'] = items.get(pid) or [c['claim']]
    if c.get('supersedes'): c['supersedes'] = '(an earlier claim in the same run)'
    return c

visible = [card(pid) for pid in pmap if pid not in hidden]
rng = random.Random(seed)
chosen = [c for c in visible if c['type'] == 'verdict']
strata = {}
for c in visible:
    if c['type'] != 'verdict': strata.setdefault((c['_key'], c['type']), []).append(c)
for (key, typ), cs in sorted(strata.items()):
    cs = sorted(cs, key=lambda c: c['id']); rng.shuffle(cs)
    chosen += cs[:math.ceil(frac * len(cs))]
rng.shuffle(chosen)

# reuse hera_cards.render() without re-running the builder
src = (here / 'hera_cards.py').read_text(); start = src.index('def render(key, out):')
ns = {'html': html, 'here': here}
exec(src[start:src.index('from collections import Counter', start)], ns)

STANDARD = '''<div style="max-width:900px;margin:1em auto;padding:1em;border:1px solid #cdd;background:#f4fafa;font-size:14px">
<b>Standard of correctness.</b> <i>The claim is what a careful expert would conclude, or the choice a careful
expert would make, from the data and information available to the agent at that moment.</i><br><br>
Each card is one claim, broken into numbered items. Score every item:
<b>correct</b> (an expert would say the same) &middot; <b>partial</b> (defensible, but you have a qualm:
interpretation, precision, an unearned lean, an over-hedge &mdash; put the qualm in the note) &middot;
<b>wrong</b> &middot; <b>unverifiable</b> (the card does not give you enough to judge; excluded, not penalised).<br>
<b>Hedged claims</b> are scored at the strength stated: "consistent with X" is correct if the data support that weak
statement, partial if the hedge smuggles in a lean the data do not earn, partial if the agent under-claimed where a
firm call was supported.<br>
<b>Fitted quantities</b> are wrong when the fit does not support quoting a value at all, whatever the error bar; partial
when the value is defensible but its stated uncertainty or stability is overclaimed.<br>
Tick <b>recognized</b> if you can tell which device or session the card came from. The note box is for anything you want
the authors to see. Progress saves in this browser; <b>Export scores</b> when you stop.
</div>'''

def build(key, cards, fname):
    for c in cards: c.pop('_key', None)
    ns['render'](key, cards)
    src_html = here / 'cards' / f'{key}.html'
    text = src_html.read_text()
    text = text.replace('</div>\n  <script>', '</div>\n' + STANDARD + '\n  <script>', 1)
    (out / fname).write_text(text); src_html.unlink()

build(f'{pool}.{rater}', [dict(c) for c in chosen], f'{pool}.{rater}.html')
with open(out / f'{pool}.{rater}.cards.jsonl', 'w') as f:
    for c in chosen: f.write(json.dumps({k: v for k, v in c.items() if k not in ('figs', '_key')}) + '\n')

from collections import Counter
manifest = {
    'pool': pool, 'rater': rater, 'seed': seed, 'frac': frac,
    'rule': 'all visible verdict cards + ceil(frac * n) inference and decision cards per run, seeded shuffle',
    'n_cards': len(chosen), 'n_items': sum(len(c['items']) for c in chosen),
    'by_type': dict(Counter(c['type'] for c in chosen)),
    'by_run_type': {f'{k}/{t}': n for (k, t), n in sorted(Counter((pmap[c['id']][0], c['type']) for c in chosen).items())},
    'card_ids': [c['id'] for c in chosen],
    'pool_visible': len(visible), 'pool_items': sum(len(c['items']) for c in visible),
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=1))

if practice:
    pkey, pn = practice.split(':'); pn = int(pn)
    pc = json.load(open(here / 'cards' / f'{pkey}.full.json'))
    pitems = {}
    try: pitems = {json.loads(l)['id']: json.loads(l).get('items') for l in open(here / 'cards' / f'{pkey}.cards.jsonl')}
    except FileNotFoundError: pass
    pc = [c for c in pc if c['type'] != 'observation']
    random.Random(seed + 1).shuffle(pc); pc = pc[:pn]
    for c in pc:
        c['items'] = pitems.get(c['id']) or [c['claim']]
        if c.get('supersedes'): c['supersedes'] = '(an earlier claim in the same run)'
    build(f'{pkey}.{rater}', pc, f'{pkey}.{rater}.html')
    manifest['practice'] = {'key': pkey, 'n': len(pc), 'ids': [c['id'] for c in pc]}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))

print(json.dumps({k: v for k, v in manifest.items() if k != 'card_ids'}, indent=1))
