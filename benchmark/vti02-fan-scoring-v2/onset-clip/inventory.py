"""Inventory every vti-02 live run: shape, field range, gate range, lock-in settings."""
import json, gzip, io, glob, numpy as np
from pathlib import Path
S = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
for sess in sorted(S.glob('2026-08-2?-vti-02-session')):
    for p in sorted((sess/'data').iterdir(), key=lambda x: (len(x.name), x.name)):
        if not p.is_dir(): continue
        try: meta = json.load(open(p/'metadata.json'))
        except Exception as e: print(sess.name[:10], p.name, 'nometa'); continue
        cols = meta.get('columns', [])
        f = p/'data.tsv.gz'
        if not f.exists():
            fs = [x.name for x in p.iterdir()]; print(sess.name[:10], p.name, 'files', fs[:6]); continue
        try: X = np.loadtxt(io.StringIO(gzip.decompress(f.read_bytes()).decode()), delimiter='\t', ndmin=2)
        except Exception as e: print(sess.name[:10], p.name, 'err', e); continue
        def c(name):
            i = [k for k, cc in enumerate(cols) if cc == name]; return X[:, i[0]] if i else None
        B = c('magnet_field'); tg = c('k_2400_tg_volt'); bg = c('k_2400_bg_volt')
        ins = meta.get('instruments', {}); lk = ''
        for nm in ('sr1',):
            if nm in ins:
                pp = ins[nm]['snapshot']['parameters']; lk = f"tau={pp.get('time_constant',{}).get('value')} amp={pp.get('amplitude',{}).get('value')} sens={pp.get('sensitivity',{}).get('value')}"
        mc = meta.get('measurement_config', {})
        fsp = meta.get('fast_setpoints'); nf = (len(fsp[0]) if fsp and isinstance(fsp[0], list) else len(fsp)) if fsp else None
        rng = lambda a: 'none' if a is None else f"{np.nanmin(a):.2f}..{np.nanmax(a):.2f}"
        print(sess.name[5:10], p.name.rjust(2), f"N={X.shape[0]:6d} nfast={nf} B={rng(B)} tg={rng(tg)} bg={rng(bg)} Rb={mc.get('bias_resistor')} {lk}")
