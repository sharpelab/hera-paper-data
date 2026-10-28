"""Per-run grading synthesis page: Pass A cards nested inside Pass B units.

    render(M, T, key) -> complete HTML document

One column of Pass B units in notebook order; each unit carries the rater's ruling
and note, then the Pass A cards the map places inside it. Pass A and Pass B numbers
sit beside each other and are never combined; the unit tally is only ever shown
stratified. Rater is a dimension throughout: every rater loop runs over T['raters'].
Stdlib only, deterministic output.
"""
import hera_synth as H
from synth_common import (FINAL_FIELDS, ITEM_VERDICTS, RULINGS, RUNS, SKIM_FIELDS,
                          DISP, SUP, IDENTITY, arm_text, chip, e, fmt, letter,
                          note_block, page, rater_name, value_class)

CLAIM_MAX = 220

EXTRA_CSS = """
.inline{font-size:12px;color:#8a8578;margin-top:4px}
.inline .il{font:11.5px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#6f6b60}
.ctxwhy{color:#a5a094;font-style:italic}
"""


# ------------------------------------------------------------------ atoms --
def ruling_word(r):
    return 'n-a' if r == 'na' else (r or 'unruled')


def moved_text(delta):
    """Skim -> final letter movement as words."""
    if delta in ('', None):
        return '—'
    d = int(delta)
    if d == 0:
        return 'same'
    return ('harsher +%d' % d) if d > 0 else ('kinder −%d' % -d)


def prefixed(multi, rater, text):
    return ('%s %s' % (rater_name(rater), text)) if multi else text


def claim_html(claim):
    claim = claim or ''
    if len(claim) <= CLAIM_MAX:
        return '<div class="claim plain">%s</div>' % e(claim)
    return ('<details class="claim"><summary>%s…<span class="more"> show full claim</span>'
            '</summary><div class="claimfull">%s</div></details>'
            % (e(claim[:CLAIM_MAX].rstrip()), e(claim)))


# ----------------------------------------------------------------- header --
def metrics_block(row):
    h = ['<div class="metrics">']
    h.append('<div class="metric big"><div class="mv">%s</div><div class="ml">S_claim</div></div>'
             % e(fmt(row['S_claim'])))
    for col, lab, ncol in (('inference_acc', 'inference', 'inference_n'),
                           ('decision_acc', 'decision', 'decision_n'),
                           ('verdict_acc', 'verdict', 'verdict_n')):
        h.append('<div class="metric"><div class="mv">%s</div><div class="ml">%s acc '
                 '<span class="mn">n=%s</span></div></div>'
                 % (e(fmt(row[col])), e(lab), e(row[ncol])))
    h.append('<div class="metric"><div class="mv">%s</div><div class="ml">item acc</div></div>'
             % e(fmt(row['item_acc'])))
    h.append('<div class="metric"><div class="mv">%s / %s</div><div class="ml">cards scored / visible '
             '<span class="mn">%s unverifiable</span></div></div>'
             % (e(row['n_scored']), e(row['n_cards']), e(row['n_unverifiable'])))
    h.append('</div>')
    return ''.join(h)


def pb_table(row):
    h = ['<table class="pb"><tr><th></th><th>skim</th><th>final</th></tr>']
    for lab, sk, fi, table in (('disposition', 'skim_disposition', 'final_disposition', DISP),
                               ('supervision', 'skim_supervision', 'final_supervision', SUP)):
        h.append('<tr><td class="pbk">%s</td><td>%s</td><td>%s</td></tr>'
                 % (e(lab), e(letter(row[sk], table)), e(letter(row[fi], table))))
    h.append('<tr><td class="pbk">moved</td><td colspan="2">disposition %s &nbsp;·&nbsp; supervision %s</td></tr>'
             % (e(moved_text(row['disposition_delta'])), e(moved_text(row['supervision_delta']))))
    h.append('</table>')
    return ''.join(h)


