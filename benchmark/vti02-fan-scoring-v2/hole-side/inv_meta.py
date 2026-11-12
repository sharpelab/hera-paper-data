"""Print a one-line summary of every vti-02 run's metadata (read-only)."""
import json, sys
from pathlib import Path
NOTES = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
for s in ['21','22','23','24','25']:
    d = NOTES / f'2026-08-{s}-vti-02-session' / 'data'
    for r in sorted([p for p in d.iterdir() if p.is_dir()], key=lambda p: int(p.name)):
        try:
            m = json.load(open(r / 'metadata.json'))
        except Exception as e:
            print(s, r.name, 'ERR', e); continue
        def rng(x):
            try:
                import numpy as np
                a = np.array(x, dtype=float).ravel()
                return f'{a.min():.3g}..{a.max():.3g} ({a.size})'
            except Exception:
                return str(x)[:60]
        keys = list(m.keys())
        print(f"08-{s} r{r.name} type={m.get('type')} fn={str(m.get('function'))[:40]} slow={rng(m.get('slow_setpoints')) if m.get('slow_setpoints') is not None else None} fast={rng(m.get('fast_setpoints')) if m.get('fast_setpoints') is not None else None}")
        print('    cols:', [c for c in m.get('columns', [])][:14])
        print('    comments:', ' | '.join(m.get('comments', []))[:400])
