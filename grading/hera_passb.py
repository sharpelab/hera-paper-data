#!/usr/bin/env python3
"""Build a Pass B collaborator-debrief page from a HERA session archive.

usage: hera_passb.py <run_key> <archive_dir>

Reads <archive_dir>/*_measure.ipynb + *_ana.ipynb (and cards/<run_key>.cards.jsonl
if present), writes passb/<run_key>.html — a self-contained single-file grading
tool.  Stdlib only.

The page grades the session the way an advisor grades a collaborator: a skim
phase (final call + figure gallery + initial reaction), then a unit-by-unit read
with sound/shaky/wrong rulings, then a final debrief that unlocks only once every
unit is ruled.
"""
import base64
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- scrubbing --
# Copied verbatim from hera_cards.py (importing it would run its pipeline).
SCRUB = [(re.compile(r'(?i)qc0426|vti-0[12]|b1c2|zf1'), '<device>'),
         (re.compile(r'2026-\d\d-\d\d'), '<date>'),
         (re.compile(r'(?i)\b(zack|aaron|qingrui|jordan|isaac|zhiren|nate|nathan|ben|benjamin)\b'), '<name>'),
         (re.compile(r'\b[0-9a-f]{7,40}\b'), '<hash>')]


def scrub(s):
    for rx, rep in SCRUB:
        s = rx.sub(rep, s)
    return s


# ------------------------------------------------------------ notebook read --
def cell_source(c):
    s = c.get('source', '')
    return s if isinstance(s, str) else ''.join(s)


def cell_text_outputs(c):
    """Concatenated stream + text/plain output of a code cell."""
    out = []
    for o in c.get('outputs', []):
        if o.get('output_type') == 'stream':
            t = o.get('text', '')
            out.append(t if isinstance(t, str) else ''.join(t))
        elif o.get('output_type') == 'error':
            tb = o.get('traceback') or []
            out.append('\n'.join(tb))
        else:
            d = o.get('data', {})
            if 'text/plain' in d:
                t = d['text/plain']
                out.append(t if isinstance(t, str) else ''.join(t))
    return ''.join(out)


def cell_pngs(c):
    out = []
    for o in c.get('outputs', []):
        d = o.get('data', {})
        if 'image/png' in d:
            b = d['image/png']
            out.append(b if isinstance(b, str) else ''.join(b))
    return out


def is_header(c):
    return c['cell_type'] == 'markdown' and cell_source(c).lstrip().startswith('#')


# ------------------------------------------------------------- markdown ------
FENCE = re.compile(r'^\s*```')
TABLE_SEP = re.compile(r'^\s*\|?[\s:|-]+\|[\s:|-]*$')


def _inline(s):
    """Escape, then apply inline markdown.  Code spans are protected first."""
    spans, esc = [], []

    def stash(m):
        spans.append(m.group(1))
        return '\x00%d\x00' % (len(spans) - 1)

    def stash_esc(m):
        esc.append(m.group(1))
        return '\x01%d\x01' % (len(esc) - 1)

    s = re.sub(r'`([^`]+)`', stash, s)
    s = re.sub(r'\\([\\`*_\[\]()#+\-.!~|{}<>])', stash_esc, s)
    s = html.escape(s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', s)
    s = re.sub(r'(?<![\w`])_([^_\n]+)_(?![\w`])', r'<i>\1</i>', s)
    s = re.sub(r'\x01(\d+)\x01', lambda m: html.escape(esc[int(m.group(1))]), s)
    return re.sub(r'\x00(\d+)\x00', lambda m: '<code>' + html.escape(spans[int(m.group(1))]) + '</code>', s)


def md_to_html(src):
    """Minimal markdown -> HTML.  Headers, lists, tables, fences, quotes, rules."""
    lines = src.split('\n')
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if FENCE.match(ln):
            i += 1
            buf = []
            while i < len(lines) and not FENCE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append('<pre class=code>%s</pre>' % html.escape('\n'.join(buf)))
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            n = min(len(m.group(1)) + 2, 6)
            out.append('<h%d>%s</h%d>' % (n, _inline(m.group(2)), n))
            i += 1
            continue
        if re.match(r'^\s*(---+|\*\*\*+|___+)\s*$', ln):
            out.append('<hr>')
            i += 1
            continue
        if ln.lstrip().startswith('>'):
            buf = []
            while i < len(lines) and (lines[i].lstrip().startswith('>') or (buf and lines[i].strip())):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            out.append('<blockquote>%s</blockquote>' % _inline(' '.join(x for x in buf if x.strip())))
            continue
        # table: a header row followed by a |---|---| separator
        if '|' in ln and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]) and '|' in lines[i + 1]:
            def cells(row):
                r = row.strip()
                r = r[1:] if r.startswith('|') else r
                r = r[:-1] if r.endswith('|') else r
                return [c.strip() for c in r.split('|')]
            head = cells(ln)
            i += 2
            body = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                body.append(cells(lines[i]))
                i += 1
            t = ['<table><thead><tr>' + ''.join('<th>%s</th>' % _inline(c) for c in head) + '</tr></thead><tbody>']
            for r in body:
                t.append('<tr>' + ''.join('<td>%s</td>' % _inline(c) for c in r) + '</tr>')
            t.append('</tbody></table>')
            out.append(''.join(t))
            continue
        m = re.match(r'^\s*([-*+]|\d+[.)])\s+(.*)$', ln)
        if m:
            ordered = not m.group(1) in ('-', '*', '+')
            items = []
            while i < len(lines):
                m2 = re.match(r'^\s*([-*+]|\d+[.)])\s+(.*)$', lines[i])
                if m2:
                    items.append(m2.group(2))
                    i += 1
                elif lines[i].strip() and lines[i].startswith((' ', '\t')) and items:
                    items[-1] += ' ' + lines[i].strip()
                    i += 1
                else:
                    break
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % _inline(x) for x in items), tag))
            continue
        if not ln.strip():
            i += 1
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not FENCE.match(lines[i]) \
                and not re.match(r'^(#{1,6})\s+', lines[i]) and not lines[i].lstrip().startswith('>') \
                and not re.match(r'^\s*([-*+]|\d+[.)])\s+', lines[i]):
            buf.append(lines[i])
            i += 1
        out.append('<p>%s</p>' % _inline(' '.join(buf)))
    return '\n'.join(out)