def tally_lines(M, T, key, rater, row):
    t = H.tally(M, rater, key)
    h = []
    for stratum, lab in (('conclusion', 'conclusion-bearing units'), ('routine', 'routine units')):
        counts = t[stratum]
        parts = ['%d %s' % (counts[r], ruling_word(r)) for r in RULINGS]
        if counts['unruled']:
            parts.append('%d unruled' % counts['unruled'])
        h.append('<div class="tally">%s: <b>%d</b> — %s</div>'
                 % (e(lab), sum(counts.values()), e(' · '.join(parts))))
    h.append('<div class="tally">context (ungraded): <b>%s</b></div>' % e(row['n_context']))

    if row['prop_n_v1'] != '':
        prop = next((p for p in T['propagation']
                     if p['run'] == key and p['rater_a'] == rater and p['rater_b'] == rater), None)
        h.append('<div class="tally">Pass A value 1.0 cards sitting in a shaky/wrong unit: '
                 '<b>%s of %s</b> (%s) · Pass A value &lt; 0.5 cards sitting in a sound unit: '
                 '<b>%s of %s</b> (%s) · eligible %s of %s</div>'
                 % (e(row['prop_n_v1_down']), e(row['prop_n_v1']), e(row['prop_down_rate'] or '—'),
                    e(row['prop_n_vlt05_up']), e(row['prop_n_vlt05']), e(row['prop_up_rate'] or '—'),
                    e(row['prop_eligible']), e(prop['n_cards'] if prop else '—')))
    if row.get('active_min'):
        h.append('<div class="tally">active scorer time <b>%s min</b> (skim %s · grading %s · debrief %s)'
                 ' · %s &gt; 30 min</div>'
                 % (e(fmt(row['active_min'], 1)), e(fmt(row['skim_min'], 1)),
                    e(fmt(row['grading_min'], 1)), e(fmt(row['debrief_min'], 1)),
                    e('%s break%s' % (row['n_breaks'], '' if row['n_breaks'] == 1 else 's'))))
    return ''.join(h)


def debrief_block(row, rater):
    h = []
    for field, lab in SKIM_FIELDS + FINAL_FIELDS:
        text = (row.get(field) or '').strip()
        if not text:
            continue
        if field == 'know_text':
            lab = '%s — knew the adjudicated answer: %s' % (lab, row.get('know_adjudicated') or '—')
        h.append('<div class="dfield"><div class="dlab">%s</div>%s</div>'
                 % (e(lab), note_block(text, rater, 'note-debrief')))
    return '<div class="debrief">%s</div>' % ''.join(h) if h else ''


def header_block(M, T, key, rater, row):
    passes = (['Pass A (blind, per-claim)'] if row['passa'] else []) + \
             (['Pass B (whole-session debrief)'] if row['passb'] else [])
    h = ['<div class="hcol"><div class="hlabel">%s</div><div class="hsub">%s</div>'
         % (e(rater_name(rater)), e(' · '.join(passes)))]
    if row['passa']:
        h.append(metrics_block(row))
    if row['passb']:
        h.append(pb_table(row))
        h.append(tally_lines(M, T, key, rater, row))
        h.append(debrief_block(row, rater))
    h.append('</div>')
    return ''.join(h)


def legend_block():
    h = ['<div class="legend"><b>Pass B ruling:</b>']
    for r in RULINGS + ['unruled']:
        h.append(chip('r', ruling_word(r), cls='r-%s' % r))
    h.append('<b>Pass A card value:</b>')
    for txt, cls in (('1.0', 'v-good'), ('0.7', 'v-ok'), ('0.5', 'v-mid'),
                     ('0.0', 'v-bad'), ('unverifiable', 'v-na')):
        h.append(chip('v', txt, cls=cls))
    h.append('<b>divergence:</b>')
    h.append(chip('x', '1.0 in a shaky/wrong unit', cls='x-down'))
    h.append(chip('x', 'value < 0.5 in a sound unit', cls='x-up'))
    h.append('<b>purple left bar:</b> the unit holds at least one Pass A inference or verdict card '
             '(conclusion-bearing); claims are truncated at %d chars — click to expand.</div>' % CLAIM_MAX)
    return ''.join(h)


