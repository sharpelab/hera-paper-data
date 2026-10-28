import json, glob, gzip, io, os, numpy as np, datetime as dtm
rows = []
for p in sorted(glob.glob('/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-06-*-QC0426-session*/data/*/metadata.json')):
    try: d = json.load(open(p))
    except Exception as e: print('bad', p); continue
    sess = p.split('/')[-4]; run = p.split('/')[-2]
    cols = d.get('columns') or d.get('column')
    ins = d.get('instruments', {})
    lk = {}
    for nm, i in ins.items():
        pp = i.get('snapshot', {}).get('parameters', {})
        if 'time_constant' in pp:
            lk[nm] = (pp.get('sensitivity', {}).get('value'), pp.get('time_constant', {}).get('value'), pp.get('filter_slope', {}).get('value'), pp.get('frequency', {}).get('value'), pp.get('amplitude', {}).get('value'))
    f = os.path.join(os.path.dirname(p), 'data.tsv.gz'); n = 0; dt = np.nan; B = None
    if os.path.exists(f) and cols:
        X = np.loadtxt(io.StringIO(gzip.decompress(open(f, 'rb').read()).decode()), delimiter='\t', ndmin=2); n = X.shape[0]
        if 'time' in cols and n > 3: dt = np.median(np.diff(X[:, cols.index('time')]))
        for bc in ('magnet_field', 'magnet_mag', 'fastbi_field'):
            if bc in cols: B = (X[:, cols.index(bc)].min(), X[:, cols.index(bc)].max())
    mc = d.get('measurement_config', {}) or {}
    st = d.get('start_time'); st = dtm.datetime.fromtimestamp(float(st)).strftime('%m-%d %H:%M') if st else '?'
    print(f"{sess[5:10]}{sess[26:]} r{run:>2s} {st} {d.get('type')} n={n} dt={dt:.2f} B={None if B is None else tuple(round(x,2) for x in B)} lk={lk} cols={[c for c in (cols or []) if c.startswith('sr') or 'curr' in c or 'magnet' in c][:14]} mcgain={mc.get('sr0_gain')} {str(mc.get('comments',''))[:60]}")
