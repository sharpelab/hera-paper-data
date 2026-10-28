import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
from fft_q1 import col_fft
for nm, sw in (('0825-r8', 20.4e-9), ('0822-r8', 20.4e-9), ('0821-r8', 35.4e-9), ('0824-r4', 35.4e-9)):
    d = load(nm); B = d['B']; X = d['g']('sr1_X'); I = np.median(np.abs(d['I']))
    Y = X * np.tan(np.deg2rad(d['g']('sr1_P'))) if 'sr1_P' in d['cols'] else d['g']('sr1_Y')
    # remove in-phase leakage: fit Y = a X per column (global a)
    a = np.sum(X * Y) / np.sum(X * X); Yc = Y - a * X
    lo = max(1.0, B.min()) if nm != '0824-r4' else 2.0
    rng = np.random.default_rng(0)
    res = {'X': [], 'Y': [], 'Yc': [], 'white': []}
    t = d['t']; dtr = np.median(np.diff(np.sort(t[:, 0])))
    for j in range(d['nfast']):
        if d['n'][j] < 0.5: continue
        fL = 10.3392 * d['n'][j]
        for k, y in (('X', X[:, j]), ('Y', Y[:, j]), ('Yc', Yc[:, j]), ('white', sw * rng.standard_normal(B.size))):
            F, S, m, du, wn = col_fft(y / I, B, lo, B.max())
            hb = (F > 1.12 * fL) & (F < 0.95 * 0.5 / du)
            res[k].append(np.median(S[hb]) if hb.sum() > 20 else np.nan)
    # also sigma of Yc along columns via row-to-row differences
    dY = np.diff(Yc[np.argsort(B)], axis=0)
    print(f'{nm}: I={I*1e9:.1f} nA  leak a={a:+.3f}  row period ~{dtr:.0f}s | floor (ohm units) X {np.nanmedian(res["X"]):.2f}  Y {np.nanmedian(res["Y"]):.2f}  Yc {np.nanmedian(res["Yc"]):.2f}  white(40nV) {np.nanmedian(res["white"]):.2f} | '
          f'sigma_Yc along B (row diffs) {1.4826*np.median(np.abs(dY))/np.sqrt(2)*1e9:.1f} nV vs within-row 2nd-diff (REPORT) ')
