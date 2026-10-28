"""Settings inventory for every vti-02 run (Aug 21-25) + fixtures. Read-only."""
import json, gzip, io, glob, os, sys
import numpy as np
S = '/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-08-%d-vti-02-session/data'
LK = ['sensitivity', 'time_constant', 'filter_slope', 'amplitude', 'frequency', 'reserve', 'input_config', 'input_shield',
      'input_coupling', 'notch_filter', 'sync_filter', 'harmonic', 'phase', 'reference_source']
rows = []
for day in range(21, 26):
    for p in sorted(glob.glob(S % day + '/*/metadata.json'), key=lambda s: int(s.split('/')[-2])):
        run = int(p.split('/')[-2])
        try: d = json.load(open(p))
        except Exception: print('SKIP', p); continue
        ins = d.get('instruments', {})
        r = dict(day=day, run=run, type=d.get('type'), start=d.get('start_time'), end=d.get('end_time'),
                 fast=d.get('fast_params'), slow=d.get('slow_params'), fdel=d.get('fast_delay'), sdel=d.get('slow_delay'),
                 cols=d.get('columns'), mc=d.get('measurement_config'), comments=d.get('comments'), interrupted=d.get('interrupted'))
        for nm, i in ins.items():
            pp = i.get('snapshot', {}).get('parameters', {})
            cls = i.get('snapshot', {}).get('__class__', '')
            if 'SR8' in cls:
                r[nm] = {k: pp[k].get('value') for k in LK if k in pp and pp[k].get('value') is not None}
            else:
                r[nm] = {k: v.get('value') for k, v in pp.items() if v.get('value') is not None and not isinstance(v.get('value'), (list, dict))
                         and k not in ('timeout',)}
        f = os.path.join(os.path.dirname(p), 'data.tsv.gz')
        if os.path.exists(f):
            X = np.loadtxt(io.StringIO(gzip.decompress(open(f, 'rb').read()).decode()), delimiter='\t', ndmin=2)
            r['npts'] = X.shape[0]
            if 'time' in r['cols'] and X.shape[0] > 3:
                t = X[:, r['cols'].index('time')]; r['dt_med'] = float(np.median(np.diff(t))); r['dur_h'] = float((t[-1] - t[0]) / 3600)
            for c in r['cols']:
                if c in ('T_sample', 'sample_temperature', 'T_vaporizer', 'vaporizer_temperature', 'magnet_field'):
                    v = X[:, r['cols'].index(c)]; r['rng_' + c] = [float(np.nanmin(v)), float(np.nanmax(v))]
        rows.append(r)
json.dump(rows, open('inventory_raw.json', 'w'), indent=1, default=str)
for r in rows:
    print(f"--- 08-{r['day']} r{r['run']} {r['type']} {r['start']} npts={r.get('npts')} dt={r.get('dt_med', 0):.2f}s dur={r.get('dur_h', 0):.2f}h fast={r['fast']} slow={r['slow']} fdel={r['fdel']} sdel={r['sdel']}")
    print('   cols', r['cols'])
    for nm in ('sr0', 'sr1', 'sr2', 'sr3'):
        if nm in r: print('   ', nm, r[nm])
    for k, v in r.items():
        if k.startswith('rng_'): print('   ', k, np.round(v, 3))
    oth = {k: v for k, v in r.items() if k not in ('sr0','sr1','sr2','sr3','cols','mc','comments') and isinstance(v, dict)}
    for k, v in oth.items(): print('   ', k, {a: b for a, b in v.items() if a in ('volt','mode','output','nplci','nplcv','rangev','field','voltage','range','output_on','smart_voltage','ramp_rate','step','inter_delay','compliancei')})
    mc = r['mc'] or {}
    print('   mc', {k: v for k, v in mc.items() if k not in ('comments',)}, '|', (mc.get('comments') or r['comments'] or '')[:200])
