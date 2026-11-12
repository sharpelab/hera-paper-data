"""Per-tone matched-filter onsets (hera.analysis.sdh_onset, read-only import) per column; classify tones light/heavy/F_L."""
import numpy as np, sys, warnings, importlib.util, pandas as pd
sys.path.insert(0, '.')
from load import load, f_L
spec = importlib.util.spec_from_file_location('ha', '/home/zack/sharpelab/measurement-env/src/hera/analysis.py')
ha = importlib.util.module_from_spec(spec); sys.modules['ha'] = ha; spec.loader.exec_module(ha)
RF = (0.0394, 0.1235)  # observed light fraction r(n) = a n + b (0825 full window)
rows = []
for nm in ['0825-r8', '0822-r8', '0821-r8']:
    d = load(nm); B = d['B']
    for j in range(0, d['nfast'], 2):
        n = d['n'][j]; FL = f_L(n); fl = (RF[0] * n + RF[1]) * FL; fh = FL - fl
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try:
                o = ha.sdh_onset(d['R'][:, j], B, b_lo=B.min(), f_min=1.5)
            except Exception as e:
                rows.append(dict(fan=nm, col=j, n=n, err=str(e)[:60])); continue
        rec = dict(fan=nm, col=j, n=round(n, 3), onset_b=round(o.onset_b, 2), onset_freq=round(o.onset_freq, 1))
        for lab, fr, tol in (('light', fl, max(0.35 * fl, 1.2)), ('heavy', fh, 0.06 * FL), ('FL', 0.97 * FL, 0.06 * FL)):
            c = [t for t in o.tones if abs(t.freq - fr) <= tol and not t.marginal]
            if c:
                t = min(c, key=lambda t: abs(t.freq - fr))
                rec[f'{lab}_F'] = round(t.freq, 1); rec[f'{lab}_onset'] = round(t.onset_b, 2); rec[f'{lab}_cens'] = t.censored
        rows.append(rec)
df = pd.DataFrame(rows); df.to_csv('tone_onsets.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
print(df.to_string())
for nm in df.fan.unique():
    a = df[df.fan == nm]
    print(nm, {lab: (int(a[f'{lab}_onset'].notna().sum()), float(np.nanmedian(a[f'{lab}_onset'])) if a[f'{lab}_onset'].notna().any() else None,
                     int(a.get(f'{lab}_cens', pd.Series(dtype=bool)).fillna(False).astype(bool).sum())) for lab in ('light', 'heavy', 'FL') if f'{lab}_onset' in a})
