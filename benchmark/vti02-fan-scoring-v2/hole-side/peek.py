import json, gzip, io, numpy as np
from pathlib import Path
N = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
for s, r in [('22',7),('24',4),('24',5),('25',7),('23',6),('23',7),('25',5),('25',6)]:
    p = N/f'2026-08-{s}-vti-02-session'/'data'/str(r)
    m = json.load(open(p/'metadata.json'))
    X = np.loadtxt(io.StringIO(gzip.decompress((p/'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    ins = m['instruments']
    lk = {}
    for nm in ('sr0','sr1'):
        pp = ins[nm]['snapshot']['parameters']
        lk[nm] = {k: pp[k]['value'] for k in ('sensitivity','time_constant','filter_slope','amplitude','frequency') if k in pp}
    mc = m['measurement_config']
    print(f'08-{s} r{r}', m['type'], m['function'], X.shape, m['columns'])
    print('   lk', lk, 'gain', mc.get('sr0_gain'), 'Rb', mc.get('bias_resistor'))
    print('   keys', [k for k in m.keys() if k not in ('instruments','columns','comments','measurement_config')])
    for k in ('fast_delay','slow_delay','delay'):
        if k in m: print('  ', k, m[k])
    ci = {c:i for i,c in enumerate(m['columns'])}
    I = X[:, m['columns'].index('sr0_X')]/mc['sr0_gain']
    print('   I nA median', np.median(np.abs(I))*1e9)