# ------------------------------------------------------------- data ids ------
DATA_PATH_RX = re.compile(r'data[/\\](\d+)')
RUN_RANGE_RX = re.compile(r'(?i)\bruns?\s*#?\s*(\d+)\s*[‐-―-]\s*(\d+)\b')
RUN_RX = re.compile(r'(?i)\bruns?\s*#?\s*(\d+)\b')
# Produced-run marker written by the lab sweep library on every acquisition.
SWEEP_ID_RX = re.compile(r'(?i)\bstarting\s+\w*sweep\s+with\s+ID\s+(\d+)\b')


def mentioned_ids(text):
    ids = set(int(x) for x in DATA_PATH_RX.findall(text))
    for a, b in RUN_RANGE_RX.findall(text):
        a, b = int(a), int(b)
        if 0 <= b - a <= 32:
            ids |= set(range(a, b + 1))
    ids |= set(int(x) for x in RUN_RX.findall(text))
    return ids


# ------------------------------------------------------------- units ---------
class Unit:
    def __init__(self, nb, start, cells):
        self.nb = nb
        self.start = start
        self.end = start
        self.cells = cells          # list of (global_index, cell)
        self.title = ''
        self.note = ''
        self.bringup = False
        self.context = False
        self.context_reason = ''
        self.ids = set()
        self.inline = []            # attached ana Units
        self.cards = []

    @property
    def uid(self):
        return ('m' if self.nb == 'measure' else 'a') + '-' + str(self.start)


def segment(nb_name, cells):
    units, cur = [], None
    for i, c in enumerate(cells):
        if is_header(c):
            cur = Unit(nb_name, i, [])
            units.append(cur)
        elif cur is None:
            cur = Unit(nb_name, i, [])
            cur.title = '(preamble)'
            units.append(cur)
        cur.cells.append((i, c))
        cur.end = i
    for u in units:
        if not u.title:
            first = cell_source(u.cells[0][1]).lstrip().split('\n')[0]
            t = scrub(re.sub(r'^#+\s*', '', first).strip())
            t = re.sub(r'\\([\\`*_])', r'\1', t.replace('`', '').replace('**', ''))
            u.title = t.strip()
    return units


HERA_MARK = re.compile(r'#\s*HERA', re.I)
# Protocol acts that open every agent-run session: the handshake, the kernel
# probe, the read-only VERIFY gate.  Recognised only in the run-up to the first
# acquisition, so a science unit that happens to say "Verify" is untouched.
PROTOCOL_TITLE = re.compile(r'(?i)\b(session[\s-]*start|kernel[\s-]*(?:binding[\s-]*)?probe|verify)\b')
TEMPLATE_MIN_ARCHIVES = 3


def norm_cell(s):
    return re.sub(r'\s+', ' ', scrub(s)).strip()


def template_index(arch):
    """Normalized cell sources that recur across sibling session archives.

    Boilerplate is what survives from run to run: the notebook template, the
    bring-up ritual, the analysis-discipline preamble.  A cell present in
    TEMPLATE_MIN_ARCHIVES or more of the sibling archives is not this session's
    work.  Too few siblings to judge -> empty index, detection stands down.
    """
    sibs = sorted(p for p in arch.parent.glob('*-session') if p.is_dir())
    if len(sibs) < TEMPLATE_MIN_ARCHIVES:
        return set(), 0
    seen = {}
    for a in sibs:
        here_cells = set()
        for p in a.glob('*.ipynb'):
            try:
                cells = json.load(open(p, encoding='utf-8'))['cells']
            except Exception:
                continue
            for c in cells:
                t = norm_cell(cell_source(c))
                if t:
                    here_cells.add(t)
        for t in here_cells:
            seen[t] = seen.get(t, 0) + 1
    return {t for t, n in seen.items() if n >= TEMPLATE_MIN_ARCHIVES}, len(sibs)


def mark_context(m_units, a_units, tmpl, final_call):
    """Flag protocol/template units as ungraded context.

    Rails: a unit that produced or analysed data, and the final-call unit, are
    always graded no matter what they match.
    """
    first_data = next((i for i, u in enumerate(m_units) if u.ids), len(m_units))
    for seq in (m_units, a_units):
        for i, u in enumerate(seq):
            u.context, u.context_reason = False, ''
            if u.ids or u is final_call:
                continue
            mds = [norm_cell(cell_source(c)) for _, c in u.cells if c['cell_type'] == 'markdown']
            mds = [t for t in mds if t]
            if getattr(u, 'bringup', False):
                u.context, u.context_reason = True, 'operator-run bring-up'
            elif seq is m_units and i < first_data and PROTOCOL_TITLE.search(u.title):
                u.context, u.context_reason = True, 'session protocol'
            elif mds and tmpl and all(t in tmpl for t in mds):
                u.context, u.context_reason = True, 'notebook template'


def collapse_bringup(units, cells):
    """Everything before the agent's first cell is operator work (bring-up +
    safety gates); the agent's first act is VERIFY.  Fold it into one context
    unit so it is read but not graded as the collaborator's.  No marker cell
    (a notebook that isn't agent-run) leaves the sequence untouched."""
    boundary = next((i for i, c in enumerate(cells) if HERA_MARK.search(cell_source(c))), None)
    if boundary is None or boundary == 0:
        return units
    pre = [u for u in units if u.start < boundary]
    rest = [u for u in units if u.start >= boundary]
    if len(pre) < 2:
        return units
    merged = Unit(pre[0].nb, pre[0].start, [c for u in pre for c in u.cells])
    merged.end = pre[-1].end
    merged.title = 'Session bring-up (operator-run)'
    merged.bringup = True
    return [merged] + rest


