import numpy as np, sys, itertools
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from tonefit import fit
from common import model
tr = {t['id']: t for t in load_all(include_ramp=False)}
cases = {'0822-r7': (1.012, [(0.7, 4.5), (1.0, 4.5), (0.7, 3.0)]), '0824-r5-c0': (0.725, [(0.51, 6.1), (0.7, 6.1), (0.51, 3.0)]),
         '0825-r7-c0': (0.846, [(1.5, 6.0), (1.5, 4.5)])}
for k, (n, wins) in cases.items():
    t = tr[k]; fl, fh, fL = model(n)
    print(k, f'|n| {n}: model light {fl:.2f} heavy {fh:.2f} F_L {fL:.2f}')
    sets = {'h': [fh], 'h+L': [fh, fL], 'l+h': [fl, fh], 'l+h+L': [fl, fh, fL], 'l+h+L+2h': [fl, fh, fL, 2 * fh], 'h+L+2h': [fh, fL, 2 * fh]}
    for lo, hi in wins:
        for name, F0 in sets.items():
            if max(F0) > 0.5 / (1 / max(lo, t['B'].min()) - 1 / (max(lo, t['B'].min()) + 0.02)) and k == '0822-r7' and False: pass
            try:
                r = fit(t['B'], t['R'], lo, hi, F0, deg=3)
            except Exception as e:
                print('  ERR', e); continue
            print(f"  [{r['lo']:.2f},{r['hi']:.2f}] {name:9s} BIC {r['bic']:8.1f} rms {r['rms']:6.2f} | " +
                  '  '.join(f"{x['F']:.2f}±{x['sF']:.2f} A{x['A_hiB']:.0f}->{x['A_loB']:.1f} a{x['a']:.1f}{'!' if x['at_bound'] else ''}" for x in r['tones']))