# ------------------------------------------------------------------ cards --
def items_block(row):
    if not row['n_items']:
        return ''
    counts = {'correct': row['n_correct'], 'partial': row['n_partial'],
              'wrong': row['n_wrong'], 'unverifiable': row['n_unverifiable']}
    parts = ['%d %s' % (counts[v], v) for v in ITEM_VERDICTS if counts[v]]
    h = ['<div class="items">%s: %s'
         % (e('%d item%s' % (row['n_items'], '' if row['n_items'] == 1 else 's')), e(', '.join(parts)))]
    flagged = [i for i in row['items'] if i['verdict'] in ('partial', 'wrong', 'unverifiable')]
    if flagged:
        h.append('<ul class="flag">')
        for i in flagged:
            h.append('<li>%s<span>%s</span></li>' % (chip('iv', i['verdict']), e(i['text'])))
        h.append('</ul>')
    h.append('</div>')
    return ''.join(h)


def divergence_chips(conc, card, rater_a, pb_raters, row, multi):
    """One chip per (Pass A rater, Pass B rater) pair whose concordance cell diverges."""
    h = []
    for rb in pb_raters:
        c = conc.get((card, rater_a, rb))
        if not c or c['divergence'] not in ('down', 'up'):
            continue
        if c['divergence'] == 'down':
            text, cls = '1.0 in a %s unit' % ruling_word(c['unit_ruling']), 'x-down'
        else:
            text, cls = '%s in a sound unit' % row['value'], 'x-up'
        title = '%s Pass A value %s · %s Pass B ruling %s' % (
            rater_name(rater_a), row['value'], rater_name(rb), ruling_word(c['unit_ruling']))
        h.append(chip('x', prefixed(multi, rb, text), cls=cls, title=title))
    return ''.join(h)


def card_block(M, conc, card, rater_a, pb_raters, multi):
    row = H.card_row(M, rater_a, card)
    cm = M['cardmeta'][card]
    h = ['<div class="card"><div class="chead">']
    h.append(chip('t', cm['type']))
    vtext = row['value'] or 'unverifiable'
    h.append(chip('v', prefixed(multi, rater_a, vtext), cls=value_class(row['value'], row['verdict']),
                  title='%s Pass A' % rater_name(rater_a)))
    h.append('<span class="cid">%s · %s</span>' % (e(row['orig_id']), e(card)))
    if cm['anchor']:
        h.append('<span class="anchor">%s</span>' % e(cm['anchor']))
    h.append(divergence_chips(conc, card, rater_a, pb_raters, row, multi))
    h.append('</div>')
    h.append(claim_html(cm['claim']))
    h.append(note_block(row['note'], rater_a, 'note-card'))
    h.append(items_block(row))
    h.append('</div>')
    return ''.join(h)


def hidden_block(M, cards):
    """The instrument/tooling decision cards, never scored: collapsed, no value, no note."""
    if not cards:
        return ''
    types = sorted({M['cardmeta'][c]['type'] for c in cards})
    word = '%s ' % types[0] if len(types) == 1 else ''
    h = ['<details class="hid"><summary>+%d hidden %scard%s — instrument/tooling, never scored</summary>'
         % (len(cards), e(word), '' if len(cards) == 1 else 's')]
    for c in cards:
        cm = M['cardmeta'][c]
        h.append('<div class="card hidden-card"><div class="chead">')
        h.append(chip('t', cm['type']))
        h.append(chip('x', 'hidden', cls='x-hidden'))
        h.append('<span class="cid">%s · %s</span>' % (e(cm['orig_id']), e(c)))
        if cm['anchor']:
            h.append('<span class="anchor">%s</span>' % e(cm['anchor']))
        h.append('</div>')
        h.append(claim_html(cm['claim']))
        h.append('</div>')
    h.append('</details>')
    return ''.join(h)