def unit_ids(u, use_produced):
    """Data ids this unit is about.

    measure: the ids it *produced* (from the sweep library's run-id log line).
    ana:     the ids named in its header title, else anywhere in its source.
    """
    if u.nb == 'measure' and use_produced:
        ids = set()
        for _, c in u.cells:
            ids |= set(int(x) for x in SWEEP_ID_RX.findall(cell_text_outputs(c)))
        return ids
    head = cell_source(u.cells[0][1]).lstrip().split('\n')[0]
    ids = mentioned_ids(head)
    if not ids:
        # Fall back only to explicit data/<n> loads in the body.  Prose "run N"
        # outside the header names inputs and neighbours, not the unit's subject.
        body = '\n'.join(cell_source(c) for _, c in u.cells)
        ids = set(int(x) for x in DATA_PATH_RX.findall(body))
    return ids


# ------------------------------------------------------------- rendering -----
def render_code(gidx, nb, src):
    src = scrub(src)
    lines = src.split('\n')
    body = '<pre class=code>%s</pre>' % html.escape(src)
    badge = '<span class=badge>%s %d</span>' % (nb, gidx)
    if len(lines) > 40:
        peek = html.escape('\n'.join(lines[:5]))
        return ('<div class=cell><details><summary>%s<span class=more>%d lines</span>'
                '<pre class="code peek">%s</pre></summary>%s</details></div>'
                % (badge, len(lines), peek, body))
    return '<div class=cell>%s%s</div>' % (badge, body)


def render_outputs(c):
    parts = []
    txt = scrub(cell_text_outputs(c))
    if txt.strip():
        lines = txt.split('\n')
        pre = '<pre class=out>%s</pre>' % html.escape(txt)
        if len(lines) > 60:
            peek = html.escape('\n'.join(lines[:5]))
            parts.append('<details class=outwrap><summary><span class=more>output, %d lines</span>'
                         '<pre class="out peek">%s</pre></summary>%s</details>' % (len(lines), peek, pre))
        else:
            parts.append(pre)
    for b in cell_pngs(c):
        parts.append('<img src="data:image/png;base64,%s">' % b)
    return ''.join(parts)


def render_cell(gidx, nb, c):
    if c['cell_type'] == 'markdown':
        return ('<div class="cell md"><span class=badge>%s %d</span>%s</div>'
                % (nb, gidx, md_to_html(scrub(cell_source(c)))))
    return render_code(gidx, nb, cell_source(c)) + render_outputs(c)


def render_unit_body(u):
    return '\n'.join(render_cell(i, u.nb, c) for i, c in u.cells)


def render_passa(u):
    if not u.cards:
        return ''
    rows = []
    for c in u.cards:
        items = c.get('items') or []
        li = ''.join('<li>%s</li>' % html.escape(scrub(x)) for x in items)
        rows.append('<div class=pacard><p>%s</p>%s</div>'
                    % (html.escape(scrub(c['claim'])), ('<ul>%s</ul>' % li) if li else ''))
    return ('<details class=passa><summary>What Pass A extracted here (%d claim%s)</summary>%s</details>'
            % (len(u.cards), '' if len(u.cards) == 1 else 's', ''.join(rows)))


WIDGET = """<div class=grade data-uid="%(uid)s">
<div class=btns>
<button type=button class=r data-v=sound onclick="rule('%(uid)s','sound')">sound</button>
<button type=button class=r data-v=shaky onclick="rule('%(uid)s','shaky')">shaky</button>
<button type=button class=r data-v=wrong onclick="rule('%(uid)s','wrong')">wrong</button>
<button type=button class=r data-v=na onclick="rule('%(uid)s','na')">n/a</button>
<span class=ts></span></div>
<textarea class=note rows=3 placeholder="optional — cite what you saw"
 oninput="noteIn('%(uid)s',this)"></textarea></div>"""


