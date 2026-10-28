#!/usr/bin/env python3
"""Grading synthesis: Pass A (per-claim, blind) beside Pass B (whole-session debrief).

    python3 dossiers/hera_synth.py            # -> dossiers/*.csv, notes.jsonl, index.html, <KEY>.html

Reads the repo read-only (blind-map.yaml, cards/, scores/, passb/), builds one
in-memory model with rater as a dimension, and writes:

  runs.csv          one row per run x rater; Pass A columns blank when that rater did
                    not score Pass A, Pass B columns blank when they did not do Pass B
  units.csv         one row per Pass B unit x rater (context units included, ruling blank)
  cards.csv         one row per pooled Pass A card x rater (hidden cards included, value blank)
  concordance.csv   one row per card x Pass A rater x Pass B rater: value beside unit ruling
  propagation.csv   pre-declared analysis #3 per run x rater pair, plus a pooled row
  notes.jsonl       every free-text field any rater wrote, with provenance (grep corpus)
  index.html        overview across the six runs
  <KEY>.html        per-run synthesis page

Rater discovery is by filename. Pass B: passb/<KEY>.passb.json is Aaron,
passb/<KEY>.<rater>.passb.json is <rater>. Pass A: scores/T1.cards.csv (+ T1.items.csv,
T1.runs.csv) is Aaron, scores/T1.<rater>.cards.csv (+ .items/.runs) is <rater>.
Output is deterministic: no timestamps or git state are baked in. Stdlib only.
"""
import csv
import datetime as dt
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from synth_common import (RUNS, IDENTITY, DISP, SUP, SEVERITY, RULINGS, CARD_TYPES,   # noqa: E402
                          ITEM_VERDICTS, DEFAULT_RATER, SKIM_FIELDS, FINAL_FIELDS,
                          THEMES, anchor_of)

BREAK_GAP_S = 30 * 60      # analysis #4: gaps longer than this are breaks, not effort


