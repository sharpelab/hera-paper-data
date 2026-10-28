#!/usr/bin/env python3
"""Build scrubbed, figure-attached claim cards from a raw extraction.
usage: hera_cards.py <run_key> <archive_dir> [--all]
Reads raw/<key>.claims.jsonl, writes cards/<key>.html + cards/<key>.cards.jsonl.
Default keeps inference/verdict/decision; observations folded in as supporting readings
when an inference's evidence cites the same cell. Figures: PNG outputs of cited ana cells."""
import json, re, sys, base64, html, pathlib, glob
key, arch = sys.argv[1], pathlib.Path(sys.argv[2]); keep_all = '--all' in sys.argv
here = pathlib.Path(__file__).parent
rows = [json.loads(l) for l in open(here/'raw'/f'{key}.claims.jsonl')]
merges = {}   # id -> id it merges into (hand list, from calibration)
try: merges = json.load(open(here/'raw'/f'{key}.merges.json'))
except FileNotFoundError: pass
excl = {}   # id -> reason (recipe-default decision, per-column repeat, ...)
try: excl = json.load(open(here/'raw'/f'{key}.exclude.json'))
except FileNotFoundError: pass
folded = {}  # target id -> [claims folded in as supporting readings]
for src, dst in merges.items():
    if dst: folded.setdefault(dst, []).append(src)
byid = {d['id']: d for d in rows}
# figures: cell index -> [png b64]
figs = {}   # markdown cell index -> pngs from the code block immediately preceding it (+ its own)
for nb in glob.glob(str(arch/'*_ana.ipynb')):
    cells = json.load(open(nb))['cells']
    def pngs(c): return [''.join(o['data']['image/png']) for o in c.get('outputs', []) if 'image/png' in o.get('data', {})]
    for i, c in enumerate(cells):
        acc = pngs(c); j = i - 1
        while j >= 0 and cells[j]['cell_type'] == 'code': acc = pngs(cells[j]) + acc; j -= 1
        figs[i] = acc
scratch = {p.name: base64.b64encode(p.read_bytes()).decode() for p in (arch/'hera_scratch').glob('*.png')}
def cell_refs(s): return [int(x) for x in re.findall(r'ana notebook cell (\d+)', s)]
import subprocess
PY='/home/aaron/pyenvs/analysis/.venv/bin/python'
def data_refs(*ss):
    ids=set()
    for s in ss:
        ids |= {int(x) for x in re.findall(r'\b(?:run|data id|data|sweep|leg)s?\s*#?(\d{1,2})\b', s, flags=re.I)}
    return sorted(i for i in ids if (arch/'data'/str(i)/'metadata.json').exists())
(here/'cards'/'figs').mkdir(parents=True, exist_ok=True)
def data_png(i):
    out = here/'cards'/'figs'/f'{key}-d{i}.png'
    if not out.exists():
        r = subprocess.run([PY, str(here/'hera_plot.py'), str(arch/'data'/str(i)), str(out)], capture_output=True, text=True)
        if r.returncode: return None
    return base64.b64encode(out.read_bytes()).decode()
def scratch_refs(s): return [n for n in scratch if n in s]
obs_by_cell = {}
for d in rows:
    if d['type'] == 'observation':
        for c in cell_refs(d['evidence']): obs_by_cell.setdefault(c, []).append(d)
# ---- verbatim source retrieval -------------------------------------------
SCRUB = [(re.compile(r'(?i)qc0426|vti-0[12]|b1c2|zf1'), '<device>'), (re.compile(r'2026-\d\d-\d\d'), '<date>'),
         (re.compile(r'(?i)\b(zack|aaron|qingrui|jordan|isaac|zhiren|nate|nathan|ben|benjamin)\b'), '<name>'),
         (re.compile(r'\b[0-9a-f]{7,40}\b'), '<hash>')]
def scrub(s):
    for rx, rep in SCRUB: s = rx.sub(rep, s)
    return s
corpus = []   # (kind, ref, text)
for nb in sorted(glob.glob(str(arch/'*.ipynb'))):
    kind = 'ana' if '_ana' in nb else 'measure'
    for i, c in enumerate(json.load(open(nb))['cells']):
        if c['cell_type'] == 'markdown':
            corpus.append((kind, i, ''.join(c['source'])))
for tr in sorted(glob.glob(str(arch/'transcripts'/'*.jsonl'))):
    for ln, line in enumerate(open(tr), 1):
        try: d = json.loads(line)
        except Exception: continue
        if d.get('type') != 'assistant': continue
        for b in d.get('message', {}).get('content', []) or []:
            if isinstance(b, dict) and b.get('type') == 'text' and b['text'].strip():
                for para in re.split(r'\n\s*\n', b['text']):
                    if len(para.strip()) > 40: corpus.append(('transcript', ln, para.strip()))