CSS = """
:root{--ink:#1a1a1a;--line:#ddd;--mut:#777}
*{box-sizing:border-box}
body{font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;margin:0}
a{color:#0645ad}
#side{position:fixed;left:0;top:0;bottom:0;width:220px;overflow-y:auto;border-right:1px solid var(--line);
 background:#fafafa;padding:.6em .5em 3em;font-size:12px}
#side h4{margin:.4em 0 .6em;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
#side a{display:block;padding:.25em .3em;color:var(--ink);text-decoration:none;border-radius:3px;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#side a:hover{background:#eee}
#side a.here{background:#e6eefc}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:#ccc;vertical-align:middle}
.dot.sound{background:#2a7}.dot.shaky{background:#e9a417}.dot.wrong{background:#c33}.dot.na{background:#8a8a8a}
#main{margin-left:220px;max-width:950px;padding:0 1.6em 6em}
#bar{position:sticky;top:0;z-index:9;background:#fff;border-bottom:1px solid var(--line);
 padding:.6em 0;margin-bottom:1em;display:flex;gap:1em;align-items:center;flex-wrap:wrap}
#bar b{font-size:15px}
#prog{color:var(--mut)}
#gradebar{flex:1;min-width:200px;display:flex;gap:.8em;align-items:center}
#pfill{height:4px;background:#2a7;width:0;transition:width .2s;display:block}
#ptrack{flex:1;min-width:120px;height:4px;background:#eee}
button{font:13px inherit;padding:.3em .8em;border:1px solid #bbb;background:#f6f6f6;border-radius:3px;cursor:pointer}
button:hover{background:#eee}
section.unit{border-top:2px solid #ccc;padding:1.2em 0 1.4em;scroll-margin-top:60px}
section.unit.cur{box-shadow:-6px 0 0 -2px #9bb8e8}
section.unit>h2{font-size:17px;margin:.1em 0 .8em}
p.unote{margin:-.5em 0 .9em;padding:.35em .7em;background:#fdf6e3;border-left:3px solid #e0c26a;
 color:#5c4a12;font-size:13px}
.cell{margin:.7em 0}
.md{line-height:1.68;max-width:74ch}
.md h3,.md h4,.md h5,.md h6{margin:1.1em 0 .4em;line-height:1.3}
.md h3:first-child,.md h4:first-child,.md h5:first-child,.md h6:first-child{margin-top:.2em}
.md p{margin:0 0 .95em}
.md ul,.md ol{margin:0 0 .95em;padding-left:1.5em}
.md li{margin:.3em 0}
.md li>ul,.md li>ol{margin:.3em 0}
.md blockquote{margin:0 0 1em;padding:.55em .9em;border-left:3px solid #c3cde0;background:#f5f7fb;
 color:#33415c;font-size:14px}
.md blockquote p{margin:0}
.md code{background:#f2f2f2;padding:0 3px;border-radius:3px;font-size:.93em}
.md table{border-collapse:collapse;margin:.5em 0;font-size:13px}
.md th,.md td{border:1px solid var(--line);padding:.25em .5em;text-align:left}
.badge{display:inline-block;font:11px ui-monospace,Menlo,Consolas,monospace;background:#eee;color:#555;
 padding:1px 6px;border-radius:3px;margin-right:.5em;vertical-align:middle}
pre.code{font:12.5px/1.45 ui-monospace,Menlo,Consolas,monospace;background:#f7f7f7;border:1px solid #eee;
 border-left:3px solid #ccc;padding:.6em .7em;overflow-x:auto;white-space:pre;margin:.3em 0}
pre.out{font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;background:#fcfcfc;border:1px solid #f0f0f0;
 padding:.5em .7em;overflow-x:auto;white-space:pre-wrap;margin:.3em 0;color:#333}
pre.peek{margin:.3em 0 0;opacity:.75;pointer-events:none}
summary{cursor:pointer}
.more{font:11px ui-monospace,monospace;color:var(--mut)}
img{max-width:100%;border:1px solid #eee;margin:.4em 0;display:block}
.ana{margin:.8em 0 .8em 1.4em;padding:.5em .9em;background:#f6f8f4;border-left:3px solid #b9d0a8}
.ana>.tag{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#5e7a4a}
.grade{background:#f6f6f6;border:1px solid var(--line);padding:.6em .7em;margin-top:1em}
.btns{display:flex;gap:.5em;align-items:center}
.grade button.r[data-v=sound].on{background:#2a7;border-color:#2a7;color:#fff}
.grade button.r[data-v=shaky].on{background:#e9a417;border-color:#e9a417;color:#fff}
.grade button.r[data-v=wrong].on{background:#c33;border-color:#c33;color:#fff}
.grade button.r[data-v=na].on{background:#8a8a8a;border-color:#8a8a8a;color:#fff}
.grade .ts{font:11px ui-monospace,monospace;color:var(--mut)}
textarea{width:100%;font:14px/1.5 inherit;padding:.5em .6em;border:1px solid #ccc;border-radius:3px;
 margin-top:.5em;resize:vertical;overflow:hidden;min-height:4.6em}
textarea.note{background:#fff}
details.passa{margin-top:1em;background:#fbfbfb;border:1px solid #eee;padding:.5em .7em}
details.passa>summary{font-size:13px;color:#555}
.pacard{border-top:1px solid #eee;padding:.5em 0;font-size:13.5px}
.pacard p{margin:.2em 0}
.pacard ul{margin:.3em 0 .3em 1.2em;padding:0;color:#444;font-size:13px}
fieldset{border:1px solid var(--line);padding:.9em 1em;margin:1em 0}
fieldset legend{font-weight:bold;padding:0 .4em}
fieldset[disabled]{opacity:.45;background:#fafafa}
fieldset[disabled] *{pointer-events:none}
.q{margin:.9em 0}
.q>label.lead{display:block;font-weight:bold;margin-bottom:.3em}
.q label{display:block;margin:.15em 0}
.hint{color:var(--mut);font-size:13px}
#gallery figure{margin:1.2em 0}
#gallery figcaption{font:11px ui-monospace,monospace;color:var(--mut);margin-bottom:.2em}
.hidden{display:none!important}
body.skimming #side{display:none}
body.skimming #main{margin-left:0;margin-right:auto;margin-left:auto}
#skimdone{margin:1em 0}
kbd{font:11px ui-monospace,monospace;border:1px solid #ccc;border-bottom-width:2px;border-radius:3px;padding:0 4px;background:#f6f6f6}
"""


