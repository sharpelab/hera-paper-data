#!/usr/bin/env python3
"""Overview page (index.html) for the HERA grading synthesis.

    render(M, T) -> one self-contained HTML document

Five sections: the headline table (one row per run x rater), the unit-sequence
strips, the debrief grid, the theme queries over the notes corpus, and the
artifact inventory. Pass A and Pass B quantities sit beside each other and are
never combined; unit tallies appear only stratified; the rater's own words are
rendered only through note_block(). Rater is a dimension throughout: every loop
runs over T['raters'] / M['passa'] / M['passb']. Stdlib only, deterministic.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import hera_synth as HS                                                      # noqa: E402
from synth_common import (RUNS, IDENTITY, DISP, SUP, RULINGS, SKIM_FIELDS,   # noqa: E402
                          FINAL_FIELDS, THEMES, e, fmt, note_block, letter,
                          arm_text, page, rater_name)

FIELD_LABEL = dict(SKIM_FIELDS + FINAL_FIELDS)
DEBRIEF_ORDER = ['skim_impression', 'overall_read', 'reanalysis', 'remeasure',
                 'omission', 'biggest_right', 'biggest_wrong', 'know_text']
LEVEL_ORDER = {'run': 0, 'unit': 1, 'card': 2}

# note_block() escapes the rater's words, so <mark> markup cannot be handed to
# it. Theme hits wrap their regex matches in these two private-use sentinels
# first and swap them for tags after escaping — the words still go through
# note_block(), and nothing is escaped twice.
MK_OPEN, MK_CLOSE = '\ue000', '\ue001'

EXTRA_CSS = """
.ok{color:#2f7a2c;font-weight:700}
.no{color:#a3261c;font-weight:700}
table.grid tr.grp th{background:#f1efe9;color:#6f6b60;border-bottom:1px solid #e2dfd6;padding:5px 8px}
table.grid td.mono{font:11.5px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.dcol .dh{font-size:12px;color:#8a8578;border-bottom:1px solid #eae7df;padding-bottom:6px;margin-bottom:8px}
.dcol .dh b{display:block;font-size:13.5px;color:#1c1c1a;letter-spacing:-.01em}
.theme .cnt{color:#8a8578;font-size:11.5px;margin-left:8px}
.legend .rchip.cb{box-shadow:0 0 0 2px #6b5ea8 inset}
"""


# ------------------------------------------------------------------ shared --
def _pb_raters(M, T, key):
    """Raters with a Pass B export for this run, in T['raters'] order."""
    return [r for r in T['raters'] if key in M['passb'].get(r, {})]


def _run_row(T, key, rater):
    return next((r for r in T['runs'] if r['run'] == key and r['rater'] == rater), None)


def _delta_text(d):
    if d == '' or d is None:
        return '—'
    d = int(d)
    if d == 0:
        return 'same'
    return ('harsher +%d' % d) if d > 0 else ('kinder −%d' % -d)


def _rate(n, d, rate):
    """'8/15 (.533)' — counts first, the pre-declared rate in parentheses."""
    if d in ('', None) or int(d) == 0:
        return '%s/%s' % (e(n), e(d))
    return '%s/%s <span class="sub">(%s)</span>' % (e(n), e(d), e(str(rate).lstrip('0') or rate))


# --------------------------------------------------------- 1 · headline ----
def _headline(M, T):
    h = ['<h2>1 &middot; Headline &mdash; one row per run &times; rater</h2>',
         '<div class="scroll"><table class="grid">',
         '<tr class="grp"><th colspan="3">identity</th><th>rater</th>'
         '<th colspan="5">Pass A &mdash; per-claim, blind</th>'
         '<th colspan="6">Pass B &mdash; whole-session debrief</th>'
         '<th colspan="2">A &times; B propagation</th><th>effort</th></tr>',
         '<tr><th>run</th><th>arm</th><th>call</th><th></th>'
         '<th>S_claim</th><th>inference acc</th><th>decision acc</th><th>verdict acc</th><th>item acc</th>'
         '<th>skim d/s</th><th>final d/s</th><th>re-analysis?</th><th>re-measure?</th>'
         '<th>CB sound &middot; shaky &middot; wrong &middot; n-a</th>'
         '<th>routine sound &middot; shaky &middot; wrong &middot; n-a</th>'
         '<th>A=1.0 &rarr; shaky/wrong</th><th>A&lt;0.5 &rarr; sound</th><th>active min</th></tr>']
    for d in T['runs']:
        ident = IDENTITY[d['run']]
        mark = {'yes': '<span class="ok">✓</span>', 'no': '<span class="no">✗</span>'}
        call = ' '.join(x for x in [e(d['call']) or '—', mark.get(d['call_correct'], '')] if x)
        h.append('<tr>')
        h.append('<td class="key"><a href="%s.html">%s</a><span class="sub">%s</span></td>'
                 % (e(d['run']), e(d['run']), e(d['label'])))
        h.append('<td>%s</td>' % e(arm_text(d['run'])))
        h.append('<td>%s%s</td>' % (call, ('<span class="sub">%s</span>' % e(ident['note'])) if ident['note'] else ''))
        h.append('<td>%s</td>' % e(rater_name(d['rater'])))
        if d['passa']:
            h.append('<td class="num"><b>%s</b></td>' % e(fmt(d['S_claim'])))
            for acc, n in (('inference_acc', 'inference_n'), ('decision_acc', 'decision_n'),
                           ('verdict_acc', 'verdict_n')):
                h.append('<td class="num">%s<span class="sub">n=%s</span></td>' % (e(fmt(d[acc])), e(d[n])))
            h.append('<td class="num">%s<span class="sub">%s/%s scored</span></td>'
                     % (e(fmt(d['item_acc'])), e(d['n_scored']), e(d['n_cards'])))
        else:
            h.append('<td></td>' * 5)
        if d['passb']:
            sk = 'disposition: %s\nsupervision: %s' % (letter(d['skim_disposition'], DISP),
                                                       letter(d['skim_supervision'], SUP))
            fi = 'disposition: %s\nsupervision: %s' % (letter(d['final_disposition'], DISP),
                                                       letter(d['final_supervision'], SUP))
            h.append('<td class="mono" title="%s">%s/%s</td>'
                     % (e(sk), e(d['skim_disposition'] or '—'), e(d['skim_supervision'] or '—')))
            h.append('<td class="mono" title="%s">%s/%s<span class="sub">disp %s &middot; sup %s</span></td>'
                     % (e(fi), e(d['final_disposition'] or '—'), e(d['final_supervision'] or '—'),
                        e(_delta_text(d['disposition_delta'])), e(_delta_text(d['supervision_delta']))))
            h.append('<td>%s</td><td>%s</td>' % ('y' if d['reanalysis_filled'] else 'n',
                                                 'y' if d['remeasure_filled'] else 'n'))
            for pre in ('cb', 'ro'):
                h.append('<td class="num">%s<span class="sub">of %s</span></td>'
                         % (' &middot; '.join(e(d['%s_%s' % (pre, r)]) for r in RULINGS), e(d['%s_units' % pre])))
        else:
            h.append('<td></td>' * 6)
        if d['prop_n_v1'] != '':
            h.append('<td class="num">%s</td>' % _rate(d['prop_n_v1_down'], d['prop_n_v1'], d['prop_down_rate']))
            h.append('<td class="num">%s</td>' % _rate(d['prop_n_vlt05_up'], d['prop_n_vlt05'], d['prop_up_rate']))
        else:
            h.append('<td></td><td></td>')
        h.append('<td class="num">%s</td></tr>' % (e(fmt(d['active_min'], 1)) if d['passb'] else ''))
    h.append('</table></div>')
    h.append(_decode(T))
    return ''.join(h)


def _decode(T):
    """Both letter tables in full, then the pooled propagation row per rater pair."""
    h = ['<div class="tally"><b>disposition</b> &mdash; %s</div>'
         % ' &middot; '.join('%s' % e(letter(k, DISP)) for k in sorted(DISP)),
         '<div class="tally"><b>supervision</b> &mdash; %s</div>'
         % ' &middot; '.join('%s' % e(letter(k, SUP)) for k in sorted(SUP))]
    pooled = [p for p in T['propagation'] if p['run'] == 'ALL']
    for p in pooled:
        pair = ('%s × %s: ' % (rater_name(p['rater_a']), rater_name(p['rater_b']))) if len(pooled) > 1 else ''
        h.append('<div class="tally">%s<b>pooled:</b> %s of %s value-1.0 cards sit in shaky/wrong units (%s); '
                 '%s of %s value&lt;0.5 cards sit in sound units (%s); eligible %s of %s</div>'
                 % (e(pair), e(p['n_v1_down']), e(p['n_v1']), e(p['down_rate'] or '—'),
                    e(p['n_vlt05_up']), e(p['n_vlt05']), e(p['up_rate'] or '—'),
                    e(p['eligible']), e(p['n_cards'])))
    return ''.join(h)


# ---------------------------------------------------- 2 · unit sequence ----
def _strips(M, T):
    h = ['<h2>2 &middot; Unit sequence &mdash; every notebook unit in reading order</h2>']
    for key in RUNS:
        for r in _pb_raters(M, T, key):
            h.append('<div class="striprow"><div class="k"><b>%s</b><span>%s<br>%s</span></div><div class="strip">'
                     % (e(key), e(IDENTITY[key]['label']), e(rater_name(r))))
            for u in HS.unit_rows(M, r, key):
                if u['context']:
                    h.append('<span class="rchip r-context ctx" title="%s">&middot;</span>'
                             % e('%s · %s — context: %s' % (u['unit_id'], u['title'], u['context_reason'])))
                    continue
                ruling = u['ruling'] or 'unruled'
                tip = '%s · %s' % (u['unit_id'], u['title'])
                if u['note'].strip():
                    tip += '\n\n' + u['note'].strip()
                h.append('<a class="rchip r-%s%s" href="%s.html#u-%s" title="%s">%s</a>'
                         % (e(ruling), ' cb' if u['stratum'] == 'conclusion' else '', e(key),
                            e(u['unit_id']), e(tip), e('n-a' if ruling == 'na' else ruling)))
            h.append('</div></div>')
    h.append('<div class="legend"><b>ruling:</b> <span class="rchip r-sound">sound</span>'
             '<span class="rchip r-shaky">shaky</span><span class="rchip r-wrong">wrong</span>'
             '<span class="rchip r-na">n-a</span><span class="rchip r-unruled">unruled</span>'
             '&nbsp;<span class="rchip r-sound cb">sound</span> '
             'heavy inset border = conclusion-bearing (the unit holds ≥1 Pass A inference or verdict card)'
             '&nbsp;<span class="rchip r-context ctx">&middot;</span> context unit, ungraded by design. '
             'Hover any chip for its title and the rater’s note; click to jump to it on the run page.</div>')
    return ''.join(h)


# ----------------------------------------------------------- 3 · debrief ----
def _debrief(M, T):
    h = ['<h2>3 &middot; Debrief &mdash; the rater’s own words, one column per run &times; rater</h2>', '<div class="dgrid">']
    for key in RUNS:
        for r in _pb_raters(M, T, key):
            d = _run_row(T, key, r)
            h.append('<div class="dcol"><div class="dh"><b>%s</b>%s<br>final %s/%s &middot; %s</div>'
                     % (e(key), e(IDENTITY[key]['label']),
                        e(d.get('final_disposition') or '—'), e(d.get('final_supervision') or '—'),
                        e(rater_name(r))))
            for f in DEBRIEF_ORDER:
                txt = d.get(f, '')
                if not (txt or '').strip():
                    continue
                lab = FIELD_LABEL.get(f, f)
                if f == 'know_text':
                    lab += ' — knew the adjudicated answer: %s' % (d.get('know_adjudicated') or '—')
                h.append('<div class="dfield"><div class="dlab">%s</div>%s</div>'
                         % (e(lab), note_block(txt, r, 'note-debrief')))
            h.append('</div>')
    h.append('</div>')
    return ''.join(h)


# ------------------------------------------------------------ 4 · themes ----
def _mark(text, pat):
    """Sentinel-wrap every match; note_block() escapes, then the sentinels become <mark>."""
    text = text.replace(MK_OPEN, '').replace(MK_CLOSE, '')
    out, pos = [], 0
    for m in pat.finditer(text):
        if m.start() < pos or m.end() == m.start():
            continue
        out.append(text[pos:m.start()])
        out.append(MK_OPEN + m.group(0) + MK_CLOSE)
        pos = m.end()
    out.append(text[pos:])
    return ''.join(out)


def _prov(n):
    href = ('%s.html#u-%s' % (n['run'], n['unit_id'])) if n['unit_id'] else ('%s.html' % n['run'])
    bits = ['<a href="%s">%s</a>' % (e(href), e(n['run'])), e(rater_name(n['rater']))]
    if n['pass'] == 'A':
        bits.append(e('Pass A card %s (%s, value %s)'
                      % (n['orig_id'], n['type'], n['value'] if n['value'] != '' else 'unverifiable')))
    elif n['level'] == 'unit':
        bits.append(e('Pass B unit %s (%s)' % (n['unit_id'], n['ruling'] or 'unruled')))
    else:
        bits.append(e('Pass B %s' % FIELD_LABEL.get(n['field'], n['field'])))
    return '<div class="prov">%s</div>' % ' &middot; '.join(bits)


def _themes(T):
    h = ['<h2>4 &middot; Themes &mdash; regex queries over the notes corpus</h2>',
         '<p class="lede">Each theme is a regular expression over the notes corpus '
         '(<code>notes.jsonl</code>); matches are listed, not interpreted. Edit <code>THEMES</code> in '
         '<code>synth_common.py</code> to add one.</p>']
    for slug, label, rx in THEMES:
        pat = re.compile(rx, re.I)
        hits = sorted(T['themes'].get(slug, []),
                      key=lambda n: (n['run'], n['pass'], LEVEL_ORDER[n['level']], n['ref']))
        h.append('<div class="theme" id="theme-%s"><h3>%s</h3>'
                 '<span class="rx">%s</span><span class="cnt">%d hit%s</span>'
                 % (e(slug), e(label), e(rx), len(hits), '' if len(hits) == 1 else 's'))
        for n in hits:
            block = note_block(_mark(n['text'], pat), n['rater'])
            block = block.replace(MK_OPEN, '<mark>').replace(MK_CLOSE, '</mark>')
            h.append('<div class="hit">%s%s</div>' % (_prov(n), block))
        h.append('</div>')
    return ''.join(h)


# --------------------------------------------------------- 5 · artifacts ----
ARTIFACTS = [
    ('runs.csv', 'runs', 'one row per run × rater: identity, Pass A metrics, Pass B letters and deltas, '
                         'stratified tally, propagation, effort minutes, every debrief field'),
    ('units.csv', 'units', 'one row per Pass B unit × rater; context units included, ruling blank'),
    ('cards.csv', 'cards', 'one row per pooled Pass A card × rater; hidden cards included, value blank'),
    ('concordance.csv', 'concordance', 'one row per card × Pass A rater × Pass B rater: '
                                       'the card value beside its unit’s ruling, with the divergence cell'),
    ('propagation.csv', 'propagation', 'pre-declared analysis #3 per run × rater pair, plus the pooled ALL row'),
    ('notes.jsonl', 'notes', 'every free-text field any rater wrote, with provenance — the corpus section 4 queries'),
]


def _artifacts(T):
    h = ['<h2>5 &middot; Artifacts</h2>', '<table class="grid"><tr><th>file</th><th>rows</th><th>contents</th></tr>']
    for fn, tkey, desc in ARTIFACTS:
        h.append('<tr><td class="key"><a href="%s">%s</a></td><td class="num">%d</td><td>%s</td></tr>'
                 % (e(fn), e(fn), len(T[tkey]), e(desc)))
    h.append('</table>')
    h.append('<div class="tally">Regenerate every table and both page types with '
             '<code>python3 dossiers/hera_synth.py</code>. Output is deterministic: no timestamps, '
             'no git state, stable sort orders.</div>')
    return ''.join(h)


# ------------------------------------------------------------------ page ----
def _head(M, T):
    raters = ', '.join(rater_name(r) for r in T['raters'])
    return ('<h1>HERA tier-1 grading synthesis</h1>'
            '<p class="lede">Pass A scored every extracted claim blind, one card at a time '
            '(card value = the mean of its items; S_claim per run); Pass B was a whole-session collaborator '
            'debrief — skim, then a ruling on every notebook unit, then a final debrief. '
            'Numbers from the two passes sit beside each other and are never combined or averaged. '
            'Unit tallies are shown only stratified: a unit is conclusion-bearing when it holds at least one '
            'Pass A inference or verdict card, routine otherwise. '
            'The rater’s own words are set <i>italic on a tinted, left-bordered block</i> — everything '
            'else on this page is generated scaffolding. Rater%s: %s.</p>'
            % ('s' if len(T['raters']) > 1 else '', e(raters)))


def render(M, T):
    body = ['<div class="wrap wide">', _head(M, T), _headline(M, T), _strips(M, T),
            _debrief(M, T), _themes(T), _artifacts(T), '</div>']
    return page('HERA tier-1 grading synthesis', ''.join(body), EXTRA_CSS)