TOK = re.compile(r'\d+(?:\.\d+)?|[A-Za-z_]{5,}')
def toks(s): return {w.lower() for w in TOK.findall(s)}
def find_verbatim(d):
    q = toks(d['claim']) | toks(d['evidence']); loc = str(d.get('source', {}).get('locator', '')); fl = str(d.get('source', {}).get('file', ''))
    cand = corpus
    m = re.search(r'cell\s*(\d+)', loc)
    if m and ('ana' in loc or 'ana' in fl or 'measure' in loc or 'measure' in fl):
        kind = 'ana' if ('ana' in loc or 'ana' in fl) else 'measure'; n = int(m.group(1))
        sub = [c for c in corpus if c[0] == kind and abs(c[1] - n) <= 1]
        if sub: cand = sub
    elif (m2 := re.search(r'line\s*(\d+)', loc)) and 'jsonl' in fl:
        n = int(m2.group(1)); sub = [c for c in corpus if c[0] == 'transcript' and abs(c[1] - n) <= 3]
        if sub: cand = sub
    best, bs = None, 0.0
    for c in cand:
        ct = toks(c[2]); s = len(q & ct) / (len(q) or 1)
        if s > bs: best, bs = c, s
    if best is None: return None, 0.0
    text = best[2]
    if len(text) > 2500:   # trim to the densest 2500-char window
        step = 500; win = max(range(0, len(text) - 2500 + 1, step), key=lambda i: len(q & toks(text[i:i + 2500])))
        text = ('…' if win else '') + text[win:win + 2500] + '…'
    find_verbatim.last = best
    return f"[{best[0]} {'cell' if best[0] != 'transcript' else 'line'} {best[1]}] " + scrub(text), round(bs, 2)

items_map = {}
out = []
for d in rows:
    if d['id'] in merges or d['id'] in excl: continue
    if not keep_all and d['type'] == 'observation': continue
    card = dict(d); card.pop('source', None)
    cells = cell_refs(d['evidence']); card['support'] = [o['claim'] for c in cells for o in obs_by_cell.get(c, []) if o['id'] != d['id']]
    card['support'] += [byid[s]['claim'] for s in folded.get(d['id'], []) if s in byid]
    for s in folded.get(d['id'], []):
        if s in byid: card['data_ids_extra'] = sorted(set(card.get('data_ids_extra', [])) | set(byid[s].get('data_ids', [])))
    card['figs'] = [b for c in cells for b in figs.get(c, [])] + [scratch[n] for n in scratch_refs(d['evidence'])]
    card['data_ids'] = sorted(set(d.get('data_ids') or data_refs(d['evidence'], d['claim'], d['context'])) | set(card.pop('data_ids_extra', [])))
    if not card['figs']:
        card['figs'] = [b for i in card['data_ids'] if (b := data_png(i))]
    card['verbatim'], card['verbatim_score'] = find_verbatim(d)
    b = getattr(find_verbatim, 'last', None)
    if b and b[0] == 'ana' and b[1] not in cells:   # attach the analysis figures behind the matched read cell
        nbf = figs.get(b[1], [])
        card['figs'] = nbf + [f for f in card['figs'] if f not in nbf]
    out.append(card)
(here/'cards').mkdir(exist_ok=True)
with open(here/'cards'/f'{key}.cards.jsonl', 'w') as f:
    for c in out: f.write(json.dumps({k: v for k, v in c.items() if k != 'figs'}) + '\n')