JS = r"""
const KEY = 'hera-passb-__KEY__';
const RUN = '__KEY__';
let S = {phase:'skim', units:{}, skim:{}, final:{}, events:[]};
try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(S, JSON.parse(raw)); } catch(e){}
if (!S.units) S.units = {};
if (!S.skim) S.skim = {};
if (!S.final) S.final = {};
if (!S.events) S.events = [];

const now = () => new Date().toISOString();
function ev(kind, target, value){
  S.events.push({ts: now(), kind: kind, target: target || null, value: (value === undefined ? null : value)});
  if (S.events.length > 8000) S.events.splice(0, S.events.length - 8000);
}
function save(){ try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e){} }

/* ---------------------------------------------------------------- rulings */
function rule(uid, v){
  const prev = S.units[uid] || {};
  S.units[uid] = {ruling: v, note: prev.note || '', ts: now()};
  ev('rule', uid, v);
  paint(uid); progress(); save();
}
function grow(el){
  if (!el || el.tagName !== 'TEXTAREA') return;
  el.style.height = 'auto';
  el.style.height = Math.max(el.scrollHeight + 2, 74) + 'px';
}
function noteIn(uid, el){
  grow(el);
  const prev = S.units[uid] || {ruling:null, ts:null};
  prev.note = el.value; S.units[uid] = prev;
  clearTimeout(noteIn['t_'+uid]);
  noteIn['t_'+uid] = setTimeout(function(){ ev('note', uid, el.value.length); save(); }, 900);
  save();
}
function paint(uid){
  const st = S.units[uid] || {};
  const g = document.querySelector('.grade[data-uid="'+uid+'"]');
  if (g){
    g.querySelectorAll('button.r').forEach(b => b.classList.toggle('on', b.dataset.v === st.ruling));
    g.querySelector('.ts').textContent = st.ts ? st.ts.slice(11,16) : '';
    const ta = g.querySelector('textarea');
    if (ta.value !== (st.note || '')) ta.value = st.note || '';
    grow(ta);
  }
  const d = document.querySelector('#side a[data-uid="'+uid+'"] .dot');
  if (d) d.className = 'dot' + (st.ruling ? ' ' + st.ruling : '');
}
function ruledCount(){ return UNITS.filter(u => (S.units[u.uid]||{}).ruling).length; }
function progress(){
  const n = ruledCount(), m = UNITS.length;
  document.getElementById('prog').textContent = n + ' of ' + m + ' units ruled';
  document.getElementById('pfill').style.width = (100*n/m) + '%';
  const fs = document.getElementById('finalfs');
  const open = (n === m);
  if (fs.disabled === open){
    fs.disabled = !open;
    if (open) ev('final_unlocked');
  }
  document.getElementById('finalhint').classList.toggle('hidden', open);
}

/* ------------------------------------------------------------- navigation */
let cur = 0;
function setCur(i, scroll){
  cur = Math.max(0, Math.min(UNITS.length - 1, i));
  const uid = UNITS[cur].uid;
  document.querySelectorAll('section.unit').forEach(s => s.classList.toggle('cur', s.id === 'u-'+uid));
  document.querySelectorAll('#side a').forEach(a => a.classList.toggle('here', a.dataset.uid === uid));
  if (scroll) document.getElementById('u-'+uid).scrollIntoView({block:'start', behavior:'smooth'});
}
function onScroll(){
  if (S.phase !== 'full') return;
  const mark = window.innerHeight * 0.35;
  let i = 0;
  UNITS.forEach((u, k) => {
    const e = document.getElementById('u-'+u.uid);
    if (e && e.getBoundingClientRect().top < mark) i = k;
  });
  if (i !== cur) setCur(i, false);
}
document.addEventListener('keydown', function(e){
  if (S.phase !== 'full') return;
  const t = e.target.tagName;
  if (t === 'TEXTAREA' || t === 'INPUT' || e.metaKey || e.ctrlKey || e.altKey) return;
  const uid = UNITS[cur].uid;
  if (e.key === '1'){ rule(uid, 'sound'); e.preventDefault(); }
  else if (e.key === '2'){ rule(uid, 'shaky'); e.preventDefault(); }
  else if (e.key === '3'){ rule(uid, 'wrong'); e.preventDefault(); }
  else if (e.key === '4'){ rule(uid, 'na'); e.preventDefault(); }
  else if (e.key === 'j'){ setCur(cur + 1, true); ev('nav', UNITS[Math.min(cur, UNITS.length-1)].uid, 'j'); e.preventDefault(); }
  else if (e.key === 'k'){ setCur(cur - 1, true); ev('nav', UNITS[Math.max(cur,0)].uid, 'k'); e.preventDefault(); }
  else if (e.key === 'n'){
    const ta = document.querySelector('.grade[data-uid="'+uid+'"] textarea');
    if (ta){ ta.focus(); ev('note_focus', uid); e.preventDefault(); }
  }
});

/* ------------------------------------------------------------- skim phase */
const SKIM_FIELDS = ['know_text','know_adjudicated','skim_disposition','skim_supervision','skim_impression'];
const SKIM_REQUIRED = ['skim_disposition','skim_supervision','skim_impression'];
const FINAL_FIELDS = ['final_disposition','reanalysis','remeasure','final_supervision',
                      'overall_read','omission','biggest_right','biggest_wrong'];
function filled(obj, fields, extra){
  const out = {};
  fields.forEach(function(f){ out[f] = (obj[f] === undefined || obj[f] === null) ? '' : obj[f]; });
  (extra || []).forEach(function(f){ out[f] = obj[f] || null; });
  return out;
}
function skimIn(name, value){
  S.skim[name] = value; S.skim.ts = now();
  ev('skim_field', name, (name === 'skim_impression' || name === 'know_text') ? value.length : value);
  checkSkim(); save();
}
function checkSkim(){
  const ok = SKIM_REQUIRED.every(f => S.skim[f] !== undefined && String(S.skim[f]).trim() !== '');
  document.getElementById('beginbtn').disabled = !ok;
}
function beginRead(){
  S.phase = 'full'; S.skim.began_ts = now(); ev('begin_full_read');
  save(); applyPhase(); window.scrollTo(0, 0); setCur(0, false);
}
function sideClick(uid){
  const i = UNITS.findIndex(u => u.uid === uid);
  ev('nav_click', uid);
  if (i >= 0) setCur(i, false);          // context units are not in the ruling sequence
  save();
}
function applyPhase(){
  const full = S.phase === 'full';
  document.body.classList.toggle('skimming', !full);
  document.getElementById('skim').classList.toggle('hidden', full);
  document.getElementById('skimbanner').classList.toggle('hidden', !full);
  document.getElementById('full').classList.toggle('hidden', !full);
  document.getElementById('gradebar').classList.toggle('hidden', !full);
  if (full){
    document.getElementById('skimfs').disabled = true;
    const t = S.skim.began_ts || '';
    document.getElementById('skimtime').textContent = t ? t.slice(11,16) : '--:--';
  }
}

/* ------------------------------------------------------------ final debrief */
const FINAL_TEXT = ['reanalysis','remeasure','overall_read','omission','biggest_right','biggest_wrong'];
function finalIn(name, value){
  S.final[name] = value; S.final.ts = now();
  ev('final_field', name, (FINAL_TEXT.indexOf(name) >= 0) ? String(value).length : value);
  if (name === 'final_disposition') condFields();
  save();
}
function condFields(){
  document.getElementById('q_reanalysis').classList.toggle('hidden', S.final.final_disposition !== 'b');
  document.getElementById('q_remeasure').classList.toggle('hidden', S.final.final_disposition !== 'c');
}

/* ------------------------------------------------------- export / import */
function payload(){
  return {
    run_key: RUN,
    exported: now(),
    phase: S.phase,
    units: UNITS.concat(CONTEXT).map(function(u){
      const st = S.units[u.uid] || {};
      return {unit_id: u.uid, notebook: u.nb, cell_range: u.range, title: u.title,
              inline: u.inline, data_ids: u.ids,
              context: !!u.context, context_reason: u.context_reason || null,
              ruling: st.ruling || null, note: st.note || '', ts: st.ts || null};
    }),
    skim: filled(S.skim, SKIM_FIELDS, ['ts','began_ts']),
    final: filled(S.final, FINAL_FIELDS, ['ts']),
    events: S.events
  };
}
function exportJSON(){
  ev('export'); save();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(payload(), null, 1)], {type:'application/json'}));
  a.download = RUN + '.passb.json';
  a.click();
  document.getElementById('msg').textContent = 'exported';
}
function importJSON(input){
  const f = input.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = function(){
    try {
      const d = JSON.parse(r.result);
      S.units = {};
      (d.units || []).forEach(function(u){
        if (u.ruling || u.note) S.units[u.unit_id] = {ruling: u.ruling, note: u.note || '', ts: u.ts};
      });
      S.skim = d.skim || {}; S.final = d.final || {};
      S.events = d.events || []; S.phase = d.phase || 'skim';
      ev('import', f.name);
      save(); restore();
      document.getElementById('msg').textContent = 'imported';
    } catch(e){ document.getElementById('msg').textContent = 'import failed: ' + e.message; }
  };
  r.readAsText(f);
  input.value = '';
}

/* ------------------------------------------------------------------ boot */
function restore(){
  UNITS.forEach(u => paint(u.uid));
  SKIM_FIELDS.forEach(function(f){
    const v = S.skim[f]; if (v === undefined) return;
    const el = document.querySelector('[data-f="'+f+'"]');
    if (el){ el.value = v; grow(el); }
    else { const r = document.querySelector('input[name="'+f+'"][value="'+v+'"]'); if (r) r.checked = true; }
  });
  ['final_disposition','final_supervision'].forEach(function(f){
    const r = document.querySelector('input[name="'+f+'"][value="'+S.final[f]+'"]'); if (r) r.checked = true;
  });
  FINAL_TEXT.forEach(function(f){
    const el = document.querySelector('[data-f="'+f+'"]');
    if (el && S.final[f] !== undefined){ el.value = S.final[f]; grow(el); }
  });
  const echo = (S.skim.know_text ? S.skim.know_text : '(not answered)') +
    '  — knew the adjudicated answer: ' + (S.skim.know_adjudicated || '(not answered)');
  document.getElementById('knowecho').textContent = echo;
  document.getElementById('knowecho2').textContent = echo;
  condFields(); checkSkim(); applyPhase(); progress();
  if (S.phase === 'full') setCur(0, false);
}
window.addEventListener('scroll', onScroll, {passive:true});
window.addEventListener('load', function(){ ev('load'); restore(); save(); });
"""


