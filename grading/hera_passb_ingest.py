#!/usr/bin/env python3
"""Ingest Pass B debrief exports into flat CSVs.
usage: hera_passb_ingest.py <export.passb.json> [...]   (or no args: passb/*.passb.json)
Writes scores/passb.runs.csv (one row per run) and scores/passb.units.csv (one row
per unit, context units included with ruling empty). Idempotent: rows keyed by run
are replaced on re-ingest. Raw exports should be committed beside the CSVs."""
import csv, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
paths = [pathlib.Path(p) for p in sys.argv[1:]] or sorted(HERE.glob('passb/*.passb.json'))
if not paths:
    sys.exit('no exports found (passb/*.passb.json)')

RUN_COLS = ['run', 'exported', 'phase', 'n_units', 'n_context', 'n_sound', 'n_shaky',
            'n_wrong', 'n_na', 'n_unruled', 'know_adjudicated', 'know_text',
            'skim_disposition', 'skim_supervision', 'skim_impression',
            'final_disposition', 'final_supervision', 'reanalysis', 'remeasure',
            'overall_read', 'omission', 'biggest_right', 'biggest_wrong',
            'skim_ts', 'began_ts', 'final_ts', 'n_events']
UNIT_COLS = ['run', 'unit_id', 'notebook', 'cell_start', 'cell_end', 'title',
             'context', 'context_reason', 'ruling', 'note', 'ts']

runs, units = {}, {}
for out in ('passb.runs.csv', 'passb.units.csv'):
    p = HERE / 'scores' / out
    if p.exists():
        with open(p, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                (runs if out == 'passb.runs.csv' else units).setdefault(r['run'], []).append(r)

for path in paths:
    d = json.load(open(path, encoding='utf-8'))
    key = d['run_key']
    us = d.get('units', [])
    graded = [u for u in us if not u.get('context')]
    tally = {}
    for u in graded:
        tally[u.get('ruling') or 'unruled'] = tally.get(u.get('ruling') or 'unruled', 0) + 1
    skim, final = d.get('skim', {}), d.get('final', {})
    runs[key] = [{
        'run': key, 'exported': d.get('exported', ''), 'phase': d.get('phase', ''),
        'n_units': len(graded), 'n_context': len(us) - len(graded),
        'n_sound': tally.get('sound', 0), 'n_shaky': tally.get('shaky', 0),
        'n_wrong': tally.get('wrong', 0), 'n_na': tally.get('na', 0),
        'n_unruled': tally.get('unruled', 0),
        'know_adjudicated': skim.get('know_adjudicated', ''), 'know_text': skim.get('know_text', ''),
        'skim_disposition': skim.get('skim_disposition', ''), 'skim_supervision': skim.get('skim_supervision', ''),
        'skim_impression': skim.get('skim_impression', ''),
        'final_disposition': final.get('final_disposition', ''), 'final_supervision': final.get('final_supervision', ''),
        'reanalysis': final.get('reanalysis', ''), 'remeasure': final.get('remeasure', ''),
        'overall_read': final.get('overall_read', ''), 'omission': final.get('omission', ''),
        'biggest_right': final.get('biggest_right', ''), 'biggest_wrong': final.get('biggest_wrong', ''),
        'skim_ts': skim.get('ts') or '', 'began_ts': skim.get('began_ts') or '',
        'final_ts': final.get('ts') or '', 'n_events': len(d.get('events', [])),
    }]
    units[key] = [{
        'run': key, 'unit_id': u.get('unit_id', ''), 'notebook': u.get('notebook', ''),
        'cell_start': (u.get('cell_range') or ['', ''])[0], 'cell_end': (u.get('cell_range') or ['', ''])[1],
        'title': u.get('title', ''), 'context': int(bool(u.get('context'))),
        'context_reason': u.get('context_reason') or '', 'ruling': u.get('ruling') or '',
        'note': u.get('note', ''), 'ts': u.get('ts') or '',
    } for u in us]
    n_r = sum(1 for u in graded if u.get('ruling'))
    print('%s: %d/%d graded units ruled (%s), disposition %s, supervision %s'
          % (key, n_r, len(graded), ' '.join('%s=%d' % kv for kv in sorted(tally.items())),
             final.get('final_disposition') or '-', final.get('final_supervision') or '-'))

(HERE / 'scores').mkdir(exist_ok=True)
for out, cols, data in (('passb.runs.csv', RUN_COLS, runs), ('passb.units.csv', UNIT_COLS, units)):
    with open(HERE / 'scores' / out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for key in sorted(data):
            for row in data[key]:
                w.writerow(row)
    print('wrote scores/%s' % out)
