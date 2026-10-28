"""Per-column tone medians over extraction choices + per-session F_L frame fit -> columns.csv, session_frames.csv."""
import numpy as np, pandas as pd
FLN = 10.3392
raw = pd.read_csv('columns_raw.csv', dtype={'session': str})
raw['det_L'] = raw.snr_L >= 4
raw['det_light'] = (raw.snr_light >= 4) & (raw.F_light >= 0.75 * raw.dF)
raw['det_heavy'] = raw.snr_heavy >= 4
rows = []
for key, g in raw.groupby(['session', 'run', 'col'], sort=False):
    r = dict(session=key[0], run=key[1], col=key[2], kind=g.kind.iloc[0], n_frame=g.n_frame.iloc[0], T_K=g.T_K.iloc[0],
             n_choice=len(g), dF=g.dF.median(), span=(1 / g.lo - 1 / g.hi).median())
    for t, F, snr in (('L', 'F_L', 'snr_L'), ('light', 'F_light', 'snr_light'), ('heavy', 'F_heavy', 'snr_heavy')):
        d = g[g[f'det_{t}']]
        r[f'rec_{t}'] = len(d) / len(g)
        if len(d) >= max(2, 0.5 * len(g)):
            f = d[F].values
            sc = 1.4826 * np.median(np.abs(f - np.median(f))) if len(f) >= 4 else np.std(f)
            ss = 0.25 * d.dF.median() / d[snr].median()
            r[f'F_{t}'] = np.median(f); r[f'sig_{t}'] = float(np.hypot(max(sc, np.std(f) / 2), ss)); r[f'snr_{t}'] = d[snr].median()
        else:
            r[f'F_{t}'] = np.nan; r[f'sig_{t}'] = np.nan; r[f'snr_{t}'] = g[snr].median()
    rows.append(r)
C = pd.DataFrame(rows)

# frame fit per session: F_L tone vs n_frame, fan + spot columns, electron side, detected F_L
fr = []
for s, g in C[(C.kind.isin(['fan', 'spot'])) & (C.n_frame > 0.4)].groupby('session'):
    d = g[np.isfinite(g.F_L)]
    if s == '0824' or len(d) < 3:
        fr.append(dict(session=s, n_cols=len(d), s0=0.90, s_off=np.nan, n0=0.0, sig_s0=0.045, rms0=np.nan, note='no F_L anchor; 08-25 LL lever arm 0.90 +- 5 %'))
        continue
    w = 1 / d.sig_L ** 2
    x, y = d.n_frame.values, d.F_L.values
    a0 = np.sum(w * x * y) / np.sum(w * x * x); res0 = y - a0 * x
    A = np.vstack([x, np.ones_like(x)]).T; W = np.sqrt(w.values)
    (a1, b1), *_ = np.linalg.lstsq(A * W[:, None], y * W, rcond=None); res1 = y - a1 * x - b1
    chi0 = np.sum(w * res0 ** 2) / (len(x) - 1); chi1 = np.sum(w * res1 ** 2) / (len(x) - 2)
    sig_a0 = np.sqrt(chi0 / np.sum(w * x * x))
    fr.append(dict(session=s, n_cols=len(d), s0=a0 / FLN, sig_s0=sig_a0 / FLN, rms0=np.sqrt(np.mean(res0 ** 2)), chi0=chi0,
                   s_off=a1 / FLN, n0=-b1 / a1, rms1=np.sqrt(np.mean(res1 ** 2)), chi1=chi1))
F = pd.DataFrame(fr); F.to_csv('session_frames.csv', index=False)
print(F.round(4).to_string())
C.to_csv('columns_tones.csv', index=False)
