"""Point-to-point (time-sequence) and row-to-row noise of sr1 Y (leak-removed) and X, every run."""
import json, sys, numpy as np
sys.path.insert(0, '.')
from nd import *
inv = json.load(open('inventory_raw.json'))
res = []
for r in inv:
    if (r.get('npts') or 0) < 60: continue
    try: d = loadrun(r['day'], r['run'])
    except Exception as e: print('fail', r['day'], r['run'], e); continue
    X, Y, t = d['sr1X'], d['sr1Y'], d['t']
    if Y is None: continue
    tau, sl = d['tau'], d['slope']
    a = np.nansum(X * Y) / np.nansum(X * X); Yc = Y - a * X
    # sequence (as recorded) 2nd diffs along the fast axis (or along the 1D sweep)
    dt = np.nanmedian(np.diff(t, axis=1)) if d['nfast'] > 2 else np.nan
    cf = corr_d2(dt, tau)
    sfy = np.nanmedian(rob(d2(Yc, 1), axis=1)) / np.sqrt(6) * cf if d['nfast'] > 4 else np.nan
    sfx = np.nanmedian(rob(d2(X, 1), axis=1)) / np.sqrt(6) * cf if d['nfast'] > 4 else np.nan
    row = dict(run=f"{r['day']}-r{r['run']}", type=r['type'], nrows=d['nrows'], nfast=d['nfast'], tau=tau, sens=d['sens'], amp=d['amp'],
               I_nA=round(d['I'] * 1e9, 1), dt=round(dt, 2), dt_tau=round(dt / tau, 1), leak=round(a, 3),
               fastY_nV=round(sfy * 1e9, 1), fastX_nV=round(sfx * 1e9, 1), fastY_d=round(to_density(sfy, tau, sl) * 1e9, 1))
    if d['nrows'] >= 8 and d['nfast'] >= 3:
        dtr = np.nanmedian(np.diff(t[:, 0]))
        sry = np.nanmedian(rob(d2(Yc, 0), axis=0)) / np.sqrt(6)
        srx = np.nanmedian(rob(d2(X, 0), axis=0)) / np.sqrt(6)
        row.update(row_dt=round(dtr, 1), rowY_nV=round(sry * 1e9, 1), rowX_nV=round(srx * 1e9, 1), rowY_d=round(to_density(sry, tau, sl) * 1e9, 1))
    res.append(row)
    print(row, flush=True)
json.dump(res, open('metric_all.json', 'w'), indent=1)