def enrich_items(cards, own_path):
    """Per-run card files carry no `items`; the enumerated assertions live in the
    re-pooled card file under different ids.  Join on exact claim text, and only
    where that text is unambiguous across the corpus."""
    idx, dup = {}, set()
    for p in sorted((HERE / 'cards').glob('*.cards.jsonl')):
        if p == own_path:
            continue
        for line in open(p, encoding='utf-8'):
            if not line.strip():
                continue
            r = json.loads(line)
            if not r.get('items'):
                continue
            k = r['claim'].strip()
            if k in idx and idx[k] != r['items']:
                dup.add(k)
            idx[k] = r['items']
    n = 0
    for c in cards:
        k = c['claim'].strip()
        if not c.get('items') and k in idx and k not in dup:
            c['items'] = idx[k]
            n += 1
    return n


def build(key, arch):
    arch = pathlib.Path(arch)
    nbs = {}
    for p in sorted(arch.glob('*.ipynb')):
        kind = 'ana' if '_ana' in p.name else ('measure' if '_measure' in p.name else None)
        if kind:
            nbs[kind] = json.load(open(p, encoding='utf-8'))['cells']
    if 'measure' not in nbs or 'ana' not in nbs:
        sys.exit('need both *_measure.ipynb and *_ana.ipynb in %s' % arch)

    have = {int(d.name) for d in (arch / 'data').glob('*') if d.is_dir() and d.name.isdigit()}

    m_units = collapse_bringup(segment('measure', nbs['measure']), nbs['measure'])
    a_units = segment('ana', nbs['ana'])
    produced = any(SWEEP_ID_RX.search(cell_text_outputs(c)) for c in nbs['measure'])
    for u in m_units:
        u.ids = unit_ids(u, produced) & have
    for u in a_units:
        u.ids = unit_ids(u, False) & have

    # attach each ana unit to the LAST measure unit it shares a data id with
    standalone = []
    for a in a_units:
        host = None
        for m in m_units:
            if a.ids & m.ids:
                host = m
        if host is None:
            standalone.append(a)
        else:
            host.inline.append(a)
    seq = m_units + standalone

    final_call = None
    for a in a_units:
        if a.cells and a.cells[0][1]['cell_type'] == 'markdown':
            final_call = a
    tmpl, n_sibs = template_index(arch)
    mark_context(m_units, standalone, tmpl, final_call)
    graded = [u for u in seq if not u.context]
    context = [u for u in seq if u.context]

    # Pass A cards: anchor first, data_ids fallback
    cards, unmatched = [], []
    cp = HERE / 'cards' / ('%s.cards.jsonl' % key)
    if cp.exists():
        cards = [json.loads(l) for l in open(cp, encoding='utf-8') if l.strip()]
        enriched = enrich_items(cards, cp)
    else:
        enriched = 0
    anchor_rx = re.compile(r'^\[(measure|ana) cell (\d+)\]')
    for c in cards:
        m = anchor_rx.match(c.get('verbatim') or '')
        placed = None
        if m:
            nb, idx = m.group(1), int(m.group(2))
            for u in seq:
                spans = [(u.nb, u.start, u.end)] + [(a.nb, a.start, a.end) for a in u.inline]
                if any(n == nb and s <= idx <= e for n, s, e in spans):
                    placed = u
                    break
        if placed is None:
            ids = set(c.get('data_ids') or [])
            best = None
            for u in seq:
                allids = set(u.ids)
                for a in u.inline:
                    allids |= a.ids
                if ids & allids:
                    best = u
            placed = best
        if placed is None:
            unmatched.append(c['id'])
        else:
            placed.cards.append(c)

    # Context units are export-only (not rendered): fold any cards anchored in
    # one into the next graded unit's Pass A panel so no card disappears.
    carry = []
    for u in seq:
        if u.context:
            for c in u.cards:
                c = dict(c)
                c['claim'] = '(from excluded context) ' + c['claim']
                carry.append(c)
            u.cards = []
        elif carry:
            u.cards = carry + u.cards
            carry = []
    if carry and graded:
        graded[-1].cards.extend(carry)

    # ------------------------------------------------------------ rendering --
    gallery = []
    for i, c in enumerate(nbs['ana']):
        for b in cell_pngs(c):
            gallery.append((i, b))

    def radio(name, opts):
        return ''.join('<label><input type=radio name="%s" value="%s" onchange="%s(\'%s\',this.value)"> %s</label>'
                       % (name, v, 'skimIn' if name.startswith('skim') or name.startswith('know') else 'finalIn',
                          name, html.escape(t))
                       for v, t in opts)

    DISP = [('a', 'a — answers the brief as-is'),
            ('b', 'b — answers it after specified re-analysis'),
            ('c', 'c — needs re-measurement to answer it'),
            ('d', 'd — does not answer it, start over')]
    SUP = [('a', 'a — hand them the fridge, read the draft'),
           ('b', 'b — trust their sweeps, check their analysis'),
           ('c', 'c — check every decision'),
           ('d', 'd — not alone with the rig')]

    H = ['<!doctype html><html lang=en><head><meta charset=utf-8>',
         '<title>Pass B — %s</title>' % html.escape(key),
         '<style>%s</style></head><body class=skimming>' % CSS]

    # sidebar
    side = ['<nav id=side><h4>Units</h4>']
    for u in graded:
        t = u.title if len(u.title) <= 46 else u.title[:45] + '…'
        side.append('<a href="#u-%s" data-uid="%s" onclick="sideClick(\'%s\')"><span class=dot></span>%s</a>'
                    % (u.uid, u.uid, u.uid, html.escape(t)))
    side.append('</nav>')
    H.append(''.join(side))

    H.append('<div id=main>')
    H.append('<div id=bar><b>Pass B — %s</b>'
             '<span id=gradebar class=hidden><span id=prog></span>'
             '<span id=ptrack><span id=pfill></span></span></span>'
             '<button type=button onclick="exportJSON()">Export JSON</button>'
             '<label class=hint>Import <input type=file accept="application/json" '
             'onchange="importJSON(this)" style="font-size:11px;width:auto"></label>'
             '<span id=msg class=hint></span></div>' % html.escape(key))

    # ---- skim phase
    H.append('<div id=skim><fieldset id=skimfs><legend>Skim — initial reaction</legend>')
    H.append('<div class=q><label class=lead>Before reading: what do you believe this device’s '
             'stacking is, and do you know the adjudicated answer?</label>'
             '<textarea rows=3 data-f=know_text placeholder="your prior on the stacking" '
             'oninput="skimIn(\'know_text\',this.value)" onchange="skimIn(\'know_text\',this.value)">'
             '</textarea>'
             '<div style="margin-top:.4em">Do you know the adjudicated answer? '
             '<label style="display:inline;margin-right:1em"><input type=radio name=know_adjudicated value=yes '
             'onchange="skimIn(\'know_adjudicated\',this.value)"> yes</label>'
             '<label style="display:inline"><input type=radio name=know_adjudicated value=no '
             'onchange="skimIn(\'know_adjudicated\',this.value)"> no</label></div></div>')
    H.append('<hr><h2>The call</h2>')
    if final_call:
        H.append(render_unit_body(final_call))
    H.append('<h2>Figures (analysis notebook, in order)</h2><div id=gallery>')
    for i, b in gallery:
        H.append('<figure><figcaption>ana %d</figcaption>'
                 '<img src="data:image/png;base64,%s"></figure>' % (i, b))
    H.append('</div><hr><h2>Initial reaction</h2>')
    H.append('<div class=q><label class=lead>Does this answer the brief?</label>%s</div>' % radio('skim_disposition', DISP))
    H.append('<div class=q><label class=lead>How much supervision would you give this collaborator next time?</label>%s</div>'
             % radio('skim_supervision', SUP))
    H.append('<div class=q><label class=lead>First impression, one sentence.</label>'
             '<textarea rows=3 data-f=skim_impression oninput="skimIn(\'skim_impression\',this.value)" '
             'onchange="skimIn(\'skim_impression\',this.value)"></textarea></div>')
    H.append('</fieldset><div id=skimdone><button type=button id=beginbtn disabled onclick="beginRead()">'
             'Begin full read</button> <span class=hint>enabled once disposition, supervision and '
             'first impression are set</span></div></div>')

    H.append('<details id=skimbanner class=hidden><summary>Initial reaction — recorded '
             '<span id=skimtime>--:--</span></summary><p class=hint>Read-only. Scroll up in the exported '
             'JSON for the full record.</p><p class=hint id=knowecho></p></details>')

    # ---- full read
    H.append('<div id=full class=hidden>')
    H.append('<p class=hint>Keys: <kbd>1</kbd> sound &middot; <kbd>2</kbd> shaky &middot; <kbd>3</kbd> wrong '
             '&middot; <kbd>4</kbd> n/a &middot; <kbd>j</kbd>/<kbd>k</kbd> move &middot; <kbd>n</kbd> note.</p>')
    for u in graded:
        badge = '<span class=badge>%s %d–%d</span>' % (u.nb, u.start, u.end)
        H.append('<section class=unit id="u-%s"><h2>%s %s</h2>'
                 % (u.uid, html.escape(u.title), badge))
        H.append(render_unit_body(u))
        for a in u.inline:
            H.append('<div class=ana><div class=tag>analysis of this data — %s (ana %d–%d)</div>%s</div>'
                     % (html.escape(a.title), a.start, a.end, render_unit_body(a)))
        H.append(render_passa(u))
        H.append((WIDGET % {'uid': u.uid}) + '</section>')

    # ---- final debrief
    H.append('<section id=debrief><h2>Final debrief</h2>'
             '<p class=hint id=finalhint>Locked until every unit above has a ruling.</p>'
             '<fieldset id=finalfs disabled><legend>Debrief</legend>')
    H.append('<div class=q><label class=lead>1. Does this answer the brief?</label>%s</div>' % radio('final_disposition', DISP))
    H.append('<div class=q id=q_reanalysis><label class=lead>List the re-analysis.</label>'
             '<textarea rows=3 data-f=reanalysis oninput="finalIn(\'reanalysis\',this.value)"></textarea></div>')
    H.append('<div class=q id=q_remeasure><label class=lead>List what to re-measure.</label>'
             '<textarea rows=3 data-f=remeasure oninput="finalIn(\'remeasure\',this.value)"></textarea></div>')
    H.append('<div class=q><label class=lead>2. Supervision</label>%s</div>' % radio('final_supervision', SUP))
    H.append('<div class=q><label class=lead>3. Overall read on the session — why the disposition and '
             'supervision above: what made this run good or bad, including any wasted effort, if any.</label>'
             '<textarea rows=3 data-f=overall_read oninput="finalIn(\'overall_read\',this.value)" '
             'onchange="finalIn(\'overall_read\',this.value)"></textarea></div>')
    H.append('<div class=q><label class=lead>4. What additional sweep or effort would have been most '
             'valuable? Anything you would have done that this run omitted.</label>'
             '<textarea rows=3 data-f=omission oninput="finalIn(\'omission\',this.value)" '
             'onchange="finalIn(\'omission\',this.value)"></textarea></div>')
    H.append('<div class=q><label class=lead>5a. Single biggest thing this run got right.</label>'
             '<textarea rows=3 data-f=biggest_right oninput="finalIn(\'biggest_right\',this.value)" '
             'onchange="finalIn(\'biggest_right\',this.value)"></textarea></div>')
    H.append('<div class=q><label class=lead>5b. Single biggest thing this run got wrong.</label>'
             '<textarea rows=3 data-f=biggest_wrong oninput="finalIn(\'biggest_wrong\',this.value)" '
             'onchange="finalIn(\'biggest_wrong\',this.value)"></textarea></div>')
    H.append('<div class=q><label class=lead>6. Knowledge state, recorded before reading</label>'
             '<p class=hint id=knowecho2></p></div>')
    H.append('</fieldset><p><button type=button onclick="exportJSON()">Export JSON</button></p></section>')
    H.append('</div>')  # #full

    units_js = [{'uid': u.uid, 'nb': u.nb, 'range': [u.start, u.end], 'title': u.title,
                 'ids': sorted(u.ids), 'context': False, 'context_reason': u.context_reason,
                 'inline': [{'notebook': a.nb, 'cell_range': [a.start, a.end], 'title': a.title} for a in u.inline]}
                for u in graded]
    context_js = [{'uid': u.uid, 'nb': u.nb, 'range': [u.start, u.end], 'title': u.title,
                 'ids': sorted(u.ids), 'context': True, 'context_reason': u.context_reason,
                 'inline': [{'notebook': a.nb, 'cell_range': [a.start, a.end], 'title': a.title} for a in u.inline]}
                for u in context]
    H.append('<script>const UNITS = %s;\nconst CONTEXT = %s;</script>'
             % (json.dumps(units_js).replace('</', '<\\/'), json.dumps(context_js).replace('</', '<\\/')))
    H.append('<script>%s</script>' % JS.replace('__KEY__', key))
    H.append('</div></body></html>')

    outdir = HERE / 'passb'
    outdir.mkdir(exist_ok=True)
    out = outdir / ('%s.html' % key)
    out.write_text('\n'.join(H), encoding='utf-8')

    # card -> unit map, for the Pass A concordance analysis (unmatched -> null)
    cmap = {}
    for u in seq:
        for c in u.cards:
            cmap[c['id']] = u.uid
    for cid in unmatched:
        cmap[cid] = None
    (outdir / ('%s.map.json' % key)).write_text(
        json.dumps(dict(sorted(cmap.items())), indent=1), encoding='utf-8')

    inline_n = sum(len(u.inline) for u in m_units)
    with_cards = sum(1 for u in seq if u.cards)
    ctx_cards = [c['id'] for u in context for c in u.cards]
    print('units graded: %d, context (ungraded): %d' % (len(graded), len(context)))
    print('template index: %d normalized cells recurring in >=%d of %d sibling archives'
          % (len(tmpl), TEMPLATE_MIN_ARCHIVES, n_sibs))
    for u in context:
        print('  context  %-6s %-8s %s  [%s]' % (u.uid, '%s %d-%d' % (u.nb, u.start, u.end),
                                                 u.title[:46], u.context_reason))
    print('sequence: %d measure + %d standalone ana' % (len(m_units), len(standalone)))
    print('ana units: %d total, %d inline-attached, %d standalone' % (len(a_units), inline_n, len(standalone)))
    print('units with Pass A claims: %d' % with_cards)
    print('cards matched: %d of %d%s' % (len(cards) - len(unmatched), len(cards),
                                         ('  unmatched: ' + ', '.join(unmatched)) if unmatched else ''))
    print('cards landing in a context unit: %d%s'
          % (len(ctx_cards), ('  ' + ', '.join(ctx_cards)) if ctx_cards else ''))
    print('cards with enumerated items: %d (%d joined from the pooled card files)'
          % (sum(1 for c in cards if c.get('items')), enriched))
    print('final-call unit: %s' % (final_call.uid if final_call else 'none'))
    print('gallery figures: %d' % len(gallery))
    print('wrote %s (%.1f MB)' % (out, out.stat().st_size / 1e6))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