json.dump(out, open(here/'cards'/f'{key}.full.json', 'w'))
def render(key, out):
  H = [f'''<meta charset=utf-8><title>cards {key}</title><style>body{{font:15px/1.4 sans-serif;max-width:900px;margin:2em auto}}article{{border-top:2px solid #ccc;padding:1em 0}}img{{max-width:100%;border:1px solid #ddd;margin:.5em 0}}.t{{font:12px monospace;background:#eee;padding:2px 6px}}li{{margin:.2em 0}}
  .score{{background:#f6f6f6;border:1px solid #ddd;padding:.6em;margin-top:.6em}}.score label{{margin-right:.6em;white-space:nowrap}}table.items{{width:100%;border-collapse:collapse;margin-bottom:.5em}}table.items td{{border-top:1px solid #e5e5e5;padding:.35em .4em;vertical-align:top}}td.n{{width:1.5em;color:#888}}td.v{{width:24em;font-size:13px}}textarea{{width:100%;height:3em}}#bar{{position:sticky;top:0;background:#fff;border-bottom:1px solid #ccc;padding:.5em 0;z-index:9}}article.done h3::after{{content:" ✓";color:green}}</style>
  <div id=bar><b>{key}</b> · <span id=prog></span> · <button onclick=exp()>Export scores</button> <button onclick=cp()>Copy JSON</button> <span id=msg></span></div>
  <script>
  const K='hera-scores-{key}';let S={{}};try{{S=JSON.parse(localStorage.getItem(K)||'{{}}')}}catch(e){{}}
  function save(id){{const a=document.getElementById(id);const n=+a.querySelector('.score').dataset.n;const items=[];
  for(let j=1;j<=n;j++){{const v=a.querySelector('input[name=v-'+id+'-'+j+']:checked');items.push(v?v.value:null)}}
  S[id]={{items:items,recognized:a.querySelector('.rec').checked,note:a.querySelector('textarea').value,ts:new Date().toISOString()}};
  a.classList.toggle('done',items.every(x=>x));try{{localStorage.setItem(K,JSON.stringify(S))}}catch(e){{}};prog()}}
  function prog(){{const n=document.querySelectorAll('article').length,d=Object.values(S).filter(x=>x.items&&x.items.every(y=>y)).length;document.getElementById('prog').textContent=d+' / '+n+' scored'}}
  function blob(){{return JSON.stringify({{batch:'{key}',exported:new Date().toISOString(),scores:S}},null,1)}}
  function exp(){{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([blob()],{{type:'application/json'}}));a.download='{key}.scores.json';a.click();document.getElementById('msg').textContent='exported'}}
  function cp(){{navigator.clipboard.writeText(blob()).then(()=>document.getElementById('msg').textContent='copied')}}
  window.addEventListener('load',()=>{{for(const id in S){{const a=document.getElementById(id);if(!a)continue;const s=S[id];
  (s.items||[]).forEach((v,k)=>{{if(v){{const e=a.querySelector('input[name=v-'+id+'-'+(k+1)+'][value='+v+']');if(e)e.checked=true}}}});
  a.querySelector('.rec').checked=!!s.recognized;a.querySelector('textarea').value=s.note||'';a.classList.toggle('done',!!(s.items&&s.items.every(y=>y)))}};prog()}})
  </script>''']
  for c in out:
      H.append(f"<article id={c['id']}><h3>{c['id']} <span class=t>{c['type']}</span>{' <span class=t>supersedes '+c['supersedes']+'</span>' if c.get('supersedes') else ''}</h3>")
      H.append(f"<p><b>Claim.</b> {html.escape(c['claim'])}</p><p><b>Context.</b> {html.escape(c['context'])}</p><p><b>Evidence.</b> {html.escape(c['evidence'])}</p>")
      if c['support']: H.append('<p><b>Supporting readings.</b></p><ul>' + ''.join(f'<li>{html.escape(s)}</li>' for s in c['support']) + '</ul>')
      vs = c.get('verbatim_score') or 0
      if c.get('verbatim'):
        flag = '' if vs >= 0.25 else ' <span class=t style="background:#fdd">low match — verify</span>'
        H.append(f'<details open><summary><b>Verbatim source</b> <span class=t>match {vs:.2f}</span>{flag}</summary><pre style="white-space:pre-wrap;background:#fafafa;border:1px solid #eee;padding:.5em;font-size:13px">{html.escape(c["verbatim"])}</pre></details>')
      else: H.append('<p><i>(verbatim source not resolved)</i></p>')
      for b in c['figs']: H.append(f'<img src="data:image/png;base64,{b}">')
      if not c['figs']: H.append('<p><i>(no figure attached)</i></p>')
      cid=c['id']; items = c.get('items') or [c['claim']]
      rows_html = ''.join(f'<tr><td class=n>{j+1}</td><td>{html.escape(it)}</td><td class=v>' + ''.join(f'<label><input type=radio name=v-{cid}-{j+1} value={v}> {v}</label>' for v in ('correct','partial','wrong','unverifiable')) + '</td></tr>' for j, it in enumerate(items))
      H.append(f'''<div class=score data-n={len(items)} onchange="save('{cid}')" oninput="save('{cid}')">
  <table class=items>{rows_html}</table>
  <label><input type=checkbox class=rec> I recognize this run</label><br><textarea placeholder="note (optional): qualms, what you would have claimed instead"></textarea></div></article>''')
  (here/'cards'/f'{key}.html').write_text('\n'.join(H))
from collections import Counter
print(len(out), Counter(c['type'] for c in out), 'with figs:', sum(bool(c['figs']) for c in out), 'excluded:', len(excl), 'merged:', len(merges))

render(key, out)
