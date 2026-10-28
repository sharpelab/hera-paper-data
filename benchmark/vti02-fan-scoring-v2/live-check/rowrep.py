import numpy as np, sys
sys.path.insert(0, '.')
from load import load
for nm in ['0822-r8', '0825-r8']:
    d = load(nm); X = d['g']('sr1_X'); Y = X*np.tan(np.deg2rad(d['g']('sr1_P'))); B = d['B']; o = np.argsort(B); I = np.median(d['I'])
    for comp, Z in (('X', X), ('Y', Y)):
        res = []
        for r in o[:12]:
            r2 = r + 1 if r + 1 < len(B) and abs(B[r+1]-B[r]) < 0.05 else r - 1
            dd = Z[r2] - Z[r]; dd = dd - np.median(dd)
            res.append(1.4826*np.median(np.abs(dd))/np.sqrt(2))
        print(nm, comp, 'row-to-row sigma at B %.2f-%.2f T: %.1f nV (%.2f ohm)' % (B[o[0]], B[o[11]], np.median(res)*1e9, np.median(res)/I))