def scorers_of(M, pa_raters, card):
    """The Pass A raters that actually hold a row for this card (a subset rater scores
    only some); falls back to the first so the card is never dropped."""
    scored = [r for r in pa_raters if card in M['passa'][r]['cards']]
    return scored or pa_raters[:1]


def cards_block(M, conc, cards, pa_raters, pb_raters, multi, st):
    """Visible cards (one block per Pass A rater), then the hidden ones."""
    if not pa_raters:
        return ''
    visible = [c for c in cards if not any(H.card_row(M, r, c)['hidden'] for r in pa_raters)]
    hidden = [c for c in cards if c not in visible]
    st['visible'] += len(visible)
    st['hidden'] += len(hidden)
    if not (visible or hidden):
        return ''
    h = ['<div class="cards">']
    for c in visible:
        for ra in scorers_of(M, pa_raters, c):
            h.append(card_block(M, conc, c, ra, pb_raters, multi))
    h.append(hidden_block(M, hidden))
    h.append('</div>')
    return ''.join(h)


# ------------------------------------------------------------------ units --
def context_unit(u):
    return ('<div class="unit ctx" id="u-%s">%s<span class="urange">%s %s–%s</span>'
            '<span class="utitle">%s</span><span class="ctxwhy">%s</span></div>'
            % (e(u['unit_id']), chip('r', 'context', cls='r-context'), e(u['notebook']),
               e(u['cell_start']), e(u['cell_end']), e(u['title']), e(u['context_reason'])))


def graded_unit(M, key, u, rulings, notes, cards_html, multi):
    cb = (key, u['unit_id']) in M['conclusion_units']
    h = ['<div class="unit%s" id="u-%s"><div class="uhead">' % (' cb' if cb else '', e(u['unit_id']))]
    for rater, ruling in rulings:
        h.append(chip('r', prefixed(multi, rater, ruling_word(ruling)),
                      cls='r-%s' % (ruling or 'unruled'),
                      title='%s: %s' % (rater_name(rater), ruling_word(ruling))))
    h.append(chip('x', 'conclusion-bearing') if cb else chip('x', 'routine', cls='x-routine'))
    h.append('<span class="urange">%s %s–%s</span><span class="uid">%s</span></div>'
             % (e(u['notebook']), e(u['cell_start']), e(u['cell_end']), e(u['unit_id'])))
    h.append('<div class="utitle">%s</div>' % e(u['title']))
    for sp in u['inline']:
        h.append('<div class="inline">inline <span class="il">%s %s–%s</span>: %s</div>'
                 % (e(sp['notebook']), e(sp['cell_range'][0]), e(sp['cell_range'][1]), e(sp['title'])))
    h.append(''.join(notes) if notes else '<div class="nonote">no Pass B note</div>')
    h.append(cards_html or '<div class="nonote">no Pass A cards mapped to this unit</div>')
    h.append('</div>')
    return ''.join(h)


def body_units(M, key, pa_raters, pb_raters, conc, multi, st):
    """Units in the primary Pass B rater's display order, each with every rater's ruling."""
    primary = pb_raters[0]
    by_rater = {r: {u['unit_id']: u for u in H.unit_rows(M, r, key)} for r in pb_raters}
    h = []
    for u in H.unit_rows(M, primary, key):
        uid = u['unit_id']
        if u['context']:
            st['context'] += 1
            h.append(context_unit(u))
            continue
        st['graded'] += 1
        rulings, notes = [], []
        for r in pb_raters:
            ur = by_rater[r].get(uid)
            if ur is None:
                continue
            rulings.append((r, ur['ruling']))
            nb = note_block(ur['note'], r)
            if nb:
                notes.append(nb)
        cards = H.cards_in_unit(M, key, uid)
        h.append(graded_unit(M, key, u, rulings, notes,
                             cards_block(M, conc, cards, pa_raters, pb_raters, multi, st), multi))
    return ''.join(h)


