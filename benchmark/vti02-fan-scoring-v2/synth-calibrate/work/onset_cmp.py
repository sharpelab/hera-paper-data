"""Per-tone onsets (live-check onsets.py definitions) on live vs sim maps."""
import sys, warnings, importlib.util
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import f_L
spec = importlib.util.spec_from_file_location('ha', '/home/zack/sharpelab/measurement-env/src/hera/analysis.py')
ha = importlib.util.module_from_spec(spec); sys.modules['ha'] = ha; spec.loader.exec_module(ha)
RF = (0.0394, 0.1235)


def onsets(R, B, n_act, step=2, label=''):
    rows = []
    for j in range(0, R.shape[1], step):
        n = n_act[j]
        if n < 0.5 or not np.all(np.isfinite(R[:, j])):
            continue
        FL = f_L(n); fl = (RF[0] * n + RF[1]) * FL; fh = FL - fl
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try:
                o = ha.sdh_onset(R[:, j], B, b_lo=B.min(), f_min=1.5)
            except Exception as e:
                continue
        rec = dict(src=label, col=j, n=n, onset_b=o.onset_b)
        for lab, fr, tol in (('light', fl, max(0.35 * fl, 1.2)), ('heavy', fh, 0.06 * FL), ('FL', 0.97 * FL, 0.06 * FL)):
            c = [t for t in o.tones if abs(t.freq - fr) <= tol and not t.marginal]
            if c:
                t = min(c, key=lambda t: abs(t.freq - fr))
                rec[f'{lab}_onset'] = t.onset_b; rec[f'{lab}_cens'] = t.censored
        rows.append(rec)
    return pd.DataFrame(rows)


def summarize(df):
    out = {}
    for lab in ('light', 'heavy', 'FL'):
        k = f'{lab}_onset'
        if k in df and df[k].notna().any():
            out[lab] = (int(df[k].notna().sum()), round(float(np.nanmedian(df[k])), 2))
        else:
            out[lab] = (0, None)
    return out
