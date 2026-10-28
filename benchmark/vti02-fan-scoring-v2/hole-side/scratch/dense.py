import numpy as np, sys
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model, peaks
tr = {t['id']: t for t in load_all(include_ramp=False)}
cfg = {'0822-r7': [(0.5, 5), (0.6, 5), (0.75, 5), (1.0, 5), (0.6, 4), (0.75, 3), (1.0, 3), (0.6, 2.3), (0.4, 2.3), (1.0, 10), (0.6, 10)],
       '0824-r5-c0': [(0.51, 6), (0.6, 6), (0.75, 6), (1.0, 6), (0.51, 4), (0.75, 4), (0.51, 3), (1.0, 4)],
       '0825-r7-c0': [(1.5, 6), (1.8, 6), (1.5, 5), (1.5, 4)]}
for k, wins in cfg.items():
    t = tr[k]; print(k, 'n_frame', t['n_frame'], 'n_e', round(t['n_act_e'], 3), 'model(h) at n_e:', np.round(model(abs(t['n_act_e'])), 2))
    for lo, hi in wins:
        for deg in (3, 5, 7):
            s = spec(t['B'], t['R'], lo, hi, deg, Fmax=30)
            if s is None: continue
            hb = (s['F'] > 13) & (s['F'] < min(0.9 * s['nyq'], 30))
            fl = np.median(s['S'][hb]) if hb.sum() > 50 else np.nan
            Z = s['S'] / s['med_noise']
            pk = peaks(s['F'], Z, 0.75 * s['dF'], min(20, s['nyq']), 4, 8)
            print(f"  [{s['lo']:.2f},{s['hi']:.2f}] deg {deg} dF {s['dF']:.2f} nyq {s['nyq']:.0f} rows {s['rows']} sig {s['sigma']:.2f} emp/white {fl / s['med_noise']:.1f}:",
                  ' '.join(f'{f:.2f}({z:.0f})' for f, z in pk))