def unmapped_block(M, key, pa_raters, pb_raters, conc, multi, st):
    cards = H.unmapped_cards(M, key)
    if not cards:
        return ''
    inner = cards_block(M, conc, cards, pa_raters, pb_raters, multi, st)
    st['unmapped'] += len(cards)
    return ('<div class="unit unmapped"><div class="utitle">Pass A cards with no unit</div>'
            '<div class="inline">the map leaves these outside every notebook unit '
            '(anchors point outside the notebooks, e.g. into the transcript)</div>%s</div>' % inner)


# ------------------------------------------------------------------- page --
def footer_block(st):
    return ('<div class="tally">units: <b>%d</b> (%d graded + %d context) · Pass A cards: <b>%d</b> mapped '
            '(%d visible + %d hidden) + %d unmapped</div>'
            % (st['graded'] + st['context'], st['graded'], st['context'],
               st['visible'] + st['hidden'] - st['unmapped'],
               st['visible'] - st['unmapped_visible'], st['hidden'] - st['unmapped_hidden'],
               st['unmapped']))


def lede(key, raters):
    ident = IDENTITY[key]
    bits = [arm_text(key)]
    if ident['call']:
        correct = {'yes': 'correct', 'no': 'not correct'}.get(ident['call_correct'], 'correctness not recorded')
        bits.append('call: %s — %s' % (ident['call'], correct))
    else:
        bits.append('no stacking call recorded')
    if ident['note']:
        bits.append(ident['note'])
    who = ' and '.join(rater_name(r) for r in raters)
    words = ('%s’s own words' % who) if len(raters) == 1 else ('the raters’ own words, each labelled')
    return ('<p class="lede">%s. %s are the italic tinted blocks; everything else on this page is '
            'generated scaffolding. Pass A (blind, per-claim) and Pass B (whole-session debrief) numbers '
            'sit beside each other and are never combined; the unit tally is stratified into '
            'conclusion-bearing and routine units.</p>' % (e(' · '.join(bits)), e(words)))


def crumbs(key):
    h = ['<div class="crumbs"><a href="index.html">overview</a>']
    for k in RUNS:
        h.append('<b>%s</b>' % e(k) if k == key else '<a href="%s.html">%s</a>' % (e(k), e(k)))
    h.append('</div>')
    return ' '.join(h)


def render(M, T, key):
    rows = {r['rater']: r for r in T['runs'] if r['run'] == key}
    raters = [r for r in T['raters'] if r in rows]
    pa_raters = [r for r in T['raters']
                 if r in M['passa'] and (rows.get(r, {}).get('passa')
                                         or any(c in M['passa'][r]['cards']
                                                for c in M['cardmeta'] if M['cardmeta'][c]['run'] == key))]
    pb_raters = [r for r in raters if rows[r]['passb']]
    multi = len(T['raters']) > 1
    conc = {(c['card'], c['rater_a'], c['rater_b']): c for c in T['concordance'] if c['run'] == key}
    st = dict(graded=0, context=0, visible=0, hidden=0, unmapped=0,
              unmapped_visible=0, unmapped_hidden=0)

    body = ['<div class="wrap">', crumbs(key),
            '<h1>%s · %s</h1>' % (e(key), e(IDENTITY[key]['label'])), lede(key, raters)]
    for r in raters:
        body.append(header_block(M, T, key, r, rows[r]))
    body.append(legend_block())
    if pb_raters:
        body.append(body_units(M, key, pa_raters, pb_raters, conc, multi, st))
    before = (st['visible'], st['hidden'])
    tail = unmapped_block(M, key, pa_raters, pb_raters, conc, multi, st)
    st['unmapped_visible'] = st['visible'] - before[0]
    st['unmapped_hidden'] = st['hidden'] - before[1]
    body.append(tail)
    body.append(footer_block(st))
    body.append('</div>')
    title = 'HERA %s — %s — grading synthesis' % (key, IDENTITY[key]['label'])
    return page(title, ''.join(body), EXTRA_CSS)
