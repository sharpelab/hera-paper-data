"""Shared helpers for noise-diag (read-only on the data)."""
import json, gzip, io, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from noise_q import acf4
S = '/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-08-%d-vti-02-session/data/%d'
FIX = {('0821', 8): 21, ('0822', 8): 22, ('0824', 4): 24, ('0825', 8): 25}
ENBW = {6: 1/4, 12: 1/8, 18: 3/32, 24: 5/64}

def loadrun(day, run):
    p = Path(S % (day, run))
    meta = json.load(open(p / 'metadata.json')); cols = meta['columns']
    X = np.loadtxt(io.StringIO(gzip.decompress((p / 'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    fs = meta.get('fast_setpoints')
    if meta.get('type') == '2D' and fs is not None:
        nfast = len(fs[0]) if isinstance(fs[0], list) else len(fs)
    else:
        nfast = X.shape[0]
    nrows = X.shape[0] // nfast; X = X[:nrows * nfast]
    def g(c, k=0):
        idx = [i for i, cc in enumerate(cols) if cc == c]
        return X[:, idx[k]].reshape(nrows, nfast) if idx else None
    lk = {}
    for nm in ('sr0', 'sr1', 'sr2', 'sr3'):
        if nm in meta['instruments']:
            pp = meta['instruments'][nm]['snapshot']['parameters']
            lk[nm] = {k: pp[k]['value'] for k in ('sensitivity', 'time_constant', 'filter_slope', 'amplitude', 'frequency') if k in pp}
    out = dict(day=day, run=run, meta=meta, cols=cols, g=g, nrows=nrows, nfast=nfast, lk=lk, t=g('time'))
    for ch in ('sr0', 'sr1'):
        x = g(ch + '_X')
        if x is None: continue
        y = g(ch + '_Y')
        if y is None:
            P = g(ch + '_P'); y = x * np.tan(np.deg2rad(P)) if P is not None else None
        out[ch + 'X'] = x; out[ch + 'Y'] = y
    out['B'] = g('magnet_field'); out['T'] = g('T_sample')
    out['Vtg'] = g('k_2400_tg_volt'); out['Vbg'] = g('k_2400_bg_volt')
    mc = meta['measurement_config']
    out['I'] = np.median(np.abs(out['sr0X'])) / abs(mc.get('sr0_gain', -1e6))
    out['tau'] = lk['sr1']['time_constant']; out['slope'] = int(lk['sr1']['filter_slope'])
    out['sens'] = lk['sr1']['sensitivity']; out['amp'] = lk['sr1'].get('amplitude')
    return out

def rob(v, axis=None):
    v = np.asarray(v)
    m = np.nanmedian(v, axis=axis, keepdims=True)
    return 1.4826 * np.nanmedian(np.abs(v - m), axis=axis)

def d2(x, axis=-1):
    x = np.moveaxis(x, axis, -1)
    return np.moveaxis(x[..., :-2] - 2 * x[..., 1:-1] + x[..., 2:], -1, axis)

def corr_d2(dt, tau):
    r1, r2 = acf4(dt / tau), acf4(2 * dt / tau)
    return np.sqrt(6 / (6 - 8 * r1 + 2 * r2))

def corr_d1(dt, tau):
    return np.sqrt(2 / (2 - 2 * acf4(dt / tau)))

def to_density(sig, tau, slope=24):
    return sig / np.sqrt(ENBW[slope] / tau)