# ----------------------------------------------------------------- loading --
def read_csv(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_blind_map():
    """pooled id -> (run key, original claim id), from the sealed pool_T1 block."""
    bm = {}
    text = (ROOT / 'blind-map.yaml').read_text(encoding='utf-8')
    block = text.split('pool_T1:', 1)[1]
    for m in re.finditer(r'^\s+(T1-\d+):\s*\{key:\s*(\w+),\s*id:\s*([\w-]+)\}', block, re.M):
        bm[m.group(1)] = (m.group(2), m.group(3))
    return bm


def discover_passa():
    """rater -> dict(cards=path, items=path, runs=path)."""
    out = {}
    for p in sorted((ROOT / 'scores').glob('T1*.cards.csv')):
        m = re.fullmatch(r'T1(?:\.([a-z0-9]+))?\.cards\.csv', p.name)
        if not m:
            continue
        r = m.group(1) or DEFAULT_RATER
        suf = ('.%s' % m.group(1)) if m.group(1) else ''
        out[r] = dict(cards=p, items=ROOT / 'scores' / ('T1%s.items.csv' % suf),
                      runs=ROOT / 'scores' / ('T1%s.runs.csv' % suf))
    return out


def discover_passb():
    """rater -> {run key -> export path}. Only tier-1 keys; CAL* is shakedown data."""
    out = {}
    for p in sorted((ROOT / 'passb').glob('*.passb.json')):
        m = re.fullmatch(r'(T1[A-F])(?:\.([a-z0-9]+))?\.passb\.json', p.name)
        if not m:
            continue
        out.setdefault(m.group(2) or DEFAULT_RATER, {})[m.group(1)] = p
    return out


def ts(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


def effort(events):
    """Analysis #4 phase timings from the events stream. Minutes; None when a phase
    boundary is missing (partial export)."""
    if not events:
        return {}
    times = [ts(ev['ts']) for ev in events]
    begin = next((ts(ev['ts']) for ev in events if ev['kind'] == 'begin_full_read'), None)
    unlock = next((ts(ev['ts']) for ev in events if ev['kind'] == 'final_unlocked'), None)
    first, last = times[0], times[-1]

    def seg(t0, t1):
        pts = sorted(set([t0] + [t for t in times if t0 <= t <= t1] + [t1]))
        active, breaks = 0.0, []
        for a, b in zip(pts, pts[1:]):
            d = (b - a).total_seconds()
            if d <= BREAK_GAP_S:
                active += d
            else:
                breaks.append(d)
        return active, breaks

    out = dict(wall_h=(last - first).total_seconds() / 3600, n_events=len(events))
    if begin and unlock:
        skim, b1 = seg(first, begin)
        grade, b2 = seg(begin, unlock)
        deb, b3 = seg(unlock, last)
        out.update(skim_min=skim / 60, grading_min=grade / 60, debrief_min=deb / 60,
                   active_min=(skim + grade + deb) / 60,
                   n_breaks=len(b1) + len(b2) + len(b3),
                   break_h=sum(b1 + b2 + b3) / 3600)
    return out


def load():
    M = {'runs': {}, 'passa': {}, 'passb': {}, 'cardmeta': {}, 'unit_of': {}, 'maps': {}}
    bm = load_blind_map()
    M['blind'] = bm

    # pooled card metadata (claim, items, verbatim anchor); pooled ids are the join key
    for line in open(ROOT / 'cards' / 'T1.cards.jsonl', encoding='utf-8'):
        c = json.loads(line)
        key, orig = bm[c['id']]
        M['cardmeta'][c['id']] = dict(card=c['id'], run=key, orig_id=orig, type=c['type'],
                                      claim=c['claim'], context=c.get('context', ''),
                                      evidence=c.get('evidence', ''), items=c.get('items', []),
                                      anchor=anchor_of(c.get('verbatim')), data_ids=c.get('data_ids', []),
                                      t_rel_h=c.get('t_rel_h'))

    # card -> unit maps (original claim id -> unit id; null = unmappable)
    for key in RUNS:
        mp = json.load(open(ROOT / 'passb' / ('%s.map.json' % key), encoding='utf-8'))
        M['maps'][key] = mp
        for orig, uid in mp.items():
            M['unit_of'][(key, orig)] = uid

    # Pass A, per rater
    for rater, paths in discover_passa().items():
        cards = {r['card']: r for r in read_csv(paths['cards'])}
        items = {}
        if paths['items'].exists():
            for r in read_csv(paths['items']):
                items.setdefault(r['card'], []).append(r)
        runs = {r['run']: r for r in read_csv(paths['runs'])} if paths['runs'].exists() else {}
        M['passa'][rater] = dict(cards=cards, items=items, runs=runs)

    # Pass B, per rater, straight from the exports (scores/passb.*.csv is Aaron-only)
    for rater, files in discover_passb().items():
        M['passb'][rater] = {}
        for key, p in files.items():
            d = json.load(open(p, encoding='utf-8'))
            assert d['run_key'] == key, (p, d['run_key'])
            M['passb'][rater][key] = dict(units=d['units'], skim=d.get('skim', {}),
                                          final=d.get('final', {}), events=d.get('events', []),
                                          exported=d.get('exported', ''), phase=d.get('phase', ''),
                                          effort=effort(d.get('events', [])))

    for key in RUNS:
        M['runs'][key] = dict(key=key, **IDENTITY[key])

    # derived: unit stratum (conclusion-bearing = holds >=1 inference/verdict card by map)
    concl = set()
    for cm in M['cardmeta'].values():
        if cm['type'] in ('inference', 'verdict'):
            uid = M['unit_of'].get((cm['run'], cm['orig_id']))
            if uid:
                concl.add((cm['run'], uid))
    M['conclusion_units'] = concl
    return M


# ----------------------------------------------------------------- derived --
def cards_in_unit(M, key, uid):
    """Pooled card ids mapped to (key, uid), in original-claim-id order."""
    return sorted((c for c, cm in M['cardmeta'].items()
                   if cm['run'] == key and M['unit_of'].get((key, cm['orig_id'])) == uid),
                  key=lambda c: M['cardmeta'][c]['orig_id'])


def unmapped_cards(M, key):
    return sorted((c for c, cm in M['cardmeta'].items()
                   if cm['run'] == key and not M['unit_of'].get((key, cm['orig_id']))),
                  key=lambda c: M['cardmeta'][c]['orig_id'])


def unit_order(units):
    """Display order: measure units by cell, then standalone ana units by cell."""
    return sorted(units, key=lambda u: (0 if u['notebook'] == 'measure' else 1, u['cell_range'][0]))


def card_row(M, rater, card):
    """One cards.csv row (also the per-card record the renderers use)."""
    cm = M['cardmeta'][card]
    pa = M['passa'][rater]
    sc = pa['cards'].get(card, {})
    its = pa['items'].get(card, [])
    counts = {v: sum(1 for i in its if i['verdict'] == v) for v in ITEM_VERDICTS}
    uid = M['unit_of'].get((cm['run'], cm['orig_id']))
    return dict(card=card, orig_id=cm['orig_id'], run=cm['run'], rater=rater, type=cm['type'],
                hidden=int(sc.get('hidden') == '1'), verdict=sc.get('verdict', ''),
                value=sc.get('value', ''), weight=sc.get('weight', ''),
                recognized=sc.get('recognized', ''), n_items=len(its),
                n_correct=counts['correct'], n_partial=counts['partial'],
                n_wrong=counts['wrong'], n_unverifiable=counts['unverifiable'],
                anchor=cm['anchor'], unit_id=uid or '',
                stratum=('conclusion' if (cm['run'], uid) in M['conclusion_units'] else 'routine') if uid else '',
                note=sc.get('note', ''), ts=sc.get('ts', ''), claim=cm['claim'],
                items=[dict(item=i['item'], verdict=i['verdict'], value=i['value'], text=i['text']) for i in its])


def unit_row(M, rater, key, u):
    uid = u['unit_id']
    cards = cards_in_unit(M, key, uid)
    return dict(run=key, rater=rater, unit_id=uid, notebook=u['notebook'],
                cell_start=u['cell_range'][0], cell_end=u['cell_range'][1], title=u['title'],
                context=int(bool(u.get('context'))), context_reason=u.get('context_reason') or '',
                stratum='conclusion' if (key, uid) in M['conclusion_units'] else 'routine',
                ruling=u.get('ruling') or '', note=u.get('note') or '', ts=u.get('ts') or '',
                n_cards=len(cards),
                n_inference=sum(1 for c in cards if M['cardmeta'][c]['type'] == 'inference'),
                n_decision=sum(1 for c in cards if M['cardmeta'][c]['type'] == 'decision'),
                n_verdict=sum(1 for c in cards if M['cardmeta'][c]['type'] == 'verdict'),
                inline=u.get('inline') or [], data_ids=u.get('data_ids') or [])


def unit_rows(M, rater, key):
    return [unit_row(M, rater, key, u) for u in unit_order(M['passb'][rater][key]['units'])]


def divergence(value, hidden, ruling, context):
    """Analysis #3 cell: 'down' (v=1.0 in shaky/wrong), 'up' (v<0.5 in sound), 'none', or
    an ineligibility reason."""
    if hidden:
        return 'ineligible:hidden'
    if value in (None, ''):
        return 'ineligible:unverifiable'
    if ruling is None:
        return 'ineligible:unmapped'
    if context:
        return 'ineligible:context-unit'
    if ruling in ('', 'na'):
        return 'ineligible:na-unit' if ruling == 'na' else 'ineligible:unruled'
    v = float(value)
    if v == 1.0 and ruling in ('shaky', 'wrong'):
        return 'down'
    if v < 0.5 and ruling == 'sound':
        return 'up'
    return 'none'


def concordance_rows(M):
    rows = []
    for rater_a in sorted(M['passa']):
        for rater_b in sorted(M['passb']):
            for card in sorted(M['cardmeta']):
                cm = M['cardmeta'][card]
                key = cm['run']
                if key not in M['passb'][rater_b]:
                    continue
                cr = card_row(M, rater_a, card)
                uid = M['unit_of'].get((key, cm['orig_id']))
                u = next((x for x in M['passb'][rater_b][key]['units'] if x['unit_id'] == uid), None) if uid else None
                ruling = (u.get('ruling') or '') if u else None
                context = bool(u and u.get('context'))
                rows.append(dict(card=card, orig_id=cm['orig_id'], run=key, type=cm['type'],
                                 rater_a=rater_a, hidden=cr['hidden'], value=cr['value'],
                                 rater_b=rater_b, unit_id=uid or '',
                                 unit_context=int(context) if u else '',
                                 unit_ruling=ruling or '',
                                 stratum=('conclusion' if (key, uid) in M['conclusion_units'] else 'routine') if uid else '',
                                 divergence=divergence(cr['value'], cr['hidden'], ruling, context)))
    return rows


def propagation_rows(conc):
    rows = []
    pairs = sorted({(r['rater_a'], r['rater_b']) for r in conc})
    for ra, rb in pairs:
        keys = sorted({r['run'] for r in conc if (r['rater_a'], r['rater_b']) == (ra, rb)})
        for key in keys + ['ALL']:
            rs = [r for r in conc if (r['rater_a'], r['rater_b']) == (ra, rb) and (key == 'ALL' or r['run'] == key)]
            el = [r for r in rs if not r['divergence'].startswith('ineligible')]
            v1 = [r for r in el if float(r['value']) == 1.0]
            lo = [r for r in el if float(r['value']) < 0.5]
            d = dict(run=key, rater_a=ra, rater_b=rb, n_cards=len(rs), eligible=len(el),
                     n_v1=len(v1), n_v1_down=sum(1 for r in v1 if r['divergence'] == 'down'),
                     n_vlt05=len(lo), n_vlt05_up=sum(1 for r in lo if r['divergence'] == 'up'))
            d['down_rate'] = ('%.3f' % (d['n_v1_down'] / d['n_v1'])) if d['n_v1'] else ''
            d['up_rate'] = ('%.3f' % (d['n_vlt05_up'] / d['n_vlt05'])) if d['n_vlt05'] else ''
            rows.append(d)
    return rows


def tally(M, rater, key):
    """Stratified ruling tally for graded units: {'conclusion': {ruling: n}, 'routine': {...}}."""
    t = {'conclusion': {r: 0 for r in RULINGS + ['unruled']},
         'routine': {r: 0 for r in RULINGS + ['unruled']}}
    for u in M['passb'][rater][key]['units']:
        if u.get('context'):
            continue
        s = 'conclusion' if (key, u['unit_id']) in M['conclusion_units'] else 'routine'
        t[s][u.get('ruling') or 'unruled'] += 1
    return t


def run_row(M, key, rater, prop_index):
    ident = M['runs'][key]
    d = dict(run=key, rater=rater, device=ident['device'], model=ident['model'], corpus=ident['corpus'],
             label=ident['label'], call=ident['call'], call_correct=ident['call_correct'])
    pa = M['passa'].get(rater, {}).get('runs', {}).get(key)
    d['passa'] = int(bool(pa))
    for col in ('n_cards', 'n_scored', 'n_unverifiable', 'S_claim', 'inference_acc', 'decision_acc',
                'verdict_acc', 'item_acc', 'inference_n', 'decision_n', 'verdict_n'):
        d[col] = (pa or {}).get(col, '')
    pb = M['passb'].get(rater, {}).get(key)
    d['passb'] = int(bool(pb))
    if pb:
        sk, fi, ef = pb['skim'], pb['final'], pb['effort']
        d.update(exported=pb['exported'], phase=pb['phase'],
                 know_adjudicated=sk.get('know_adjudicated', ''),
                 skim_disposition=sk.get('skim_disposition', ''), skim_supervision=sk.get('skim_supervision', ''),
                 final_disposition=fi.get('final_disposition', ''), final_supervision=fi.get('final_supervision', ''))
        d['skim_disposition_text'] = DISP.get(d['skim_disposition'], '')
        d['skim_supervision_text'] = SUP.get(d['skim_supervision'], '')
        d['final_disposition_text'] = DISP.get(d['final_disposition'], '')
        d['final_supervision_text'] = SUP.get(d['final_supervision'], '')
        d['disposition_delta'] = (SEVERITY.get(d['final_disposition'], 0) - SEVERITY.get(d['skim_disposition'], 0)
                                  if d['final_disposition'] and d['skim_disposition'] else '')
        d['supervision_delta'] = (SEVERITY.get(d['final_supervision'], 0) - SEVERITY.get(d['skim_supervision'], 0)
                                  if d['final_supervision'] and d['skim_supervision'] else '')
        for f, _ in SKIM_FIELDS:
            d[f] = sk.get(f, '')
        for f, _ in FINAL_FIELDS:
            d[f] = fi.get(f, '')
        d['reanalysis_filled'] = int(bool(fi.get('reanalysis', '').strip()))
        d['remeasure_filled'] = int(bool(fi.get('remeasure', '').strip()))
        units = pb['units']
        d['n_units'] = sum(1 for u in units if not u.get('context'))
        d['n_context'] = sum(1 for u in units if u.get('context'))
        t = tally(M, rater, key)
        for s, pre in (('conclusion', 'cb'), ('routine', 'ro')):
            d['%s_units' % pre] = sum(t[s].values())
            for r in RULINGS:
                d['%s_%s' % (pre, r)] = t[s][r]
        for col in ('skim_min', 'grading_min', 'debrief_min', 'active_min', 'wall_h', 'break_h'):
            d[col] = ('%.2f' % ef[col]) if col in ef else ''
        d['n_breaks'] = ef.get('n_breaks', '')
        d['n_events'] = ef.get('n_events', '')
    # propagation for the (rater, rater) pair when this rater did both passes
    p = prop_index.get((key, rater, rater))
    for col in ('eligible', 'n_v1', 'n_v1_down', 'down_rate', 'n_vlt05', 'n_vlt05_up', 'up_rate'):
        d['prop_%s' % col] = p[col] if p else ''
    return d


def notes_rows(M):
    """Every free-text field anyone wrote. One record per non-empty field."""
    out = []
    for rater in sorted(M['passa']):
        for card in sorted(M['cardmeta']):
            cr = card_row(M, rater, card)
            if cr['note'].strip():
                out.append(dict(run=cr['run'], rater=rater, **{'pass': 'A'}, level='card', field='note',
                                ref=card, orig_id=cr['orig_id'], unit_id=cr['unit_id'],
                                type=cr['type'], value=cr['value'], hidden=cr['hidden'],
                                ruling='', text=cr['note'].strip()))
    for rater in sorted(M['passb']):
        for key in sorted(M['passb'][rater]):
            pb = M['passb'][rater][key]
            for f, _ in SKIM_FIELDS:
                if (pb['skim'].get(f) or '').strip():
                    out.append(dict(run=key, rater=rater, **{'pass': 'B'}, level='run', field=f, ref=key,
                                    orig_id='', unit_id='', type='', value='', hidden='',
                                    ruling='', text=pb['skim'][f].strip()))
            for f, _ in FINAL_FIELDS:
                if (pb['final'].get(f) or '').strip():
                    out.append(dict(run=key, rater=rater, **{'pass': 'B'}, level='run', field=f, ref=key,
                                    orig_id='', unit_id='', type='', value='', hidden='',
                                    ruling='', text=pb['final'][f].strip()))
            for u in unit_order(pb['units']):
                if (u.get('note') or '').strip():
                    out.append(dict(run=key, rater=rater, **{'pass': 'B'}, level='unit', field='note',
                                    ref=u['unit_id'], orig_id='', unit_id=u['unit_id'], type='', value='',
                                    hidden='', ruling=(u.get('ruling') or ('context' if u.get('context') else '')),
                                    text=u['note'].strip()))
    return out


def theme_hits(notes):
    """{slug: [note record, ...]} for the declared THEMES lexicon."""
    hits = {}
    for slug, _, rx in THEMES:
        pat = re.compile(rx, re.I)
        hits[slug] = [n for n in notes if pat.search(n['text'])]
    return hits


# ---------------------------------------------------------------- writing --
def write_csv(path, rows, cols):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


RUN_COLS = ['run', 'rater', 'device', 'model', 'corpus', 'label', 'call', 'call_correct',
            'passa', 'n_cards', 'n_scored', 'n_unverifiable', 'S_claim', 'inference_acc', 'decision_acc',
            'verdict_acc', 'item_acc', 'inference_n', 'decision_n', 'verdict_n',
            'passb', 'exported', 'phase', 'know_adjudicated',
            'skim_disposition', 'skim_supervision', 'final_disposition', 'final_supervision',
            'skim_disposition_text', 'skim_supervision_text', 'final_disposition_text', 'final_supervision_text',
            'disposition_delta', 'supervision_delta', 'reanalysis_filled', 'remeasure_filled',
            'n_units', 'n_context',
            'cb_units', 'cb_sound', 'cb_shaky', 'cb_wrong', 'cb_na',
            'ro_units', 'ro_sound', 'ro_shaky', 'ro_wrong', 'ro_na',
            'prop_eligible', 'prop_n_v1', 'prop_n_v1_down', 'prop_down_rate',
            'prop_n_vlt05', 'prop_n_vlt05_up', 'prop_up_rate',
            'skim_min', 'grading_min', 'debrief_min', 'active_min', 'wall_h', 'n_breaks', 'break_h', 'n_events',
            'know_text', 'skim_impression', 'overall_read', 'reanalysis', 'remeasure',
            'omission', 'biggest_right', 'biggest_wrong']
UNIT_COLS = ['run', 'rater', 'unit_id', 'notebook', 'cell_start', 'cell_end', 'title', 'context',
             'context_reason', 'stratum', 'ruling', 'note', 'ts', 'n_cards', 'n_inference', 'n_decision', 'n_verdict']
CARD_COLS = ['card', 'orig_id', 'run', 'rater', 'type', 'hidden', 'verdict', 'value', 'weight', 'recognized',
             'n_items', 'n_correct', 'n_partial', 'n_wrong', 'n_unverifiable', 'anchor', 'unit_id', 'stratum',
             'note', 'ts', 'claim']
CONC_COLS = ['card', 'orig_id', 'run', 'type', 'rater_a', 'hidden', 'value', 'rater_b', 'unit_id',
             'unit_context', 'unit_ruling', 'stratum', 'divergence']
PROP_COLS = ['run', 'rater_a', 'rater_b', 'n_cards', 'eligible', 'n_v1', 'n_v1_down', 'down_rate',
             'n_vlt05', 'n_vlt05_up', 'up_rate']
NOTE_COLS = ['run', 'rater', 'pass', 'level', 'field', 'ref', 'orig_id', 'unit_id', 'type', 'value',
             'hidden', 'ruling', 'text']


def build(M):
    """All derived tables in one dict (the renderers take this)."""
    conc = concordance_rows(M)
    prop = propagation_rows(conc)
    prop_index = {(p['run'], p['rater_a'], p['rater_b']): p for p in prop}
    raters = sorted(set(M['passa']) | set(M['passb']))
    runs = [run_row(M, key, r, prop_index) for key in RUNS for r in raters
            if (r in M['passa'] and key in M['passa'][r]['runs']) or key in M['passb'].get(r, {})]
    units = [ur for r in sorted(M['passb']) for key in sorted(M['passb'][r]) for ur in unit_rows(M, r, key)]
    cards = [card_row(M, r, c) for r in sorted(M['passa']) for c in sorted(M['cardmeta'])]
    notes = notes_rows(M)
    return dict(runs=runs, units=units, cards=cards, concordance=conc, propagation=prop,
                notes=notes, themes=theme_hits(notes), raters=raters)


def write_artifacts(T):
    write_csv(HERE / 'runs.csv', T['runs'], RUN_COLS)
    write_csv(HERE / 'units.csv', T['units'], UNIT_COLS)
    write_csv(HERE / 'cards.csv', T['cards'], CARD_COLS)
    write_csv(HERE / 'concordance.csv', T['concordance'], CONC_COLS)
    write_csv(HERE / 'propagation.csv', T['propagation'], PROP_COLS)
    with open(HERE / 'notes.jsonl', 'w', encoding='utf-8') as f:
        for n in T['notes']:
            f.write(json.dumps({k: n[k] for k in NOTE_COLS}, ensure_ascii=False) + '\n')


def main():
    M = load()
    T = build(M)
    write_artifacts(T)
    print('runs %d  units %d  cards %d  concordance %d  propagation %d  notes %d  raters %s'
          % (len(T['runs']), len(T['units']), len(T['cards']), len(T['concordance']),
             len(T['propagation']), len(T['notes']), ','.join(T['raters'])))
    try:
        import synth_render_run, synth_render_index
    except ImportError as ex:
        print('renderers not available (%s); tables written only' % ex)
        return
    for key in RUNS:
        out = HERE / ('%s.html' % key)
        out.write_text(synth_render_run.render(M, T, key), encoding='utf-8')
        print('wrote', out.name, out.stat().st_size)
    out = HERE / 'index.html'
    out.write_text(synth_render_index.render(M, T), encoding='utf-8')
    print('wrote', out.name, out.stat().st_size)


if __name__ == '__main__':
    main()
